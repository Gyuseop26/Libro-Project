# 📚도서관 내 자율주행 운반 시스템 Libro
<img width="900" height="600" alt="Libro Project README image" src="https://github.com/user-attachments/assets/7da2c73d-b3ed-487c-aa6c-2893bd400aaa" />

## 프로젝트 개요
+ 2019년 자료 기준 공공 도서관 1012곳 중 **사서 수가 3명 미만인 곳은 34.4%**
+ 업무량 증가 여부의 주된 항목은 **인력 부족 30.20%**/ **코로나 팬데믹으로 비대면 서비스 증가가 38.5%** 로 조사 됐습니다.
+ 도서관 수는 늘었지만 사서의 수가 감소하여 인력이 부족하고 펜데믹 이후 업무 강도는 올라가 도서관 운영의 어려움을 겪고 있다는 문제를 발견했습니다.
+ Libro 프로젝트는 도서관 사서의 반복 업무를 대신해 업무 부담을 줄이고 도서관 이용자에게는 편리를 제공합니다.

## 프로젝트 기간
> **2025. 04. 07 ~ 2025. 05. 30 (약 8주)**


## 기술 스택
| Category | Skills |
| :--- | :--- |
| **Environment** | Ubuntu 24.04, ROS 2(Jazzy), Arduino IDE |
| **Languages** | Python, C++, SQL, HTML |
| **Deep Learning** | YOLO 11 OBB, Paddle OCR |
| **DBMS / GUI** | PostgreSQL / PyQt |
| **Frontend / Backend** | React, TypeScript, Tailwind CSS / FastAPI, Node.js |
| **Collaboration** | Jira, Confluence, Git, Slack |

## SW Architecture
<p align="center">
  <img width="900" height="600" alt="Libro SW Architecture" src="https://github.com/user-attachments/assets/84e2c5b4-81a0-43e2-b687-bcd7e4b48f6f" />
</p>

## 주요 기능
+ #### 사용자 UI
  + **도서관 이용자** : 웹/앱으로 도서관 이용자가 희망하는 도서를 픽업 요청할 수 있습니다. 또한 도서가 픽업되는 과정을 확인할 수 있습니다.
  + **도서관 관리자(사서)** : 웹을 통해 도서 관리, 도서관 이용자 관리를 할 수 있습니다. PyQt 기반 로봇 관제 UI로 현재 로봇의 위치 확인, 로봇의 작업 상태 확인, 로봇 긴급 정지와 재시작, 로그 관리를 할 수 있습니다.

| ![Image 1](https://github.com/user-attachments/assets/4ff229b9-8387-4c3b-b8c4-da4db97f3a57) | ![Image 2](https://github.com/user-attachments/assets/c3108a44-6956-4d22-862b-159a1294da48) |
| :---: | :---: |
| **도서 검색** | **길 안내 요청** |
| ![Image 3](https://github.com/user-attachments/assets/1b2a4f77-16c5-4a2e-bafa-bc0206ac719a) | ![Image 4](https://github.com/user-attachments/assets/74b5cef4-e128-4b56-a5cb-bb6dc93093ec) |
| **픽업 트래킹** | **로봇 관제 UI** |


+ #### 도서 픽업(로봇팔)
  + 도서 픽업 명령이 들어오면 Libro(로봇팔)가 카메라로 도서의 중심 좌표와 ArucoMarker 값을 조합해 좌표 변환 기술을 통해 Pick and Place를 수행합니다.
  + 픽업이 완료된 도서는 이용자에게 배정된 픽업함에 책을 집어 넣습니다.

| ![Image 1](https://github.com/user-attachments/assets/fd89d1fc-4691-4307-9f1e-1198d9437dd1) | ![Image 2](https://github.com/user-attachments/assets/900cedad-5007-4aa9-b6a2-4261bf74fc3f) | ![Image 3](https://github.com/user-attachments/assets/0808921f-b06e-4efb-94c6-fdd72f91297d) |
| :---: | :---: | :---: |
| **도서 픽업** | **바구니에 넣기** | **픽업함에 넣기** |


+ #### 길 안내/ 이동(주행로봇)
  + 도서 픽업 명령이 들어오면 Libro(주행로봇)가 해당 도서가 있는 책장까지 이동합니다.
  + 로봇팔로부터 책을 바구니에 담았다는 완료 메시지가 전달 되면 이용자에게 배정된 픽업함까지 이동합니다.
  + 장애물이 나타났을 때 멈추고 장애물이 사라지면 다시 주행합니다.
  + 이용자가 도서관 내 장소까지 안내 요청을 하면 가이드 작업을 수행합니다.
  + 충전이 필요하거나 작업이 완료되면 복귀합니다. 

| ![Image 1](https://github.com/user-attachments/assets/9f6f62a8-fa90-4646-90ca-439b029b360e) | ![Image 2](https://github.com/user-attachments/assets/e1e373ab-06a3-4163-aa57-23d1a48dee7a) |
| :---: | :---: |
| **Marker based Odom** | **길 안내** |
| ![Image 3](https://github.com/user-attachments/assets/ca9f8694-b267-4e6b-9d2c-8d99f4695250) | ![Image 4](https://github.com/user-attachments/assets/c638f8ad-83b3-460b-9832-1091461c2033) |
| **비상 정지** | **장애물 회피** |

---

## 시나리오
> ### 도서 픽업 시나리오
<p align="center">
  <img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/d6e6ad6e-ee7a-4c9f-b213-421ee1af9802" />
</p>

> ### 길 안내 요청
<p align="center">
  <img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/266e279c-f688-4baf-840d-e47a92870e28" />
</p>

## 세부 기능
> ### **도서 픽업**
* YOLO 11 OBB를 이용해 객체 인식 진행
* Paddle OCR로 책 제목 추출
* Googel Books API를 활용해 추출된 책 제목 보정
* Book Recognition을 통해 ArucoMarker Z값 추출, 책 좌표 추출
  + 2D 카메라로 한정된 상황에서 깊이 값을 인식하기 위해 ArucoMarker 사용
* Libro Task Manager로 책 좌표 전달 후 ROS 통신으로 좌표와 픽업 명령
* 카메라-로봇팔 좌표 변환을 거쳐 도서 픽업

> ### **Navigation**
* Marker 기반 Visual Odometry **Localization**
  * Encoder의 부재를 해결하기 위해 ArUco Marker를 사용한 Odom TF 발행
* A* 기반 Planner **Path Planning**
* PID Controller **Path Following**


## 개발자 소개 및 담당
| 역할 | 이름 |
| :--- | :--- |
| **팀장** | 임소희 |
| **책 인식** | 김명서, 이의준, 임소희 |
| **로봇팔 제어** | 정규섭, 임소희 |
| **Localization** | 임소희, 백은기 |
| **Path Planning** | 김명서, 이지은 |
| **Path Following** | 이지은, 김명서 |
| **장애물 회피** | 이지은, 백은기 |
| **로봇 관제 UI** | 정규섭, 이의준 |
| **통합 제어** | 이종호 |
| **도서관 WebAPP FastAPI 서버 데이터베이스** | 한지선 |


