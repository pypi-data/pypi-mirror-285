import serial
import serial.tools.list_ports
import time

class PyArduino:
    def __init__(self):
        """
        수신받은 데이터 값을 저장하는 변수 초기화
        아두이노 객체 초기화
        """
        self.serial_receive_data = ""
        self.arduino = None  

    def connect(self):
        """
        ===========================================
        시리얼 클래스를 사용하여 아두이노 객체 생성
        직렬 포트를 검색하여 'Arduino Uno'가 포함된 포트를 찾아 연결합니다.

        예제:
        >>> py_arduino = PyArduino()
        >>> py_arduino.connect()
        (포트를 검색하여 아두이노를 연결합니다.)

        """
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "Arduino Uno" in p.description:
                print(f"{p} 포트에 연결하였습니다.")
                self.arduino = serial.Serial(p.device, baudrate=9600, timeout=1.0)
                time.sleep(2.0)

    def close(self):
        """
        =====================
        시리얼 포트 연결 종료

        예제:
        >>> py_arduino = PyArduino()   # 객체생성
        >>> py_arduino.connect()       # 포트연결
        >>> py_arduino.close()
        (아두이노와의 연결을 종료합니다.)
        """
        if self.arduino:
            self.arduino.close()
            print("연결을 종료하였습니다.")

    def delay(self,delay_time):
        """
        ===================
        지정된 시간만큼 대기합니다.

        매개변수:
        - delay_time (float): 대기할 시간(초)

        예제:
        >>> py_arduino = PyArduino()       # 객체생성
        >>> py_arduino.connect()           # 포트연결
        >>> for i in range(10):   
                py_arduino.send_bright()
                py_arduino.delay(0.1)      # 빛센서를 0.1초 간격으로 10회 읽어들입니다
        """
        time.sleep(delay_time)

    def send_rgb(self, cnt=1):
        """
        =========================================================
        빨강, 초록, 파랑 순서로 매개변수 횟수만큼 RGB LED 깜빡이기

        매개변수:
        - cnt (int): LED를 깜빡일 횟수

        예제:
        >>> py_arduino = PyArduino()   # 객체생성
        >>> py_arduino.connect()       # 포트연결
        >>> py_arduino.send_rgb(3)     # RGB LED를 빨강, 초록, 파랑 순서로 3회 깜빡입니다
        """
        self.cnt = cnt
        for i in range(self.cnt):
            self.arduino.write("RGB=255,0,0\n".encode())
            time.sleep(1)
            self.arduino.write("RGB=0,255,0\n".encode())
            time.sleep(1)
            self.arduino.write("RGB=0,0,255\n".encode())
            time.sleep(1)
        self.arduino.write("RGB=0,0,0\n".encode())  # LED 끄고 종료

    def send_rgb_color(self, red=255, green=255, blue=255):
        """
        ===================================
        매개변수로 받은 RGB 값으로 LED 켜기

        매개변수:
        - red (int): 빨강 값 (0~255)
        - green (int): 초록 값 (0~255)
        - blue (int): 파랑 값 (0~255)

        예제:
        >>> py_arduino = PyArduino()                  # 객체생성
        >>> py_arduino.connect()                      # 포트연결
        >>> py_arduino.send_rgb_color(255, 100, 50)   # RGB LED를 빨강 255, 초록 100, 파랑 50으로 설정하여 켭니다
        """
        self.arduino.write(f'RGB={red},{green},{blue}\n'.encode())

    def send_servo(self,degree):
        """
        =========================
        서보모터 각도 데이터 전송

        매개변수:
        - degree (int): 서보모터 각도 (0~180)

        예제:
        >>> py_arduino = PyArduino()   # 객체생성
        >>> py_arduino.connect()       # 포트연결
        >>> py_arduino.send_servo(90)  # 서보모터를 90도로 회전시킵니다
        """
        self.arduino.write(f"SERVO={degree}\n".encode())

    def send_buzzer(self,freq):
        """
        ============================
        버저 음계 주파수 데이터 전송

        주어진 주파수를 아두이노로 전송하여 버저로 해당 음계를 재생합니다.

        매개변수:
        - freq (int): 전송할 음계의 주파수 (Hz)

        음계와 해당 주파수:
        - 도 (C4) : 261.63 Hz
        - 레 (D4) : 293.66 Hz
        - 미 (E4) : 329.63 Hz
        - 파 (F4) : 349.23 Hz
        - 솔 (G4) : 392.00 Hz
        - 라 (A4) : 440.00 Hz
        - 시 (B4) : 493.88 Hz
        - 높은 도 (C5) : 523.25 Hz

        예제:
        >>> py_arduino = PyArduino()      # 객체생성
        >>> py_arduino.connect()          # 포트연결
        >>> py_arduino.send_buzzer(440)   # 아두이노에 440 Hz의 라(A4) 음을 전송합니다
        """          
        self.arduino.write(f"BUZZER={freq}\n".encode())

    def send_fnd(self,data):
        """
        ======================================
        FND (7세그먼트 디스플레이) 데이터 전송

        매개변수:
        - data (str): FND에 표시할 데이터

        예제:
        >>> py_arduino = PyArduino()      # 객체생성
        >>> py_arduino.connect()          # 포트연결
        >>> py_arduino.send_fnd("1234")   # FND에 '1234'를 표시합니다
        """
        self.arduino.write(f"FND={data}\n".encode())

    def request_sensor_data(self, sensor_command, sensor_label):
        """
        ================================================
        매개변수의 센서 값을 요청하고 결과 리턴하는 함수

        매개변수:
        - sensor_command (str): 아두이노에게 보낼 센서 값을 요청하기 위한 문자열
        - sensor_label (str): 요청된 센서 값의 문자열

        예제:
        >>> py_arduino = PyArduino()                               # 객체생성
        >>> py_arduino.connect()                                   # 포트연결
        >>> py_arduino.request_sensor_data("BRIGHT=?", "BRIGHT")   # 빛센서값을 받아서 리턴
        """
        self.arduino.flushInput()  # 입력 버퍼 비우기
        self.serial_receive_data = ""
        self.arduino.write(f"{sensor_command}\n".encode())
        time.sleep(0.1)  
        read_data = self.arduino.readline()
        self.serial_receive_data = read_data.decode().strip()
        if sensor_label in self.serial_receive_data:
            sensor_value = self.serial_receive_data.split('=')[1]
            return int(sensor_value)

    def send_vr(self):
        """
        =====================
        VR (가변저항) 값 요청

        예제:
        >>> py_arduino = PyArduino()   # 객체생성
        >>> py_arduino.connect()       # 포트연결
        >>> py_arduino.send_vr()       # 가변저항 값을 요청합니다
        """
        return self.request_sensor_data("VR=?", "VR")

    def send_bright(self):
        """
        =================
        조도 센서 값 요청

        예제:
        >>> py_arduino = PyArduino()   # 객체생성
        >>> py_arduino.connect()       # 포트연결
        >>> py_arduino.send_bright()   # 조도 센서 값을 요청합니다
        """
        return self.request_sensor_data("BRIGHT=?", "BRIGHT")

    def send_temperature(self):
        """
        =================
        온도 센서 값 요청

        예제:
        >>> py_arduino = PyArduino()        # 객체생성
        >>> py_arduino.connect()            # 포트연결
        >>> py_arduino.send_temperature()   # 온도 센서 값을 요청합니다
        """
        return self.request_sensor_data("TEMPERATURE=?", "TEMPERATURE")

    def send_humidity(self):
        """
        =================
        습도 센서 값 요청

        예제:
        >>> py_arduino = PyArduino()       # 객체생성
        >>> py_arduino.connect()           # 포트연결
        >>> py_arduino.send_humidity()     # 습도 센서 값을 요청합니다
        """
        return self.request_sensor_data("HUMIDITY=?", "HUMIDITY")

    def send_object_temperature(self):
        """
        ======================
        물체 온도 센서 값 요청

        예제:
        >>> py_arduino = PyArduino()               # 객체생성
        >>> py_arduino.connect()                   # 포트연결
        >>> py_arduino.send_object_temperature()   # 물체 온도 센서 값을 요청합니다
        """
        return self.request_sensor_data("OBJECT=?", "OBJECT")

    def send_ambient_temperature(self):
        """
        ======================
        주변 온도 센서 값 요청

        예제:
        >>> py_arduino = PyArduino()                # 객체생성
        >>> py_arduino.connect()                    # 포트연결
        >>> py_arduino.send_ambient_temperature()   # 주변 온도 센서 값을 요청합니다
        """
        return self.request_sensor_data("AMBIENT=?", "AMBIENT")