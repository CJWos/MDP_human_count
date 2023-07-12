import RPi.GPIO as GPIO
import time
import cv2
import socket

# GPIO 핀 번호 설정
coil_A_1_pin = 12
coil_A_2_pin = 21
coil_B_1_pin = 16
coil_B_2_pin = 20  

# GPIO 핀 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

# 스텝 및 방향 제어 함수
def set_step(w1, w2, w3, w4):
    GPIO.output(coil_A_1_pin, w1)
    GPIO.output(coil_A_2_pin, w2)
    GPIO.output(coil_B_1_pin, w3)
    GPIO.output(coil_B_2_pin, w4)

# 스텝 모터 회전 함수
def step(delay, steps, clockwise=True):
    # 시계 방향 또는 반시계 방향 스텝 패턴 정의
    if clockwise:
        step_sequence = [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1]
        ]
    else:
        step_sequence = [
            [1, 0, 0, 1],
            [0, 0, 0, 1],
            [0, 0, 1, 1],
            [0, 0, 1, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [1, 0, 0, 0]
        ]

    # 스텝 수행
    for _ in range(steps):
        for step in step_sequence:
            set_step(step[0], step[1], step[2], step[3])
            time.sleep(delay)

# 소켓 설정
HOST = "10.137.208.228"  # 안드로이드 디바이스의 IP 주소로 변경해야 합니다.
PORT = 8001
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')
s.bind((HOST, PORT))
print('Socket bind complete')
s.listen(1)
print('Socket now listening')

# 물체 감지를 위한 설정
prototxt = '/home/mdp1/Desktop/human_count-main/pot/MobileNetSSD_deploy.prototxt'
model = '/home/mdp1/Desktop/human_count-main/pot/MobileNetSSD_deploy.caffemodel'
min_confidence = 0.5

# 클래스 레이블
class_labels = [
    'background', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
    'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
    'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse',
    'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
    'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
    'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
    'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass',
    'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
    'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
    'hair drier', 'toothbrush'
]

# 원하는 물체의 클래스 레이블
target_label = 'bird'

# 모델 로드
net = cv2.dnn.readNetFromCaffe(prototxt, model)

# 비디오 캡처 객체 생성
cap = cv2.VideoCapture(0)

while True:
    # 비디오 프레임 읽기
    ret, frame = cap.read()

    if not ret:
        break

    # 입력 프레임 크기 가져오기
    height, width = frame.shape[:2]

    # 이미지 전처리를 위해 Blob 생성
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

    # Blob을 모델에 입력
    net.setInput(blob)

    # 물체 감지 수행
    detections = net.forward()

    # 개체 개수 초기화
    object_count = 0

    # 감지된 물체에 대한 후속 처리
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        # 신뢰도가 최소 신뢰도보다 큰 경우에만 처리
        if confidence > min_confidence:
            class_id = int(detections[0, 0, i, 1])
            class_label = class_labels[class_id]

            # 원하는 물체에 해당하는 경우에만 처리
            if class_label == target_label:
                # 감지된 물체의 경계 상자 좌표 계산
                x_left_bottom = int(detections[0, 0, i, 3] * width)
                y_left_bottom = int(detections[0, 0, i, 4] * height)
                x_right_top = int(detections[0, 0, i, 5] * width)
                y_right_top = int(detections[0, 0, i, 6] * height)

                # 경계 상자 및 클래스 레이블 그리기
                cv2.rectangle(frame, (x_left_bottom, y_left_bottom), (x_right_top, y_right_top), (0, 255, 0), 2)
                label = f"{class_label}: {confidence:.2f}"
                cv2.putText(frame, label, (x_left_bottom, y_left_bottom - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 2)

                # 개체 개수 증가
                object_count += 1

    # 개체 개수 출력
    print("Detected objects:", object_count)

    # 개수에 따른 상태 출력
    if 0 <= object_count <= 2:
        status = "쾌적"
    elif 3 <= object_count <= 5:
        status = "평범"
    elif 6 <= object_count <= 8:
        status = "포화"
    else:
        status = "알 수 없음"

    print("Status:", status)

    # 결과 영상 출력
    cv2.imshow('Object Detection', frame)

    # 개체 수 인식 상태가 평범 이상이면 스텝모터 코드 실행
    if status != "쾌적":
        step(0.01, 30, clockwise=True)
        time.sleep(1)
        step(0.01, 30, clockwise=False)
        time.sleep(1)

    # 소켓 통신을 위한 접속 승인
    print("Waiting for connection...")
    conn, addr = s.accept()
    print("Connected by", addr)

    # 개수에 따른 상태를 클라이언트에 전송
    data = status.encode("utf-8")
    conn.sendall(data)

    # 연결 닫기
    conn.close()

    # 종료 조건 설정
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

s.close()
cap.release()
cv2.destroyAllWindows()


