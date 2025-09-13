# 원격 접속 문제 해결 완료

## 문제
- 원격에서 프론트엔드는 접속되지만 백엔드 연결 실패
- "시스템 연결 오류 / System Connection Error" 메시지 표시

## 원인
1. 프론트엔드의 환경 변수가 제대로 적용되지 않음
2. Socket.IO CORS 설정 문제
3. uvicorn 실행 시 socket_app을 사용하지 않음

## 해결 방법

### 1. 프론트엔드 환경 설정 (frontend/.env.local 생성)
```env
NEXT_PUBLIC_API_URL=http://192.168.0.3:8000
NEXT_PUBLIC_WS_URL=ws://192.168.0.3:8000
```

### 2. 백엔드 CORS 설정 (.env 파일)
```env
CORS_ORIGINS=http://192.168.0.3:3000,http://192.168.0.244:3000,http://localhost:3000,http://127.0.0.1:3000
ENVIRONMENT=development
```

### 3. 서버 재시작

#### 백엔드 (PowerShell)
```powershell
cd backend
# 가상환경 활성화 후
pip install python-socketio  # Socket.IO 설치 필요
uvicorn src.open_deep_research.api.main:socket_app --host 0.0.0.0 --port 8000 --reload
```
**중요**: `main:app` 대신 `main:socket_app` 사용!

#### 프론트엔드 (다른 터미널)
```powershell
cd frontend
npm run dev
```

### 4. 접속 테스트
- 로컬: http://localhost:3000
- 원격: http://192.168.0.3:3000

## 확인 사항
- 백엔드 헬스체크: http://192.168.0.3:8000/api/v1/health
- 방화벽에서 포트 3000, 8000 열려있는지 확인
- Windows Defender 방화벽 예외 추가 필요할 수 있음

## 주의사항
- 프론트엔드 환경 변수 변경 후 반드시 재시작 필요
- IP 주소 변경 시 .env.local과 .env 파일 모두 수정 필요