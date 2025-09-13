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
OLLAMA_BASE_URL=http://192.168.0.244:11434
OLLAMA_MODEL=deepseek-r1:8b

# Search API Configuration
TAVILY_API_KEY=your_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./research_database.db

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=http://192.168.0.3:3000,http://localhost:3000,http://127.0.0.1:3000
FRONTEND_URL=http://192.168.0.3:3000

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development

# Next.js Configuration (프론트엔드용)
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

## 주의사항
- 백엔드는 이제 루트 디렉토리의 `.env` 파일을 자동으로 읽음
- 프론트엔드는 루트 `.env`와 `frontend/.env.local` 모두 읽을 수 있음
- IP 주소 변경 시 루트 `.env` 파일만 수정하면 됨