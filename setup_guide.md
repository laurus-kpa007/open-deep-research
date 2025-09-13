# Deep Research Agent - 상세 설정 가이드

이 문서는 Deep Research Agent를 처음 설치하고 실행하는 방법을 단계별로 안내합니다.

## 🎯 설치 옵션 / Installation Options

### Option 1: Docker를 사용한 빠른 설치 (권장)
### Option 2: 로컬 개발 환경 설정

---

## Option 1: Docker 설치 (권장)

### 1. 사전 준비

```bash
# Docker 설치 확인
docker --version
docker-compose --version

# 없다면 설치 필요:
# https://docs.docker.com/get-docker/
```

### 2. 프로젝트 클론

```bash
git clone <repository-url>
cd open_deep_research
```

### 3. 환경 설정

```bash
# 환경 파일 복사
cp .env.example .env

# 환경 파일 편집 (필요시)
nano .env
```

### 4. 서비스 시작

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f ollama
```

### 5. 접속 확인

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

---

## Option 2: 로컬 개발 환경

### 1. Ollama 설치 및 설정

#### Windows
```powershell
# Ollama 다운로드 및 설치
# https://ollama.ai/download 에서 Windows 버전 다운로드

# 명령 프롬프트에서 확인
ollama --version
```

#### macOS
```bash
# Homebrew 사용
brew install ollama

# 또는 직접 다운로드
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### 모델 설치
```bash
# Ollama 서비스 시작 (백그라운드)
ollama serve

# 새 터미널에서 모델 다운로드
ollama pull gemma3:12b

# 설치 확인
ollama list
```

### 2. Python 백엔드 설정

#### Python 및 Poetry 설치
```bash
# Python 3.11+ 설치 확인
python --version

# Poetry 설치
pip install poetry

# 또는 curl 사용
curl -sSL https://install.python-poetry.org | python3 -
```

#### 백엔드 의존성 설치
```bash
cd backend

# 가상환경 생성 및 의존성 설치
poetry install

# 환경 파일 설정
cp .env.example .env
```

#### 환경 변수 설정
`.env` 파일 편집:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:12b
TAVILY_API_KEY=your_api_key_here  # 선택사항
DATABASE_URL=sqlite:///./research.db  # 개발용
```

#### 백엔드 실행
```bash
# 개발 서버 시작
poetry run uvicorn src.open_deep_research.api.main:socket_app --reload --host 0.0.0.0 --port 8000
```

### 3. Node.js 프론트엔드 설정

#### Node.js 설치
```bash
# Node.js 18+ 설치 확인
node --version
npm --version

# 없다면 https://nodejs.org 에서 설치
```

#### 프론트엔드 의존성 설치
```bash
cd frontend

# 의존성 설치
npm install

# 또는 yarn 사용
yarn install
```

#### 환경 변수 설정
`.env.local` 파일 생성:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

#### 프론트엔드 실행
```bash
# 개발 서버 시작
npm run dev

# 또는
yarn dev
```

---

## 📋 설치 후 확인 사항

### 1. Health Check
http://localhost:8000/api/v1/health 접속하여 상태 확인:
```json
{
  "status": "healthy",
  "ollama_available": true,
  "search_available": true
}
```

### 2. 기능 테스트
1. http://localhost:3000 접속
2. 간단한 질문 입력 ("AI의 미래 전망은?")
3. 연구 진행 과정 확인
4. 결과 확인

### 3. 로그 확인
- 백엔드: 터미널에서 로그 확인
- 프론트엔드: 브라우저 개발자 도구 콘솔
- Ollama: `ollama logs` 또는 시스템 로그

---

## 🔧 고급 설정

### Tavily API 키 설정
1. https://app.tavily.com/ 가입
2. API 키 발급
3. `.env` 파일에 추가:
```env
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxx
```

### PostgreSQL 사용 (프로덕션)
```bash
# PostgreSQL 설치 및 시작
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# 데이터베이스 생성
sudo -u postgres createdb research_db
sudo -u postgres createuser research_user

# .env 파일 수정
DATABASE_URL=postgresql+asyncpg://research_user:password@localhost:5432/research_db
```

### 성능 최적화
```bash
# Ollama GPU 가속 (NVIDIA CUDA)
CUDA_VISIBLE_DEVICES=0 ollama serve

# 메모리 제한
OLLAMA_MAX_LOADED_MODELS=1 ollama serve
```

---

## 🚨 문제 해결

### Ollama 관련 문제
```bash
# 서비스 상태 확인
ollama list

# 프로세스 확인
ps aux | grep ollama

# 포트 사용 확인
netstat -tulpn | grep 11434

# 재시작
pkill ollama
ollama serve
```

### Python 의존성 문제
```bash
# Poetry 캐시 클리어
poetry cache clear --all pypi

# 의존성 재설치
poetry install --no-cache
```

### Node.js 문제
```bash
# 캐시 클리어
npm cache clean --force

# node_modules 재설치
rm -rf node_modules package-lock.json
npm install
```

### 포트 충돌 문제
```bash
# 포트 사용 확인
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000
netstat -tulpn | grep :11434

# 프로세스 종료
kill -9 <PID>
```

---

## 📞 추가 지원

문제가 지속되면:
1. GitHub Issues에 문제 보고
2. 로그 파일 첨부
3. 시스템 정보 (OS, Python/Node 버전) 포함

**성공적인 설치를 위한 팁**: 
- 각 단계를 순서대로 진행
- 오류 메시지를 주의 깊게 읽기
- 각 서비스가 정상 작동하는지 확인 후 다음 단계 진행