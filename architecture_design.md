# Deep Research Agent 웹 구현 풀스택 설계

## 1. 전체 아키텍처 개요

### 시스템 구성
```
Frontend (React/Next.js) ←→ Backend API (FastAPI/Python) ←→ Ollama LLM ←→ External APIs
                                         ↓
                                   Database (SQLite/PostgreSQL)
```

## 2. 백엔드 아키텍처 설계

### 2.1 핵심 컴포넌트
- **FastAPI 서버**: RESTful API 제공
- **Ollama 통합**: 로컬 LLM 모델 (Gemma 2:12B) 연결
- **Research Engine**: 다단계 연구 프로세스 관리
- **Search Integration**: Tavily API 등 외부 검색 서비스
- **Report Generator**: 구조화된 보고서 생성

### 2.2 디렉토리 구조
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── research.py      # 연구 요청 처리
│   │   │   ├── reports.py       # 보고서 관리
│   │   │   └── health.py        # 헬스체크
│   ├── core/
│   │   ├── config.py            # 설정 관리
│   │   ├── ollama_client.py     # Ollama 연결 클라이언트
│   │   └── research_engine.py   # 핵심 연구 엔진
│   ├── models/
│   │   ├── request.py           # 요청 모델
│   │   └── response.py          # 응답 모델
│   ├── services/
│   │   ├── search_service.py    # 검색 서비스
│   │   ├── llm_service.py       # LLM 서비스
│   │   └── report_service.py    # 보고서 서비스
│   └── utils/
│       ├── language_detector.py # 언어 감지
│       └── formatters.py        # 출력 포맷터
```

## 3. 프론트엔드 아키텍처 설계

### 3.1 기술 스택
- **Framework**: Next.js 14 (App Router)
- **UI Library**: Tailwind CSS + Shadcn/ui
- **State Management**: Zustand
- **HTTP Client**: Axios
- **국제화**: next-i18next

### 3.2 컴포넌트 구조
```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # 루트 레이아웃
│   │   ├── page.tsx             # 홈페이지
│   │   └── research/
│   │       ├── page.tsx         # 연구 페이지
│   │       └── [id]/page.tsx    # 연구 결과 페이지
│   ├── components/
│   │   ├── ui/                  # shadcn/ui 컴포넌트
│   │   ├── research/
│   │   │   ├── QueryForm.tsx    # 질문 입력 폼
│   │   │   ├── ProgressBar.tsx  # 진행 상태
│   │   │   └── ResultViewer.tsx # 결과 뷰어
│   │   └── layout/
│   │       ├── Header.tsx       # 헤더
│   │       └── Sidebar.tsx      # 사이드바
│   ├── hooks/
│   │   ├── useResearch.ts       # 연구 훅
│   │   └── useLanguage.ts       # 언어 훅
│   └── store/
│       └── researchStore.ts     # 상태 관리
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

### 5.3 연구 프로세스
1. **초기 검색**: 키워드 기반 다중 소스 검색
2. **정보 수집**: 검색 결과 요약 및 분석
3. **심화 연구**: LLM을 통한 추가 질문 생성 및 검색
4. **내용 통합**: 수집된 정보의 통합 및 구조화
5. **보고서 작성**: 최종 보고서 생성 및 포맷팅

## 6. 기술적 구현 세부사항

### 6.1 Ollama 통합
```python
class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "gemma2:12b"
    
    async def generate_response(self, prompt: str, language: str) -> str:
        # Ollama API 호출 로직
        pass
```

### 6.2 API 엔드포인트 설계
```python
# 주요 API 엔드포인트
POST /api/v1/research/start      # 연구 시작
GET  /api/v1/research/{id}       # 연구 상태 조회
GET  /api/v1/research/{id}/report # 보고서 조회
POST /api/v1/research/{id}/export # 보고서 내보내기
```

### 6.3 실시간 업데이트
- **WebSocket**: 연구 진행 상황 실시간 전달
- **Server-Sent Events**: 브라우저 호환성을 위한 대안

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
    depends_on:
      - ollama
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
```

### 7.2 성능 최적화
- **캐싱**: Redis를 통한 검색 결과 캐싱
- **비동기 처리**: 장시간 소요 작업의 백그라운드 처리
- **리소스 관리**: Ollama 모델 로딩 최적화

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
2. **다국어 지원**: 한국어/영어 질문 및 답변
3. **실시간 피드백**: 연구 진행 상황 실시간 표시
4. **고품질 보고서**: 다양한 소스 기반 구조화된 문서
5. **확장 가능한 아키텍처**: 모듈화된 설계로 기능 확장 용이

---
*참고: https://github.com/langchain-ai/open_deep_research*