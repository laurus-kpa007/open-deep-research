# 🚀 Deep Research Agent - 초보자를 위한 완전 설치 가이드

풀스택이 처음이시니까 하나하나 차근차근 설명드릴게요! 

## 📋 전체 구조 이해하기 (5분)

우선 이 프로젝트가 뭘로 이루어져 있는지 알아볼까요?

```
🖥️ 프론트엔드 (Next.js) - 웹페이지 (당신이 보는 화면)
    ↕️ 통신
🔧 백엔드 (FastAPI) - 서버 (데이터 처리)
    ↕️ 통신  
🤖 Ollama + Gemma 3 - AI 모델 (실제로 연구하는 AI)
```

**왜 이렇게 나눠져 있나요?**
- **프론트엔드**: 사용자가 질문을 입력하고 결과를 보는 예쁜 웹페이지
- **백엔드**: 질문을 받아서 AI에게 전달하고 결과를 정리해주는 중간 역할
- **Ollama**: AI 모델을 우리 컴퓨터에서 실행해주는 프로그램

## 🎯 설치 방법 선택하기

**두 가지 방법이 있어요:**
1. **Docker 사용 (추천!)** - 모든 걸 자동으로 설치 (초보자에게 좋음)
2. **수동 설치** - 하나하나 직접 설치 (개발자가 되려면 알아두면 좋음)

**Docker를 추천하는 이유:**
- 클릭 몇 번으로 모든게 설치됨
- 컴퓨터가 망가질 일이 없음
- 삭제도 쉬움

어떤 방법을 원하시나요? 우선 Docker 방법부터 알려드릴게요!

---

## 📦 방법 1: Docker로 간단 설치 (추천)

### 1단계: 필요한 프로그램 설치 (10분)

#### Windows 사용자
```powershell
# 1. Docker Desktop 다운로드
https://www.docker.com/products/docker-desktop/ 접속
→ "Download Docker Desktop for Windows" 클릭
→ 다운로드된 파일 실행하여 설치
→ 컴퓨터 재시작

# 2. 설치 확인 (명령 프롬프트에서)
docker --version
docker-compose --version
```

#### Mac 사용자
```bash
# 1. Docker Desktop 다운로드
https://www.docker.com/products/docker-desktop/ 접속
→ "Download Docker Desktop for Mac" 클릭
→ 설치

# 2. 설치 확인
docker --version
docker-compose --version
```

**⚠️ Docker가 제대로 실행되고 있는지 확인하세요!**
- Windows: 시스템 트레이에 Docker 고래 아이콘이 있어야 함
- Mac: 메뉴바에 Docker 고래 아이콘이 있어야 함

### 2단계: 프로젝트 파일 준비하기 (5분)

현재 `C:\Users\lauru\PythonProjects\open_deep_research` 폴더에 모든 파일이 있으니까:

```powershell
# 1. 해당 폴더로 이동
cd C:\Users\lauru\PythonProjects\open_deep_research

# 2. 파일들이 있는지 확인
dir  # Windows
# 또는
ls   # Mac/Linux

# 이런 파일들이 보여야 해요:
# - docker-compose.yml
# - backend/ 폴더
# - frontend/ 폴더
# - .env.example 파일
```

### 3단계: 환경설정 파일 만들기 (2분)

```powershell
# .env.example을 복사해서 .env 파일 만들기
copy .env.example .env    # Windows
# 또는
cp .env.example .env      # Mac/Linux
```

**.env 파일 편집 (선택사항):**
- 메모장이나 VS Code로 .env 파일 열기
- `TAVILY_API_KEY=your_tavily_api_key_here`을 실제 API 키로 바꾸기
- (API 키가 없어도 작동하지만, 검색 기능이 제한됩니다)

### 4단계: 마법의 명령어 실행! ✨

```powershell
# 모든 서비스를 한 번에 설치하고 실행
docker-compose up -d

# 뭐가 일어나는지 보고 싶다면 (-d 없이)
docker-compose up
```

**이때 뭐가 일어나나요?**
1. Docker가 필요한 프로그램들을 다운로드
2. 데이터베이스(PostgreSQL) 설치
3. Ollama AI 프로그램 설치  
4. Gemma 3 모델 다운로드 (이게 시간이 좀 걸려요, 5-10분)
5. 백엔드 서버 시작
6. 프론트엔드 웹사이트 시작

