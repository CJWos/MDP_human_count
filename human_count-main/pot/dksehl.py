import socket
import Adafruit_DHT

HOST = "10.153.153.69"  # 모든 네트워크 인터페이스에서 들을 수 있도록 0.0.0.0으로 설정
PORT = 8003

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')
s.bind((HOST, PORT))
print('Socket bind complete')
s.listen(1)
print('Socket now listening')

def read_temperature_humidity():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 4)  # GPIO 4에 DHT11 센서를 연결한 경우
    if humidity is not None and temperature is not None:
        return temperature, humidity
    else:
        return None, None

while True:
    conn, addr = s.accept()
    print("Connected by", addr)

    data = conn.recv(1024)
    if not data:
        break

    data = data.decode("utf8").strip()
    print("Received:", data)

    if data == "GET":
        temperature, humidity = read_temperature_humidity()
        if temperature is not None and humidity is not None:
            response = "온도: {:.1f}도, 습도: {:.1f}%".format(temperature, humidity)
        else:
            response = "온도 및 습도를 읽을 수 없습니다."
    else:
        response = "잘못된 명령어입니다."

    conn.sendall(response.encode("utf-8"))
    conn.close()

s.close()
