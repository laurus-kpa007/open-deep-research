# Deep Research Agent 웹 구현 풀스택 설계

## 1. 전체 아키텍처 개요

### 시스템 구성
```
Frontend (Next.js 14) ←→ Backend API (FastAPI/Socket.IO) ←→ Ollama LLM ←→ External APIs
         ↓                           ↓                         ↓
    Zustand Store              SQLite Database          Gemma 3:4B/12B
         ↓                           ↓
    WebSocket Client          Session Storage
```

## 2. 백엔드 아키텍처 설계

### 2.1 핵심 컴포넌트
- **FastAPI 서버**: RESTful API 및 WebSocket 지원
- **Socket.IO 통합**: 실시간 양방향 통신
- **Ollama 통합**: 로컬 LLM 모델 (Gemma 3:4B/12B) 연결
- **LangGraph Engine**: 체계적인 워크플로우 관리
- **Search Integration**: Tavily API를 통한 웹 검색
- **Session Manager**: 연구 세션 저장 및 재개
- **Report Generator**: 구조화된 보고서 생성

### 2.2 디렉토리 구조
```
backend/
├── src/open_deep_research/
│   ├── api/
│   │   ├── main.py              # FastAPI + Socket.IO 메인
│   │   ├── endpoints.py         # REST API 엔드포인트
│   │   └── websocket.py         # WebSocket 핸들러
│   ├── core/
│   │   ├── config.py            # 설정 관리
│   │   ├── workflow.py          # LangGraph 워크플로우
│   │   └── ollama_client.py     # Ollama 클라이언트
│   ├── models/
│   │   ├── research.py          # 연구 데이터 모델
│   │   └── session.py           # 세션 모델
│   ├── services/
│   │   ├── search_service.py    # Tavily 검색 서비스
│   │   ├── llm_service.py       # LLM 서비스
│   │   ├── session_service.py   # 세션 관리 서비스
│   │   └── report_service.py    # 보고서 서비스
│   ├── prompts/
│   │   └── templates.py         # 프롬프트 템플릿
│   └── utils/
│       ├── language.py          # 언어 감지/처리
│       └── formatters.py        # 출력 포맷터
├── sessions/                     # 세션 데이터 저장
├── cors_config.py               # CORS 설정
└── pyproject.toml               # Poetry 의존성 관리
```

## 3. 프론트엔드 아키텍처 설계

### 3.1 기술 스택
- **Framework**: Next.js 14 (App Router)
- **UI Library**: Tailwind CSS
- **State Management**: Zustand
- **WebSocket Client**: Socket.IO Client
- **HTTP Client**: Fetch API (내장)
- **Progress Tracking**: 커스텀 DetailedProgress 컴포넌트

### 3.2 컴포넌트 구조
```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # 루트 레이아웃
│   │   ├── page.tsx             # 메인 연구 페이지
│   │   ├── providers.tsx        # Context 프로바이더
│   │   └── globals.css          # 전역 스타일
│   ├── components/
│   │   ├── ResearchForm.tsx     # 연구 질문 입력 폼
│   │   ├── ResearchProgress.tsx # 실시간 진행 상태
│   │   ├── DetailedProgress.jsx # 세부 진행률 표시
│   │   ├── ResearchResults.tsx  # 결과 뷰어
│   │   └── HealthCheck.tsx      # 시스템 상태 체크
│   ├── hooks/
│   │   └── useResearchSession.ts # 세션 관리 훅
│   ├── lib/
│   │   └── api.ts               # API 클라이언트
│   └── store/
│       └── index.ts             # Zustand 스토어
```

### 3.3 주요 페이지 구성
1. **홈페이지**: 연구 시작 인터페이스
2. **연구 페이지**: 실시간 진행 상황 표시
3. **결과 페이지**: 생성된 보고서 표시 및 다운로드

## 4. 다국어 지원 시스템

### 4.1 언어 감지 및 처리
- **자동 감지**: 입력 텍스트 언어 자동 인식
- **응답 언어**: 질문 언어와 동일한 언어로 응답 생성
- **UI 언어**: 사용자 설정에 따른 인터페이스 언어

### 4.2 구현 방식
```typescript
// 언어 감지 서비스
interface LanguageService {
  detectLanguage(text: string): 'ko' | 'en'
  translatePrompt(text: string, targetLang: string): string
}

// 다국어 프롬프트 템플릿
const RESEARCH_PROMPTS = {
  ko: {
    research: "다음 주제에 대해 깊이 있는 연구를 수행하세요: {query}",
    summarize: "다음 내용을 요약해주세요: {content}"
  },
  en: {
    research: "Conduct deep research on the following topic: {query}",
    summarize: "Please summarize the following content: {content}"
  }
}
```

## 5. 연구 및 보고서 생성 시스템

### 5.1 연구 파이프라인
```
Query Input → Language Detection → Multi-Source Search → LLM Analysis → Report Generation
     ↓              ↓                    ↓                 ↓              ↓
한국어/영어      자동감지         Tavily, Google 등      Ollama        구조화된 보고서
```

