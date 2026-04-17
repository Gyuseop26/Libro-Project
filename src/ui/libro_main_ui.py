import os, sys, math, threading, copy
import time
import requests
import bcrypt # 서버에 있는 비밀번호는 암호화 되어있어서 해석하려면 이 모듈을 써야 함


from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPoint, QSettings, QRegExp
from PyQt5.QtGui import QPainter, QPen, QColor, QRegExpValidator
from PyQt5.QtGui import QMovie
from PyQt5 import uic

from libro_ui_ros import RosTopicInfo

# UI 파일 연결
main_ui = uic.loadUiType("Libro_main_ui.ui")[0]

# 로그인 정보
ID = "admin"
PASSWORD = "1234"

## 화면을 띄우는데 사용되는 Class 선언
class LibroAdmin(QMainWindow, main_ui): 
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Libro Admin")
        
        # 타이머 선언
        self.timer = QTimer()

        # 초기 화면은 로그인 페이지 (index 0)
        self.stackedWidget.setCurrentIndex(0)

        # ROS Thread 연결
        self.ros_topic = RosTopicInfo()
        
        self.ros_topic.libro1_pose_received.connect(self.current_area_update)
        self.ros_topic.libro2_pose_received.connect(self.current_area_update)
        self.ros_topic.libro3_pose_received.connect(self.current_area_update)

        self.ros_topic.libro1_state_received.connect(self.robot_state_update)
        self.ros_topic.libro2_state_received.connect(self.robot_state_update)
        self.ros_topic.libro3_state_received.connect(self.robot_state_update)
        
        self.ros_topic.start()
        

        # 로그인 버튼 클릭과 로그인 함수 연결
        self.login_btn.clicked.connect(self.check_login)
        # 비밀번호 입력창에서 엔터로 로그인
        self.lineEdit_password.returnPressed.connect(self.login_btn.click)
        
        # 로그인 성공한 아이디 저장 기능 
        settings = QSettings("fourfour", "LibroAdmin") # QSettings의 파일 저장 방식
        saved_id = settings.value("saved_id", "") #저장된 아이디를 불러오고, 없다면 공백으로 채움
        self.lineEdit_id.setText(saved_id)

        # 저장된 ID가 있다면 체크박스를 체크상태로 둔다.
        if saved_id:
            self.id_save_check_btn.setChecked(True)

        # tab2: robot_activate_sw 상태 정의
        self.libro1_activate_sw.setChecked(True)
        self.libro2_activate_sw.setChecked(True)
        self.libro3_activate_sw.setChecked(True)

        # 맵 위에 그릴 로봇 좌표 저장 공간, 초기 위치 설정
        self.robot_positions = {
                1: (1010, 20),
                2: (1010, 30),
                3: (1010, 40)
            }
        
        # 퍼블리시 해서 들어오는 로봇의 실제 좌표값을 따라가지 못할까봐, 주기적으로 호출해서 그림
        self.timer.timeout.connect(self.draw_robot_position)
        self.timer.start(33) #33ms 약 30fps

        if self.map_image_lb.pixmap() is not None:
            self.map_image_origin = self.map_image_lb.pixmap().copy()
        else:
            self.map_image_origin = None
        
        self.draw_robot_position() # 시작할 때 한 번은 그려지게 초기 선언
        

    # # 로그인 확인 - (서버 연결용)
    # def check_login(self):
    #     user_id = self.lineEdit_id.text()
    #     user_pw = self.lineEdit_password.text()
        
    #     if len(user_pw) < 4:
    #         self.login_fail_label.setText("비밀번호는 4자리 이상 입력해주세요.")
    #         self.lineEdit_password.clear()
    #         return

    #     try:
    #         # 서버에서 사용자 리스트 가져오기
    #         login_response = requests.get("http://192.168.0.138:8000/users", timeout= 3) # 서버 미응답 시간 5초로 제한
    #         input_login = login_response.json()

    #         matched_user = None

    #         for u in input_login:
    #             if u["email"] == user_id and u["role"] == "admin": # 관리자만 로그인 할 수 있도록 제한
    #                 matched_user = u
    #                 break  # 첫 번째 일치하는 사용자만 찾으면 끝냄
            
    #         if matched_user:
    #             hashed_pw = matched_user["password"].encode("utf-8")
    #             input_pw = user_pw.encode("utf-8")

    #             # bcrypt로 암호화 된 비밀번호 확인
    #             if bcrypt.checkpw(input_pw, hashed_pw):
                    
    #                 settings = QSettings("fourfour", "LibroAdmin")
    #                 # 체크박스가 눌린 채로 로그인을 성공하게 되면 아이디 저장
    #                 if self.id_save_check_btn.isChecked():
    #                     settings.setValue("saved_id", user_id)
    #                 else:
    #                     settings.remove("saved_id")
        
    #                 self.login_fail_label.setText("")
    #                 self.stackedWidget.setCurrentIndex(1)  # 관리자 페이지로 전환
    #                 return

    #         # 로그인 실패 처리/ 입력창 초기화
    #         self.login_fail_label.setText("아이디 또는 비밀번호가 올바르지 않습니다.")
    #         self.lineEdit_password.clear()
    #         self.lineEdit_id.clear()

    #     except Exception as e:
    #         print("서버 오류:", e)
    #         self.login_fail_label.setText("서버 연결 실패")


    # 로그인 확인 - 아이디 & 비번 코드에서 저장해서 씀.
    def check_login(self):
        user_id = self.lineEdit_id.text()
        user_pw = self.lineEdit_password.text()

        if user_id == ID and user_pw == PASSWORD:

            settings = QSettings("fourfour", "LibroAdmin")
            # 체크박스가 눌린 채로 로그인을 성공하게 되면 아이디 저장
            if self.id_save_check_btn.isChecked():
                settings.setValue("saved_id", user_id)
            else:
                settings.remove("saved_id")

            self.login_fail_label.setText("") 
            self.stackedWidget.setCurrentIndex(1)  # 관리자 페이지로 전환
        
        elif len(user_pw) < 4:
            self.login_fail_label.setText("비밀번호는 4자리 이상 입력해주세요.")
            self.lineEdit_password.clear()

        else:
            self.login_fail_label.setText("아이디 또는 비밀번호를 확인해주세요")
            # 아이디와 비밀번호 입력창 초기화
            self.lineEdit_id.clear()
            self.lineEdit_password.clear()

    # 실제 로봇이 받는 좌표와 PyQT 맵에서 표현하는 좌표 위치가 달라서 변환 과정을 해주는 함수.
    def robot_to_pyqt_coords(self, x, y):
        img_width = 960 # 이미지 크기
        img_height = 485
        margin = 5      # 테두리를 구성하는 픽셀 크기
        draw_width = img_width - 2 * margin   # PyQT 맵 이미지에서 표현할 범위 950
        draw_height = img_height - 2 * margin # PyQT 맵 이미지에서 표현할 범위 475
        
        # x축 변환/ 로봇은 최대 2, PyQT 이미지에서는 최대 950, 테두리 5px
        img_x = int(margin + (x / 2) * draw_width)
        # y축 변환/ 로봇은 최대 1, PyQT 이미지에서는 최대 475
        img_y = int(margin + ((1 - y) / 1) * draw_height)
        
        return img_x, img_y +20
    

    # 로봇 실시간 좌표로 위치 업데이트
    def current_area_update(self, robot_id, x, y):
        # print(f"robot_id= {robot_id}, x= {x}, y= {y}") # 로봇 좌표 흔들려서 추가한 코드

        if robot_id == 1:
            x = round(x, 2)
            y = round(y, 2)
            self.libro1_area_lb.setText(f"X: {x}, Y: {y}")
        
        elif robot_id == 2:
            x = round(x, 2)
            y = round(y, 2)
            self.libro2_area_lb.setText(f"X: {x}, Y: {y}")
        
        elif robot_id == 3:
            x = round(x, 2)
            y = round(y, 2)
            self.libro3_area_lb.setText(f"X: {x}, Y: {y}")

        # 좌표 값을 받아서 그림 그릴 저장소에 업데이트
        self.robot_positions[robot_id] = (self.robot_to_pyqt_coords(x, y))

        self.draw_robot_position() #좌표가 토픽으로 들어오면 그리기 함수 실행


    # 맵 위에 픽셀로 로봇 현재 위치 표시
    def draw_robot_position(self):
        # 이미지가 없으면 그림을 그리지 않겠다.
        if self.map_image_origin is None:
            return
        
        # 현재 map_image가 바뀌지 않게 복사해서 사용. 항상 원본에 복사
        pixmap = self.map_image_origin.copy()
        
        painter = QPainter(pixmap)
        color_map = {1: 'blue', 2: 'red', 3: 'green'}
        radius = 25 #그려지는 픽셀 원 반지름
        
        # 로봇 좌표 저장소에서 꺼내서 for문을 돌림.
        for robot_id, (x, y) in self.robot_positions.items():
            pen = QPen(QColor(color_map.get(robot_id, 'yellow')))
            pen.setWidth(1) # 그려지는 원 테두리 두께
            painter.setPen(pen)
            painter.setBrush(QColor(color_map.get(robot_id, 'yellow'))) # 원 내부 색상
            
            # 중심이 (x, y)이고 지름이 2*radius인 원을 그림
            painter.drawEllipse(int(x) - radius, int(y) - radius, 2*radius, 2*radius)
        
        painter.end()
        
        self.map_image_lb.setPixmap(pixmap)


    # state가 영어로 들어오니까 gui에 업데이트 되는 것은 한글로 변경하고 싶음.
    def translate_state(self, state):
        mapping = {
            'charging': '충전중',
            'waiting': '대기중',
            'pickup': '픽업중',
            'nav': '길 안내중'
        }
        return mapping.get(state, state)

    # 로봇의 상태를 실시간으로 업데이트.
    def robot_state_update(self, robot_id, state):
        robot_state = self.translate_state(state)
        if robot_id == 1:
            self.libro1_state_lb.setText(robot_state)
        
        elif robot_id == 2:
            self.libro2_state_lb.setText(robot_state)
        
        elif robot_id == 3:
            self.libro3_state_lb.setText(robot_state)


    

if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    
    # Window Class의 인스턴스 생성
    window = LibroAdmin()
    
    # 프로그램 화면을 보여주는 코드
    window.show()
    
    # 프로그램을 이벤트 루프로 진입시키는(프로그램을 작동 시키는) 코드
    sys.exit(app.exec())