**진행 상황 확인:**
```powershell
# 로그 확인 (뭐가 일어나는지 구경하기)
docker-compose logs -f

# 특히 Ollama 로그 확인 (모델 다운로드 상황)
docker-compose logs -f ollama
```

### 5단계: 접속해서 확인하기! 🎉

모든게 설치되면:

1. **웹사이트**: http://localhost:3000
2. **API 문서**: http://localhost:8000/docs  
3. **시스템 상태**: http://localhost:8000/api/v1/health

**이런 화면이 나와야 성공:**
- 웹사이트에 "Deep Research Agent에 오신 것을 환영합니다" 메시지
- 시스템 상태에서 모든 서비스가 초록불

---

## 🔧 방법 2: 수동 설치 (개발자 경험해보기)

Docker가 안 되거나 직접 해보고 싶으시면:

### 1단계: Ollama 설치 (10분)

#### Windows
```powershell
# 1. https://ollama.ai/download 접속
# 2. Windows용 다운로드
# 3. 설치 파일 실행
# 4. 명령 프롬프트에서 확인
ollama --version
```

#### Mac
```bash
# 방법 1: 홈브류 사용 (권장)
brew install ollama

# 방법 2: 직접 다운로드
curl -fsSL https://ollama.ai/install.sh | sh
```

**AI 모델 다운로드:**
```bash
# 백그라운드로 Ollama 실행
ollama serve

# 새 터미널 창에서 모델 다운로드 (5-10분 소요)
ollama pull gemma3:12b

# 설치 확인
ollama list
```

### 2단계: Python 백엔드 설치 (15분)

```bash
# 1. Python 확인 (3.11 이상 필요)
python --version
python3 --version

# 2. Poetry 설치 (파이썬 패키지 관리자)
pip install poetry

# 3. 백엔드 폴더로 이동
cd backend

# 4. 의존성 설치
poetry install

# 5. 환경 파일 설정
copy .env.example .env    # Windows
cp .env.example .env      # Mac/Linux

# 6. 서버 실행
poetry run uvicorn src.open_deep_research.api.main:socket_app --reload --host 0.0.0.0 --port 8000
```

### 3단계: Node.js 프론트엔드 설치 (10분)

**새 터미널 창에서:**
```bash
# 1. Node.js 확인 (18 이상 필요)
node --version
npm --version

# 2. 프론트엔드 폴더로 이동  
cd frontend

# 3. 의존성 설치
npm install

# 4. 환경 파일 만들기
# .env.local 파일 생성하고 다음 내용 입력:
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# 5. 개발 서버 시작
npm run dev
```

---

## 🚨 자주 발생하는 문제들과 해결법

### 문제 1: "Docker를 찾을 수 없습니다"
```powershell
# 해결법:
# 1. Docker Desktop이 실행 중인지 확인
# 2. 컴퓨터 재시작
# 3. 명령 프롬프트를 관리자 권한으로 실행
```

### 문제 2: "포트가 이미 사용 중입니다"
```powershell
# 포트 사용 확인
netstat -ano | findstr :3000  # 프론트엔드
netstat -ano | findstr :8000  # 백엔드  
netstat -ano | findstr :11434 # Ollama

# 프로세스 종료 (PID 번호를 위 명령어에서 확인)
taskkill /PID <PID번호> /F
```

### 문제 3: "Gemma 3 모델이 다운로드되지 않음"
```bash
# 수동으로 다운로드
ollama pull gemma3:12b

# 공간 확인 (10GB 정도 필요)
# Windows: C 드라이브 용량 확인
# Mac: 홈 폴더 용량 확인
```

### 문제 4: "npm install이 실패함"
```bash
# 캐시 초기화
npm cache clean --force

# Node.js 버전 확인 (18 이상 필요)
node --version

# 다른 패키지 매니저 사용
npx yarn install
```

---

## ✅ 설치 완료 확인하기

### 1. 웹사이트 확인 ✨
http://localhost:3000 접속해서:
- [x] "Deep Research Agent에 오신 것을 환영합니다" 메시지가 보이나요?
- [x] 시스템 상태가 초록불인가요?
- [x] 질문 입력 창이 보이나요?

### 2. 기능 테스트 🧪
간단한 질문으로 테스트:
```
질문: "인공지능의 장점과 단점은?"
```