### 5.2 보고서 구조
```json
{
  "id": "research_uuid",
  "query": "사용자 질문",
  "language": "ko|en",
  "sources": [
    {
      "title": "출처 제목",
      "url": "URL",
      "summary": "요약"
    }
  ],
  "sections": [
    {
      "title": "섹션 제목",
      "content": "내용",
      "citations": ["출처 인덱스"]
    }
  ],
  "conclusion": "결론",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 5.3 연구 프로세스 (LangGraph 워크플로우)
1. **초기화 단계**: 세션 생성 및 언어 감지
2. **계획 수립**: AI가 연구 계획 및 하위 질문 생성
3. **병렬 검색**: 여러 연구원이 동시에 정보 수집
   - Tavily API를 통한 웹 검색
   - 각 하위 질문별 독립적 조사
4. **정보 분석**: LLM을 통한 수집 정보 분석
5. **내용 통합**: 모든 정보를 종합하여 구조화
6. **보고서 작성**: 최종 보고서 생성 (인용 포함)
7. **세션 저장**: 연구 결과 및 상태 영구 저장

## 6. 기술적 구현 세부사항

### 6.1 Ollama 통합
```python
class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = os.getenv("OLLAMA_MODEL", "gemma3:4b")

    async def generate_response(
        self,
        prompt: str,
        language: str,
        temperature: float = 0.7
    ) -> str:
        # Ollama API 호출 with streaming support
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {"temperature": temperature}
                }
            ) as response:
                # Stream processing logic
                pass
```

### 6.2 API 엔드포인트 설계
```python
# RESTful API 엔드포인트
POST /api/v1/research/start      # 연구 시작
GET  /api/v1/research/{id}       # 연구 상태 조회
GET  /api/v1/research/{id}/report # 보고서 조회
GET  /api/v1/sessions            # 세션 목록 조회
GET  /api/v1/sessions/{id}       # 세션 상세 조회
DELETE /api/v1/sessions/{id}     # 세션 삭제
GET  /health                     # 헬스체크

# WebSocket 이벤트
socket.on('start_research')      # 연구 시작
socket.on('progress_update')     # 진행 상황 업데이트
socket.on('research_complete')   # 연구 완료
socket.on('error')              # 오류 처리
```

### 6.3 실시간 업데이트 (Socket.IO)
```python
# 서버 측 이벤트 발신
async def emit_progress(session_id: str, data: dict):
    await sio.emit(
        'progress_update',
        {
            'session_id': session_id,
            'stage': data['stage'],
            'percentage': data['percentage'],
            'message': data['message'],
            'details': data.get('details', {})
        },
        room=session_id
    )

# 클라이언트 측 수신
socket.on('progress_update', (data) => {
    updateProgressBar(data.percentage);
    updateStatusMessage(data.message);
    updateDetailedProgress(data.details);
});
```

## 7. 배포 및 운영

### 7.1 개발 환경
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - DATABASE_URL=sqlite:///./research_database.db
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - CORS_ORIGINS=http://localhost:3000
    volumes:
      - ./backend/sessions:/app/sessions
    depends_on:
      - ollama

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: serve

volumes:
  ollama_data:
```

### 7.2 성능 최적화
- **모델 선택**:
  - Gemma 3:4B - 빠른 응답, 적은 메모리 (권장)
  - Gemma 3:12B - 높은 품질, 더 많은 리소스
- **병렬 처리**: 여러 연구원이 동시에 작업 수행
- **세션 캐싱**: SQLite 기반 결과 캐싱
- **스트리밍**: LLM 응답 실시간 스트리밍
- **비동기 처리**: FastAPI의 async/await 활용
- **연결 풀링**: 데이터베이스 연결 최적화

## 8. 개발 로드맵

### Phase 1: 기초 인프라 (2-3주)
- Ollama 연결 및 기본 API 구조
- 프론트엔드 기본 UI 구성
- 기본 연구 파이프라인 구현

### Phase 2: 핵심 기능 (3-4주)
- 다중 소스 검색 통합
- 고급 보고서 생성
- 실시간 진행 상황 표시

### Phase 3: 최적화 및 고도화 (2-3주)
- 성능 최적화
- 사용자 경험 개선
- 다국어 지원 완성

## 핵심 특징

1. **로컬 LLM 활용**: Ollama를 통한 프라이버시 보호
2. **다국어 지원**: 한국어/영어 자동 감지 및 응답
3. **실시간 진행 표시**: Socket.IO 기반 세부 진행률 추적
4. **세션 지속성**: 연구 중단 후 재개 가능
5. **병렬 연구**: 여러 AI 연구원의 동시 작업
6. **고품질 보고서**: 인용 포함 구조화된 문서
7. **원격 접속**: 네트워크 내 여러 디바이스 지원
8. **확장 가능한 아키텍처**: LangGraph 기반 모듈화 설계

---
*참고: https://github.com/langchain-ai/open_deep_research*