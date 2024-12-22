
# Sonatus TCP 서버-클라이언트 과제

이 프로젝트는 Python을 사용한 TCP 서버-클라이언트 시스템을 구현하며, 클라이언트가 각기 다른 타임아웃과 대기 시간 설정에 따라 서버에 순차적으로 데이터를 전송합니다. 서버는 데이터 순서를 검증하고 조건에 맞지 않을 경우 에러 코드를 반환합니다.

## 프로젝트 구조

```
SONATUS_ASSIGNMENT/
├── docs/
│   ├── overview.pdf
│   └── README.md
├── pcap/
│   ├── success_capture.pcap
│   ├── failure_capture.pcap
├── src/
│   ├── client.py
│   └── server.py
├── test_data/
│   ├── failure_data.json
│   └── success_data.json
└── requirements.txt
```

- **docs/**: 개발자 및 비개발자를 위한 문서 파일
- **pcap/**: 성공 및 실패 테스트 케이스에 대한 패킷 캡처 파일
- **src/**: 주요 코드 파일 (`client.py`와 `server.py`)
- **test_data/**: 성공 및 실패 시나리오를 위한 JSON 테스트 파일
- **requirements.txt**: 프로그램 실행에 필요한 라이브러리 목록

## 요구 사항

서버와 클라이언트 스크립트를 실행하려면 필요한 Python 패키지를 먼저 설치해야 합니다:
```bash
pip install -r requirements.txt
```

## 사용법

서버 또는 클라이언트 스크립트를 실행하기 전에 `src/` 디렉토리로 이동하세요:
```bash
cd SONATUS_ASSIGNMENT/src
```

### 서버 실행

기본 또는 사용자 정의 옵션으로 서버를 실행하세요:
```bash
python server.py --host localhost --port 8080 --timeout 5
```
- **--host**: 서버 IP 주소 (기본값: `localhost`)
- **--port**: 서버 포트 (기본값: `8080`)
- **--timeout**: 타임아웃 임계값 (초 단위, 기본값: `5`)

### 클라이언트 실행

서버에 연결하기 위해 클라이언트를 실행하세요:
```bash
python client.py --data success --host localhost --port 8080
```
- **--data**: `test_data/`에 있는 테스트 데이터 파일 (`success` 또는 `failure`)
- **--host**: 서버 IP 주소 (기본값: `localhost`)
- **--port**: 서버 포트 (기본값: `8080`)

### 테스트 시나리오

- **성공 데이터** (`success_data.json`): 순차적인 `step_id`와 최소 5초의 타임아웃을 확인합니다.
- **실패 데이터** (`failure_data.json`): 순차적이지 않은 `step_id` 또는 5초 미만의 타임아웃 조건을 포함합니다.

## 결론

이 프로젝트를 통해 TCP 통신, 멀티스레딩, 에러 핸들링에 대해 깊이 학습할 수 있었습니다. 향후 개선 사항으로 비동기 I/O 도입과 실시간 데이터 처리를 위한 데이터베이스 통합을 고려할 수 있습니다.