**정상 작동시:**
1. 연구 시작 버튼 클릭
2. 진행 상황 바가 움직임
3. "연구 중..." 메시지들이 바뀜
4. 최종적으로 결과 보고서 출력

### 3. 시스템 상태 확인 🔍
http://localhost:8000/api/v1/health 에서:
```json
{
  "status": "healthy",
  "ollama_available": true,    // 이게 true여야 함!
  "search_available": true     // API 키 없으면 false (괜찮음)
}
```

---

## 🎉 성공했다면...

**축하합니다! 이제 다음을 할 수 있어요:**

1. **한국어로 질문하기**
   - "기후변화의 영향은?"
   - "블록체인 기술이란?"

2. **영어로 질문하기** 
   - "What is machine learning?"
   - "Future of renewable energy?"

3. **고급 설정 사용하기**
   - 연구 깊이 조절
   - 동시 연구원 수 조절

4. **결과 다운로드하기**
   - Markdown 형식
   - 텍스트 형식

---

## 🆘 그래도 안 된다면...

**다음 정보와 함께 질문해 주세요:**

1. **운영체제**: Windows 10? Mac? 
2. **오류 메시지**: 정확한 에러 내용
3. **진행 단계**: 어느 단계에서 막혔는지
4. **로그 내용**: 
```bash
docker-compose logs    # Docker 사용시
# 또는 터미널의 오류 메시지
```

**자주 보는 곳들:**
- 🐳 [Docker 공식 문서](https://docs.docker.com/)
- 🤖 [Ollama 공식 사이트](https://ollama.ai/)  
- 📚 [프로젝트 README](./README.md)

---

## 💡 초보자를 위한 꿀팁

**1. 명령어 실행할 때:**
- Windows: `Win + R` → `cmd` 입력 → Enter
- Mac: `Cmd + Space` → `terminal` 입력 → Enter

**2. 폴더 이동할 때:**
- `cd` 뒤에 폴더 경로 입력
- 탭(Tab) 키를 누르면 자동완성됨

**3. 프로그램 종료할 때:**
- `Ctrl + C` 로 실행 중인 프로그램 종료
- Docker는 `docker-compose down`으로 전체 종료

**4. 뭔가 안 될 때:**
- 컴퓨터 재시작이 만능 해결책
- 오류 메시지를 구글에 검색
- 차근차근 단계별로 다시 해보기

**5. 개발자 도구 사용하기:**
- 브라우저에서 `F12` 키를 누르면 개발자 도구
- Console 탭에서 오류 메시지 확인 가능
- Network 탭에서 API 호출 상황 확인 가능

**6. 포트 번호 이해하기:**
- `:3000` - 프론트엔드 웹사이트
- `:8000` - 백엔드 API 서버
- `:11434` - Ollama AI 서비스
- `:5432` - PostgreSQL 데이터베이스

**7. 유용한 명령어들:**
```bash
# Docker 관련
docker-compose up -d          # 서비스 시작
docker-compose down           # 서비스 종료
docker-compose logs -f        # 로그 보기
docker ps                     # 실행 중인 컨테이너 확인

# 일반적인 문제 해결
docker system prune           # Docker 캐시 정리
docker-compose pull           # 최신 이미지 다운로드
docker-compose restart       # 서비스 재시작
```

풀스택 개발의 첫 걸음을 축하드려요! 🎊  
궁금한 점이나 문제가 있으면 언제든 물어보세요!

---

## 📚 다음 단계 학습 추천

성공적으로 설치했다면, 이제 다음을 공부해보세요:

1. **웹 개발 기초**
   - HTML, CSS, JavaScript 기본 개념
   - React 튜토리얼

2. **백엔드 개발 기초**  
   - Python 기본 문법
   - FastAPI 튜토리얼

3. **AI/ML 기초**
   - 머신러닝 개념
   - LangChain 사용법

4. **DevOps 기초**
   - Docker 사용법
   - Git 버전 관리

**추천 학습 사이트:**
- [MDN Web Docs](https://developer.mozilla.org/) - 웹 개발
- [Real Python](https://realpython.com/) - 파이썬 학습  
- [Docker 공식 튜토리얼](https://docs.docker.com/get-started/)
- [LangChain 문서](https://docs.langchain.com/)

이 프로젝트를 통해 풀스택 개발의 전체적인 흐름을 이해하셨을 거예요. 
각 부분을 조금씩 깊이 파보시면 훌륭한 개발자가 되실 수 있을 것입니다! 🚀