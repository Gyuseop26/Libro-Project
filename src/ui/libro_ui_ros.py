import json
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, PoseStamped
from std_msgs.msg import String
from PyQt5.QtCore import QThread, pyqtSignal

class LibroPoseSub(Node):
    def __init__(self, 
                 libro1_pose, libro2_pose, libro3_pose,
                 libro1_state, libro2_state, libro3_state,
                 libro1_error, libro2_error, libro3_error, 
                 
        ):
        super().__init__('libro_topic_subscriber') # 노드 이름이 libro_pose_subscriber
        # 로봇 위치 정보
        self.libro1_pose_signal = libro1_pose
        self.libro2_pose_signal = libro2_pose
        self.libro3_pose_signal = libro3_pose

        # 로봇 작업상태 정보
        self.libro1_state_signal = libro1_state
        self.libro2_state_signal = libro2_state
        self.libro3_state_signal = libro3_state

        # 로봇 에러 정보
        self.libro1_error_signal = libro1_error
        self.libro2_error_signal = libro2_error
        self.libro3_error_signal = libro3_error

        # 각각의 libro들의 pose 토픽을 받을 서브스크라이브 생성, 데이터를 받으면 콜백 함수 실행.
        self.libro1_pose_sub = self.create_subscription(PoseStamped, '/aruco1/map/pose', self.libro1_pose_callback, 10)
        self.libro2_pose_sub = self.create_subscription(PoseStamped, '/aruco2/map/pose', self.libro2_pose_callback, 10)
        self.libro3_pose_sub = self.create_subscription(PoseStamped, '/aruco3/map/pose', self.libro3_pose_callback, 10)

        # 각각의 libro들의 state 토픽을 받을 서브스크라이브 생성, 데이터를 받으면 콜백 함수 실행.
        self.libro_state_sub = self.create_subscription(String, '/libro_robot_states', self.robot_states_callback, 10)

        # 각각의 libro들의 error 토픽을 받을 서브스크라이브 생성, 데이터를 받으면 콜백 함수 실행.



    # 각각의 libro들의 pose 메시지를 수신했을 때 실행되는 콜백 함수.
    def libro1_pose_callback(self, msg):
        x = msg.pose.position.x
        y = msg.pose.position.y
        self.libro1_pose_signal.emit(1, x, y) # signal을 발생할 때 로봇 id도 같이 발생
        # libro_pose_signal이라는 시그널을 emit(발생시킨다.)
        # libro1_pose_signal은 방송 채널, 즉 libro1_pose_received 시그널을 발생.

    def libro2_pose_callback(self, msg):
        x = msg.pose.position.x
        y = msg.pose.position.y
        self.libro2_pose_signal.emit(2, x, y)

    def libro3_pose_callback(self, msg):
        x = msg.pose.position.x
        y = msg.pose.position.y
        self.libro3_pose_signal.emit(3, x, y)

    # 각각의 libro의 상태를 담은 json 형태의 토픽을 받았을 때 실행되는 콜백 함수.
    def robot_states_callback(self, msg):
        try:
            states = json.loads(msg.data)  # json 형식의 문자열을 파싱해서 파이썬 딕셔너리 형태로 변환하는 함수.
            if "libro1" in states:
                self.libro1_state_signal.emit(1, states["libro1"])
            
            if "libro2" in states:
                self.libro2_state_signal.emit(2, states["libro2"])
            
            if "libro3" in states:
                self.libro3_state_signal.emit(3, states["libro3"])
        
        except Exception as e:
            print(f" ROS Topic 파싱 에러: {e}")

class RosTopicInfo(QThread):
    # 각 로봇의 pose 정보를 PyQT로 전달할 시그널 선언.
    # 이 시그널들은  정보를 PyQT 메인 스레드로 전달할 수 있음.
    # 콜백 함수에 libro_pose_signal과 같은 내용을 담은 변수라고 보면 됨.
    # 다만, 역할이 다르다. ROS 노드 클래스 안에서 signal은 방송을 하는 놈이고, QThread 안에 있는 놈은 방송을 받는 놈.
    # main_ui 파일에서 오브젝트들과 연결될 녀석은 QTread 안에 있는 received가 된다.
    
    libro1_pose_received = pyqtSignal(int, float, float) # robot_id를 int, x, y 좌표를 float 형태로 보냄.
    libro2_pose_received = pyqtSignal(int, float, float)
    libro3_pose_received = pyqtSignal(int, float, float)

    libro1_state_received = pyqtSignal(int, str) # robot_id를 int, 로봇의 작업 상태를 str 형태로 보냄.
    libro2_state_received = pyqtSignal(int, str)
    libro3_state_received = pyqtSignal(int, str)

    libro1_error_received = pyqtSignal(int, str) # robot_id를 int, 로봇의 에러 상태를 str 형태로 보냄.
    libro2_error_received = pyqtSignal(int, str)
    libro3_error_received = pyqtSignal(int, str)    

    def __init__(self):
        super().__init__()

    def run(self):
        # rclpy.init()은 여러 번 호출되면 안되니까, 예외처리 추가.
        try:
            rclpy.init()
        except RuntimeError:
            pass
        
        # 노드를 생성하여, 시그널 객체들을 전달
        self.node = LibroPoseSub(
            self.libro1_pose_received, self.libro2_pose_received, self.libro3_pose_received,
            self.libro1_state_received, self.libro2_state_received, self.libro3_state_received,
            self.libro1_error_received, self.libro2_error_received, self.libro3_error_received
        )
        
        rclpy.spin(self.node)
        self.node.destroy_node()
        rclpy.shutdown()
