# Deep Research Agent - Web Implementation

🧠 **AI 기반 심층 연구 에이전트** / AI-Powered Deep Research Agent

Ollama를 활용한 로컬 LLM 기반 웹 연구 도구로, 한국어와 영어를 지원합니다.  
A web-based research tool powered by local LLM via Ollama, supporting Korean and English.

## ✨ 주요 특징 / Key Features

- 🤖 **로컬 LLM 통합** - Ollama와 Gemma 3 모델을 사용한 프라이버시 보장
- 🌐 **다국어 지원** - 한국어/영어 자동 감지 및 응답
- ⚡ **실시간 진행 상황** - WebSocket 기반 실시간 업데이트
- 📊 **고품질 보고서** - 다중 소스 기반 구조화된 연구 보고서
- 🐳 **Docker 지원** - 간편한 배포 및 관리

## 🏗️ 아키텍처 / Architecture

```
Frontend (Next.js) ↔ Backend (FastAPI) ↔ Ollama (Gemma 3:12B)
                            ↓
                    SQLite Database
```

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, LangGraph, Pydantic
- **LLM**: Ollama with Gemma 3:12B
- **Database**: SQLite (PostgreSQL ready)
- **Search**: Tavily API

📊 **[시스템 구성도 보기 / View System Architecture](./ARCHITECTURE.md)**

## 🚀 빠른 시작 / Quick Start

### 전제 조건 / Prerequisites

1. **Docker & Docker Compose** (권장 / Recommended)
2. **Ollama** (로컬 설치 시 / For local installation)
3. **Node.js 18+** (개발 시 / For development)
4. **Python 3.11+** (개발 시 / For development)

### Docker로 시작하기 / Getting Started with Docker

1. **저장소 복제 / Clone Repository**
```bash
git clone <repository-url>
cd open_deep_research
```

2. **환경 설정 / Environment Setup**
```bash
cp .env.example .env
# Edit .env file with your settings
```

3. **서비스 시작 / Start Services**
```bash
docker-compose up -d
```

4. **브라우저에서 접속 / Access in Browser**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 로컬 개발 설정 / Local Development Setup

#### 1. Ollama 설치 및 설정 / Ollama Installation

```bash
# Ollama 설치 / Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Ollama 서비스 시작 / Start Ollama service
ollama serve

# Gemma 3 모델 다운로드 / Download Gemma 3 model
ollama pull gemma3:12b
```

#### 2. 백엔드 설정 / Backend Setup

```bash
cd backend

# Poetry 설치 (if not installed)
pip install poetry

# 의존성 설치 / Install dependencies
poetry install

# 환경 변수 설정 / Setup environment
cp .env.example .env

# 개발 서버 시작 / Start development server
poetry run uvicorn src.open_deep_research.api.main:socket_app --reload --host 0.0.0.0 --port 8000
```

#### 3. 프론트엔드 설정 / Frontend Setup

```bash
cd frontend

# 의존성 설치 / Install dependencies
npm install

# 개발 서버 시작 / Start development server
npm run dev
```

## 🔧 환경 설정 / Configuration

### 필수 환경 변수 / Required Environment Variables

```env
# Ollama 설정
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:12b

# 검색 API (선택사항)
TAVILY_API_KEY=your_tavily_api_key

# 데이터베이스
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/research_db
```

### Tavily API 키 설정 / Tavily API Key Setup

