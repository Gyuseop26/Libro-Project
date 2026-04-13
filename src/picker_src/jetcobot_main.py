import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from std_msgs.msg import Float32MultiArray, Bool, String

import numpy as np
from robot_move import RobotController
from cam_transform import transform_camera_to_tcp

class RobotExecutor(Node):
    def __init__(self):
        super().__init__('robot_executor')
        self.subscription = self.create_subscription(
            Float32MultiArray,
            'libro1/pick_book',
            self.move_book,
            10
        )

        self.place_basket_subscription = self.create_subscription(
            String,
            'libro1/place_basket',
            self.place_to_basket,
            10
        )

        self.place_cabinet_subscription = self.create_subscription(
            String,
            'libro1/place_cabinet',
            self.place_to_cabinet,
            10
        )
        
        self.pick_book_done_publisher = self.create_publisher(
            Bool, 
            'libro1/pick_info', 
            10
        )

        self.place_book_done_publisher = self.create_publisher(
            Bool, 
            'libro1/place_info', 
            10
        )
        
        self.controller = RobotController(logger=self.get_logger())
        self.controller.move_to_initial()

    # 책장에서 책 꺼내는 함수 실행
    def move_book(self, msg):
        # 넘겨 받는 데이터 갯수 확인
        if len(msg.data) < 4:
            self.get_logger().warn("좌표 데이터 갯수를 확인해주세요.")
            return
        
        x, y, z, angle = msg.data
        self.get_logger().info(f"받은 좌표: x={x}, y={y}, z={z}, angle={angle}")

        cam_coords = np.array([x, y, z])
        
        tcp_coords = transform_camera_to_tcp(cam_coords)
        book_angle = angle
        self.get_logger().info(f"TCP 좌표: {tcp_coords}, 기울기: {book_angle}")
        
        # 로봇 동작 함수 실행
        self.controller.move_and_grab(tcp_coords, book_angle)
        self.get_logger().info("책 꺼내기 동작 완료")

        # 동작이 끝났으니 완료 응답 퍼블리시
        done_msg = Bool()
        done_msg.data = True
        self.pick_book_done_publisher.publish(done_msg)
        self.get_logger().info("완료 메시지를 보냈음.")

    # 바구니에 담는 동작 실행 함수
    def place_to_basket(self, msg):
        basket_id = msg.data.strip().upper()

        # 바구니 ID가 제대로 들어왔는지 확인
        valid_ids = ['B1', 'B2']
        if basket_id not in valid_ids:
            self.get_logger().warn(f"잘못된 바구니 ID 수신됨: {basket_id}")
            return
        
        self.get_logger().info(f"바구니 명령 수신: {basket_id}")

        # 로봇 동작 함수 실행
        self.controller.place_book(basket_id)
        self.get_logger().info("책 바구니에 담기 완료")

        # 동작이 끝났으니 완료 응답 퍼블리시
        done_msg = Bool()
        done_msg.data = True
        self.place_book_done_publisher.publish(done_msg)
        self.get_logger().info("바구니 담기 완료 메시지를 보냈음.")

    # 바구니에서 픽업함에 책 넣는 함수 실행
    def place_to_cabinet(self, msg):
        topic_data = msg.data.strip()
        parts = [p.strip().upper() for p in topic_data.split(',')]

        if len(parts) != 5:
            self.get_logger().warn(f"잘못된 메시지 형식: {parts}")
            return
        
        _, place_pickup1, place_pickup2, place_basket1, place_basket2 = parts

        # 들어오는 토픽 순서에 따라 동작 실행
        if place_pickup1 and place_basket1:
            self.get_logger().info(f"첫 번째 픽업 {place_basket1} → {place_pickup1}")
            self.controller.place_cabinet(place_pickup1, place_basket1)

        if place_pickup2 and place_basket2:
            self.get_logger().info(f"두 번째 픽업 {place_basket2} → {place_pickup2}")
            self.controller.place_cabinet(place_pickup2, place_basket2)

        # 동작이 끝났으니 완료 응답 퍼블리시
        done_msg = Bool()
        done_msg.data = True
        self.place_book_done_publisher.publish(done_msg)
        self.get_logger().info("픽업 완료 메시지를 보냈음.")

        # # 노드 종료
        # self.get_logger().info("모든 책 픽업 완료. 노드를 종료합니다.")
        # rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = RobotExecutor()
    rclpy.spin(node)
    node.destroy_node()

if __name__ == '__main__':
    main()
