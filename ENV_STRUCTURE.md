# 환경 변수 파일 구조

## 통합된 환경 변수 관리

### 현재 구조
```
open_deep_research/
├── .env                    # 메인 환경 변수 파일 (개발용)
├── .env.example            # 환경 변수 예제
├── .env.production         # 프로덕션 환경 변수
├── frontend/
│   └── .env.local          # Next.js 로컬 환경 변수 (NEXT_PUBLIC_* 변수용)
└── backend/
    └── (삭제됨: .env)      # 루트 .env 파일 사용
```

### 루트 .env 파일 구조
```env
# Ollama Configuration
OLLAMA_BASE_URL=http://192.168.0.3:11434  # 원격 접속 시 IP 주소로 변경
OLLAMA_MODEL=gemma3:4b  # 또는 gemma3:12b, deepseek-r1:8b 등

# Search API Configuration
TAVILY_API_KEY=your_api_key_here  # https://app.tavily.com/에서 발급

# Database Configuration
DATABASE_URL=sqlite:///./research_database.db

# Security
SECRET_KEY=your-secret-key-for-deep-research-agent-2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration (원격 접속할 주소들을 모두 추가)
CORS_ORIGINS=http://192.168.0.3:3000,http://192.168.0.244:3000,http://localhost:3000,http://127.0.0.1:3000
FRONTEND_URL=http://192.168.0.3:3000

# Logging
LOG_LEVEL=INFO

# Docker Configuration (for docker-compose)
COMPOSE_PROJECT_NAME=deep-research-agent

# Production Configuration
NODE_ENV=development  # production으로 변경 가능
ENVIRONMENT=development  # production으로 변경 가능

# Next.js Configuration
NEXT_PUBLIC_API_URL=http://192.168.0.3:8000
NEXT_PUBLIC_WS_URL=ws://192.168.0.3:8000
```

### frontend/.env.local 파일
Next.js는 `.env.local`을 우선적으로 읽으므로, 프론트엔드 전용 설정에 사용
```env
NEXT_PUBLIC_API_URL=http://192.168.0.3:8000
NEXT_PUBLIC_WS_URL=ws://192.168.0.3:8000
```

## 장점
1. **중앙 집중 관리**: 모든 환경 변수를 한 곳에서 관리
2. **중복 제거**: 동일한 설정을 여러 파일에 반복하지 않음
3. **일관성**: 백엔드와 프론트엔드가 동일한 설정 공유
4. **유지보수 용이**: 한 파일만 수정하면 됨
5. **원격 접속 지원**: CORS_ORIGINS에 여러 IP 주소 추가 가능

## 주의사항
- 백엔드는 이제 루트 디렉토리의 `.env` 파일을 자동으로 읽음
- 프론트엔드는 루트 `.env`와 `frontend/.env.local` 모두 읽을 수 있음
- IP 주소 변경 시 루트 `.env` 파일만 수정하면 됨
- 보안상 `.env` 파일은 절대 Git에 커밋하지 말 것 (.gitignore에 포함됨)
- 프로덕션 환경에서는 `.env.production` 파일 사용

## 환경별 설정

### 개발 환경 (Development)
- `ENVIRONMENT=development`
- `NODE_ENV=development`
- `LOG_LEVEL=DEBUG` 또는 `INFO`
- 로컬 IP 주소 사용 (localhost, 127.0.0.1)

### 프로덕션 환경 (Production)
- `ENVIRONMENT=production`
- `NODE_ENV=production`
- `LOG_LEVEL=WARNING` 또는 `ERROR`
- 실제 도메인 또는 공인 IP 주소 사용
- 강력한 SECRET_KEY 사용 (랜덤 생성)

### 원격 접속 설정
1. 모든 IP 주소를 네트워크 IP로 변경 (예: 192.168.x.x)
2. CORS_ORIGINS에 접속할 모든 클라이언트 IP 추가
3. 방화벽에서 포트 8000, 3000 허용
4. Ollama 서버도 원격 접속 허용 설정 (`OLLAMA_HOST=0.0.0.0:11434`)