1. [Tavily](https://app.tavily.com/)에서 계정 생성
2. API 키 발급
3. `.env` 파일에 `TAVILY_API_KEY` 설정

> **참고**: Tavily API 키가 없어도 시스템은 작동하지만, 검색 기능이 제한됩니다.

## 📖 사용 방법 / How to Use

### 1. 기본 연구 실행 / Basic Research

1. 웹 인터페이스 접속 (http://localhost:3000)
2. 연구 질문 입력 (한국어 또는 영어)
3. **연구 시작** 버튼 클릭
4. 실시간 진행 상황 모니터링
5. 완료 후 결과 확인 및 다운로드

### 2. 고급 설정 / Advanced Settings

- **언어**: 자동 감지, 한국어, 영어
- **연구 깊이**: 간단, 보통, 심층
- **동시 연구원 수**: 1-5명 (병렬 처리)

### 3. API 사용법 / API Usage

```bash
# 연구 시작 / Start Research
curl -X POST "http://localhost:8000/api/v1/research/start" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI 기술의 최신 동향", "language": "ko"}'

# 연구 상태 확인 / Check Research Status
curl "http://localhost:8000/api/v1/research/{session_id}"

# 보고서 조회 / Get Report
curl "http://localhost:8000/api/v1/research/{session_id}/report"
```

## 🛠️ 개발 / Development

### 프로젝트 구조 / Project Structure

```
open_deep_research/
├── backend/                 # FastAPI 백엔드
│   ├── src/open_deep_research/
│   │   ├── api/            # API 엔드포인트
│   │   ├── core/           # 핵심 로직
│   │   ├── models/         # 데이터 모델
│   │   ├── services/       # 서비스 레이어
│   │   ├── prompts/        # 프롬프트 템플릿
│   │   └── utils/          # 유틸리티
│   ├── tests/              # 테스트
│   └── pyproject.toml      # 의존성 관리
├── frontend/               # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/           # Next.js App Router
│   │   ├── components/    # React 컴포넌트
│   │   ├── hooks/         # React 훅
│   │   └── lib/           # 라이브러리
│   └── package.json       # 의존성 관리
└── docker-compose.yml     # Docker 구성
```

### 테스트 실행 / Running Tests

```bash
# 백엔드 테스트 / Backend Tests
cd backend
poetry run pytest

# 프론트엔드 테스트 / Frontend Tests
cd frontend
npm run test
```

### 코드 품질 / Code Quality

```bash
# 백엔드 린팅 / Backend Linting
cd backend
poetry run ruff check
poetry run mypy src

# 프론트엔드 린팅 / Frontend Linting
cd frontend
npm run lint
npm run type-check
```

## 🔍 트러블슈팅 / Troubleshooting

### 일반적인 문제 / Common Issues

1. **Ollama 연결 실패**
   - Ollama 서비스가 실행 중인지 확인: `ollama list`
   - 모델이 설치되어 있는지 확인: `ollama list`
   - 포트 충돌 확인: `netstat -tulpn | grep 11434`

2. **검색 기능 제한**
   - Tavily API 키가 설정되었는지 확인
   - API 키의 유효성 확인

3. **WebSocket 연결 오류**
   - CORS 설정 확인
   - 방화벽 설정 확인
   - 브라우저 콘솔에서 오류 메시지 확인

### 로그 확인 / Log Checking

```bash
# Docker 로그 확인 / Check Docker Logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ollama

# 백엔드 직접 실행 시 로그 / Direct Backend Logs
LOG_LEVEL=DEBUG poetry run uvicorn src.open_deep_research.api.main:socket_app --reload
```

## 📊 성능 최적화 / Performance Optimization

### 시스템 요구사항 / System Requirements

- **최소**: 8GB RAM, 2 CPU cores
- **권장**: 16GB RAM, 4+ CPU cores
- **디스크**: 10GB+ (모델 저장용)

### 성능 튜닝 / Performance Tuning

1. **Ollama 설정**
   ```bash
   # GPU 사용 (NVIDIA CUDA)
   CUDA_VISIBLE_DEVICES=0 ollama serve
   
   # 메모리 제한
   OLLAMA_HOST=0.0.0.0:11434 OLLAMA_MAX_LOADED_MODELS=1 ollama serve
   ```

2. **동시 연구원 수 조절**
   - 시스템 리소스에 따라 1-5명 조절
   - CPU 코어 수에 따라 최적화

## 📝 라이센스 / License

MIT License - 자세한 내용은 LICENSE 파일을 참조하세요.

## 🤝 기여 / Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📞 지원 / Support

- 이슈 리포트: [GitHub Issues](https://github.com/your-repo/issues)
- 문서: [Architecture Design](./architecture_design.md)
- 데이터 흐름: [Data Flow Analysis](./data_flow_analysis.md)

---

**Based on**: [Open Deep Research](https://github.com/langchain-ai/open_deep_research) by LangChain AI