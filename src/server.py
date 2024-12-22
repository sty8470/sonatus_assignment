import socket  # TCP/IP 통신 소켓을 생성하고 관리하기 위해 사용
import threading  # 멀티스레딩 처리를 통해 여러 클라이언트를 동시에 처리할 수 있도록 지원
import json  # 클라이언트와 서버 간 데이터를 JSON 형식으로 직렬화/역직렬화하기 위해 사용
import argparse  # 명령줄에서 서버의 설정(host, port, timeout)을 동적으로 전달받기 위해 사용
import logging  # 서버 실행 중 발생하는 이벤트(정보, 경고, 오류)를 로그로 기록
from enum import Enum  # 코드에서 사용하는 에러 코드를 열거형으로 정의하여 가독성과 유지보수성 향상

# 로깅 설정: 로그 레벨을 INFO로 설정하여 중요한 정보를 출력
logging.basicConfig(level=logging.INFO)

# 에러 코드 열거형 및 메시지 매핑
class ErrorCode(Enum):
    OK = 0  # 정상 처리 완료
    TIMEOUT = 1  # 서버로부터 응답을 받는 데 시간이 초과된 경우
    OUT_OF_ORDER = 2  # 클라이언트가 보내온 step_id가 순차적이지 않은 경우
    UNEXPECTED_ERROR = 3  # 예기치 못한 오류가 발생한 경우

# TCP 서버 클래스 정의
class TCPServer:
    def __init__(self, host='localhost', port=8080, timeout_threshold=5):
        """
        TCPServer 클래스 초기화 메서드
        - host: 서버가 바인딩될 IP 주소 (기본값 'localhost')
        - port: 서버가 바인딩될 포트 번호 (기본값 8080)
        - timeout_threshold: 클라이언트 요청 처리 시 기준이 되는 timeout 임계값 (기본값 5초)
        """
        self.host = host  # 서버가 실행될 IP 주소
        self.port = port  # 서버가 실행될 포트 번호
        self.current_step = 0  # 서버가 기억하는 현재 유효한 step_id 값 (초기값 0)
        self.lock = threading.Lock()  # 다중 스레드 간 공유 자원 접근을 제어하기 위한 락
        self.timeout_threshold = timeout_threshold  # 클라이언트 요청 timeout 임계값

    def handle_client(self, client_socket):
        """
        handle_client 메서드
        - 클라이언트와 통신을 처리하며, JSON 데이터를 받고 step_id를 확인
        - 정상 처리 또는 에러 응답을 클라이언트로 반환
        """
        while True:
            try:
                data = client_socket.recv(1024)  # 클라이언트로부터 데이터를 1024바이트 크기로 수신 #receive의 뜻 
                if not data:  # 데이터가 없으면 클라이언트 연결 종료
                    break

                # 디버그 포인트: 수신된 데이터를 확인
                logging.info(f"클라이언트로부터 받은 raw data: {data}")

                request = json.loads(data.decode())  # 수신된 데이터를 JSON 형식으로 디코딩
                step_id = request.get("step_id")  # JSON 데이터에서 step_id 값을 추출
                request_timeout = request.get("timeout")  # JSON 데이터에서 timeout 값을 추출

                # timeout 값이 서버의 임계값보다 작을 경우 TIMEOUT 에러 반환
                if request_timeout < self.timeout_threshold:
                    response = {"step_id": step_id, "error_code": ErrorCode.TIMEOUT.value}
                    logging.info(f"Step {step_id} - 요청 timeout({request_timeout})이 임계값({self.timeout_threshold})보다 작음. TIMEOUT 에러 반환")
                else:
                    # timeout 조건 충족 시, step_id의 순차성 검증
                    with self.lock:  # 락을 사용해 데이터 무결성 보장
                        if step_id == self.current_step + 1:  # step_id가 서버가 기억하는 값보다 정확히 +1일 경우
                            response = {"step_id": step_id, "error_code": ErrorCode.OK.value}  # 정상 처리 응답 생성
                            self.current_step = step_id  # 현재 유효한 step_id를 업데이트
                        else:  # step_id가 순차적이지 않은 경우 OUT_OF_ORDER 에러 반환
                            response = {"step_id": step_id, "error_code": ErrorCode.OUT_OF_ORDER.value}
                            logging.info(f"순차적이지 않은 step_id: {step_id} - OUT_OF_ORDER 에러 발생")
                            self.current_step += 1  # 에러 발생 시에도 step_id 증가

                client_socket.sendall(json.dumps(response).encode())  # 응답 데이터를 JSON 형식으로 직렬화 후 클라이언트에게 전송

            except socket.timeout:  # 클라이언트 요청 처리 중 소켓 타임아웃 발생
                response = {"step_id": step_id, "error_code": ErrorCode.TIMEOUT.value}
                client_socket.sendall(json.dumps(response).encode())
                logging.info("클라이언트 처리 중 타임아웃 발생")
                break
            except Exception as e:  # 기타 예외 처리
                response = {"step_id": step_id, "error_code": ErrorCode.UNEXPECTED_ERROR.value}
                client_socket.sendall(json.dumps(response).encode())
                logging.info(f"클라이언트 처리 중 예기치 못한 오류 발생: {e}")
                break

        client_socket.close()  # 클라이언트 소켓 연결 종료

    def start(self):
        """
        서버 시작 메서드
        - 지정된 IP와 포트에서 클라이언트 요청을 수락하며 처리 스레드 생성
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP 소켓 생성 (IPv4, TCP 프로토콜)
        server_socket.bind((self.host, self.port))  # 소켓을 지정된 IP와 포트에 바인딩
        server_socket.listen(5)  # 최대 5개의 연결 요청을 큐에 대기
        logging.info(f"서버가 {self.host}:{self.port}에서 대기 중입니다. Timeout threshold: {self.timeout_threshold}")

        while True:
            client_socket, addr = server_socket.accept()  # 클라이언트 연결 요청 수락, 소켓과 주소 반환
            logging.info(f"{addr}주소에서 {client_socket}연결 수락됨")  # 연결된 클라이언트 주소 로그 출력
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))  # 클라이언트 요청 처리를 위한 스레드 생성
            client_thread.start()  # 스레드 실행
            # logging.info(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

if __name__ == "__main__":
    # 프로그램의 진입점
    parser = argparse.ArgumentParser(description="TCP Server for handling client communication.")  # argparse 객체 생성 및 명령줄 옵션 설명 추가
    parser.add_argument("--host", default="localhost", help="Specify the host IP to bind the server. Default is 'localhost'.")  # --host 옵션 정의
    parser.add_argument("--port", type=int, default=8080, help="Specify the port to bind the server. Default is 8080.")  # --port 옵션 정의
    parser.add_argument("--timeout", type=int, default=5, help="Specify the timeout threshold in seconds.")  # --timeout 옵션 정의
    args = parser.parse_args()  # 명령줄 인자 파싱

    server = TCPServer(host=args.host, port=args.port, timeout_threshold=args.timeout)  # TCPServer 객체 생성, 명령줄에서 받은 인자로 초기화
    server.start()  # 서버 실행
