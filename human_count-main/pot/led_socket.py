import socket
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)  # GPIO 18을 출력으로 설정합니다.

HOST = "10.153.153.69"
PORT = 8002

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')
s.bind((HOST, PORT))
print('Socket bind complete')
s.listen(1)
print('Socket now listening')

def do_some_stuffs_with_input(input_string):
    if input_string == "TURN_ON":
        GPIO.output(18, GPIO.HIGH)  # LED를 켭니다.
        return "LED를 켰습니다."
    elif input_string == "TURN_OFF":
        GPIO.output(18, GPIO.LOW)  # LED를 끕니다.
        return "LED를 껐습니다."
    else:
        return "잘못된 명령어입니다."

while True:
    conn, addr = s.accept()
    print("Connected by", addr)

    data = conn.recv(1024)
    if not data:
        break

    data = data.decode("utf8").strip()
    print("Received:", data)

    if data == "close":
        break

    res = do_some_stuffs_with_input(data)
    print("파이 동작:", res)

    conn.sendall(res.encode("utf-8"))
    conn.close()

s.close()
