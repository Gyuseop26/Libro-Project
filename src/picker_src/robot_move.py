import time
#from pymycobot.mycobot import MyCobot
# ----- 로봇 연결 -----
from packaging import version
import pymycobot
if version.parse(pymycobot.__version__) >= version.parse("3.6.0"):
    from pymycobot import MyCobot280 as MyCobot
else:
    from pymycobot import MyCobot

from pose_config import basket1, basket2, pickup1, pickup2, place_home, basket_home


class RobotController:
    def __init__(self, port='/dev/ttyJETCOBOT', baud=1000000, logger= None):
        self.mc = MyCobot(port, baud)
        self.init_pos = [0, 90, -90, 0, 0, -45]
        self.logger = logger

    def move_to_initial(self):
        self.logger.info("초기 자세로 이동합니다.")
        self.mc.send_angles(self.init_pos, 30)
        self.mc.set_gripper_value(100, 50)
        time.sleep(1)
        self.logger.info("초기 자세 이동 완료.")

    def change_gripper_angle(self, book_angle): #책의 기울기를 입력 받으면 현재 좌표에서 그리퍼만 회전
        change_gripper = book_angle - 135 #책의 기울기를 받아서 현재 그리퍼 각도를 수정

        self.mc.send_angle(6, change_gripper, 50)
        current_coords = self.mc.get_coords()
    
        print(f"현재 좌표{current_coords}")
        rx, ry, rz = current_coords[3:6] # 현재 로봇 좌표에서 회전값만 추출해서 rx, ry, rz에 저장
        print("회전값 rx, ry, rz:", rx, ry, rz)
    
        return rx, ry, rz
    
    def is_within_range(self, coord):
        min_vals = [-281.45, -281.45, -70, -180, -180, -180]
        max_vals = [300.0,  281.45, 420.0, 180, 180, 180]
        
        for i in range(6):
            if not (min_vals[i] <= coord[i] <= max_vals[i]):
                return False
        return True
    
    # 책장에서 책 집기
    def move_and_grab(self, tcp_coords, book_angle, rx=-92, ry=-45, rz=-93):
        move_coords = tcp_coords.tolist() + [rx, ry, rz]
        move_coords[1] -= 3
        # move_coords[0] +=10 # 테스트 보정 좌표
        # move_coords[2] +=10 # 테스트 보정 좌표
        
        if not self.is_within_range(move_coords):
            self.logger.info("작동 범위를 초과했습니다.")
            return

        self.logger.info(f"물체를 집으러 이동 중 {move_coords}")
        
        # 잡기 전에 앞에가서 멈추기위한 waypoint
        foward_coords = move_coords.copy()
        foward_coords[0] -= 30

        # 책 앞까지 가서 그리퍼 회전
        forward_coords_angle = foward_coords.copy()

        # 동작 시작
        self.mc.send_coords(foward_coords, 20)
        time.sleep(2)

        # 책에 기울기만큼 그리퍼 회전
        self.logger.info(f"그리퍼를 {book_angle}만큼 회전합니다.")
        
        forward_coords_angle[3:6] = self.change_gripper_angle(book_angle)
        print("forward_coords_angle: ",forward_coords_angle)
        time.sleep(1)
        
        # 회전한 상태로 목표 좌표로 이동
        # forward_coords_angle[0] += 25
        forward_coords_angle[0] += 47
        print("f_coords_angle",forward_coords_angle)
        self.mc.send_coords(forward_coords_angle, 20)
        time.sleep(1)

        # 그리퍼 머리 세우기
        self.mc.send_angle(4, 75, 20)
        time.sleep(2)

        # 그리퍼 닫기
        self.logger.info("그리퍼를 닫기")
        self.mc.set_gripper_value(0, 50)
        time.sleep(1)
        
        # 책 세우기
        self.mc.send_coords(move_coords, 20)
        time.sleep(1)

        #집은 상태에서 뒤로 빠지기
        foward_coords = move_coords.copy()
        foward_coords[2] += 10
        self.mc.send_coords(foward_coords,20)
        time.sleep(1)
        
        # 목표 좌표 앞으로 살짝 빼기
        foward_coords[0] -= 30 # 책을 집는다고 가정하면 지금 크기보다 더 빠져야 됨.
        self.mc.send_coords(foward_coords,20)
        time.sleep(1)
        
        # 초기 자세로 돌아오기
        self.mc.send_angles(self.init_pos, 30)
        time.sleep(1)
        self.logger.info("물체를 집고 시작 위치로 돌아왔습니다.")

    # 바구니에 책 담기
    def place_book(self, basket_id):
        # 바구니 초기 자세로
        self.mc.send_angles(basket_home, 50)
        time.sleep(1)
        
        if basket_id == 'B1':
            self.logger.info("바구니 1에 책을 담습니다.")

            self.mc.send_coords(basket1["up"], 50)
            time.sleep(1)

            self.mc.send_coords(basket1["middle"], 30)
            time.sleep(1)

            self.mc.send_coords(basket1["middle2"], 20)
            time.sleep(1)

            self.mc.send_coords(basket1["down"], 10)
            time.sleep(1)

            # 바구니 1에 내려놓기
            self.mc.set_gripper_value(100, 50)
            time.sleep(1)

            self.mc.send_coords(basket1["middle"], 20)
            time.sleep(1)

            self.mc.send_coords(basket1["up"], 50)
            time.sleep(1)

        elif basket_id == 'B2':
            self.logger.info("바구니 2에 책을 담습합니다.")

            self.mc.send_coords(basket2["up"], 50)
            time.sleep(1)

            self.mc.send_coords(basket2["middle"], 30)
            time.sleep(1)

            self.mc.send_coords(basket2["middle2"], 20)
            time.sleep(1)

            self.mc.send_coords(basket2["down"], 10)
            time.sleep(1)

            # 바구니 2에 내려놓기
            self.mc.set_gripper_value(100, 50)
            time.sleep(1)

            self.mc.send_coords(basket2["middle"], 20)
            time.sleep(1)

            self.mc.send_coords(basket2["up"], 50)
            time.sleep(1)
        
        else:
            self.get_logger().warn(f"잘못된 바구니 ID: {basket_id}")
            return
        
        # 바구니 초기 자세로 돌아오기
        self.mc.send_angles(basket_home, 50)
        time.sleep(1)

        # 초기 자세로 돌아오기
        self.mc.send_angles(self.init_pos, 30)
        self.logger.info("책을 바구니에 담았습니다.")

    # 바구니에서 픽업함으로 책 넣기
    def place_cabinet(self, cabinet_id, basket_id):
        self.logger.info(f"[바구니 → 픽업함] {basket_id} → {cabinet_id} 책 이동 시작")

        # 바구니 초기 자세로
        self.mc.send_angles(basket_home, 50)
        time.sleep(1)

        # 첫 번째 해당하는 바구니 위로 이동
        if basket_id == "B1":
            self.mc.send_coords(basket1["up"], 50)
            time.sleep(1)

            self.mc.send_coords(basket1["middle"], 30)
            time.sleep(1)

            self.mc.send_coords(basket1["middle2"], 20)
            time.sleep(1)

            self.mc.send_coords(basket1["down"], 10)
            time.sleep(1)

            self.mc.send_coords(basket1["down2"], 10)
            time.sleep(1)

            # 내려가서 책 잡기
            self.mc.set_gripper_value(0, 50)
            time.sleep(1)

            self.mc.send_coords(basket1["middle2"], 20)
            time.sleep(1)

            self.mc.send_coords(basket1["middle"], 30)
            time.sleep(1)

            self.mc.send_coords(basket1["up"], 50)
            time.sleep(1)
        
        elif basket_id == "B2":

            self.mc.send_coords(basket2["up"], 50)
            time.sleep(1)

            self.mc.send_coords(basket2["middle"], 30)
            time.sleep(1)

            self.mc.send_coords(basket2["middle2"], 20)
            time.sleep(1)

            self.mc.send_coords(basket2["down"], 10)
            time.sleep(1)

            self.mc.send_coords(basket2["down2"], 10)
            time.sleep(1)

            # 내려가서 책 잡기
            self.mc.set_gripper_value(0, 50)
            time.sleep(1)

            self.mc.send_coords(basket2["middle2"], 20)
            time.sleep(1)

            self.mc.send_coords(basket2["middle"], 30)
            time.sleep(1)

            self.mc.send_coords(basket2["up"], 50)
            time.sleep(1)

        else:
            self.logger.warn(f"잘못된 바구니 ID: {basket_id}")
            return
        
        # 바구니 자세로 돌아오기
        self.mc.send_angles(basket_home, 50)
        time.sleep(1)
        self.logger.info("책을 바구니에서 꺼냈습니다.")
        self.mc.send_angle(6, -45, 30)
        time.sleep(1)

        # 초기 자세로 돌아오기
        self.mc.send_angles(self.init_pos, 30)
        time.sleep(1)

        # 픽업함 자세로 이동
        self.mc.send_angles(place_home, 30)
        time.sleep(1)
        self.logger.info("픽업함 앞으로 이동")

        if cabinet_id == "P1":

            self.mc.send_angles(pickup1["before"],30)
            time.sleep(3)

            self.mc.send_angles(pickup1["p1"], 15)
            time.sleep(3)

            self.mc.set_gripper_value(100, 50)
            time.sleep(3)

            self.mc.send_coords(pickup1["push"], 20)
            time.sleep(3)
            
            # 밀어 넣기 전에 그리퍼 회전
            self.mc.send_angle(6, -45, 50)
            time.sleep(3)

            self.mc.send_angles(pickup1["pushing"], 15)
            time.sleep(3)

            # 픽업함에 담기 끝
            self.mc.send_angles(place_home, 50)
            time.sleep(3)
            self.mc.send_angle(6, -45, 50)
        
        elif cabinet_id == "P2":

            self.mc.send_angles(pickup2["before"],30)
            time.sleep(3)

            self.mc.send_angles(pickup2["p2"], 15)
            time.sleep(3)

            self.mc.set_gripper_value(100, 50)
            time.sleep(3)

            self.mc.send_angles(pickup2["push"], 30)
            time.sleep(3)

            # 밀어 넣기 전에 그리퍼 회전
            self.mc.send_angle(6, -45, 50)
            time.sleep(3)

            self.mc.send_angles(pickup2["pushing"], 15)
            time.sleep(3)

            self.mc.send_angles(pickup2["push_done"], 15)
            time.sleep(3)

            # 픽업함에 담기 끝
            self.mc.send_angles(place_home, 50)
            self.mc.send_angle(6, -45, 50)

        else :
            self.logger.warn(f"잘못된 픽업함 ID: {cabinet_id}")
            return
        
        # 픽업 완료
        self.mc.send_angles(self.init_pos, 30)
        self.logger.info("책 픽업 완료. 초기 자세로 복귀함.")