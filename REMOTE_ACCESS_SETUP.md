# 원격 접속 설정 가이드

## 문제 해결: 백엔드 접속 불가 문제

### 원인
CORS(Cross-Origin Resource Sharing) 설정이 원격 접속 주소를 허용하지 않아서 발생

### 해결 방법

#### 1. 환경 변수 설정 (.env 파일)
```bash
# CORS 설정에 원격 접속할 모든 주소를 추가
CORS_ORIGINS=http://192.168.0.3:3000,http://192.168.0.244:3000,http://localhost:3000,http://127.0.0.1:3000

# API URL 설정 (실제 서버 IP로 변경)
NEXT_PUBLIC_API_URL=http://192.168.0.3:8000
NEXT_PUBLIC_WS_URL=ws://192.168.0.3:8000
```

#### 2. 백엔드 CORS 설정 확인
- `backend/cors_config.py` 파일이 환경 변수에서 CORS_ORIGINS를 읽어옴
- `backend/src/open_deep_research/api/main.py`가 cors_config.py를 사용하도록 수정됨

#### 3. Docker 실행 시 (docker-compose.prod.yml 사용)
```bash
# .env.production 파일 수정
SERVER_HOST=실제_서버_IP
CORS_ORIGINS=http://실제_서버_IP:3000,http://원격_접속_IP:3000

# Docker 실행
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

#### 4. 일반 실행 시
```bash
# Backend 실행
cd backend
uvicorn src.open_deep_research.api.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend 실행
cd frontend
npm run dev -- --host 0.0.0.0
```

### 중요 사항
1. **방화벽 설정**: 포트 3000, 8000이 열려있는지 확인
2. **IP 주소**: 실제 네트워크 IP 주소 사용 (localhost는 원격에서 접속 불가)
3. **CORS_ORIGINS**: 접속하려는 모든 주소를 콤마로 구분하여 추가

### 테스트 방법
1. 브라우저 개발자 도구 (F12) 열기
2. Network 탭에서 API 요청 확인
3. CORS 에러가 없는지 확인