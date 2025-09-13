# Deep Research Agent 웹 구현 - 수정된 풀스택 설계
*GitHub 분석 기반: https://github.com/langchain-ai/open_deep_research*

## 1. 핵심 아키텍처 변경사항

### 1.1 원본 분석 결과
- **LangGraph 기반 워크플로우**: StateGraph를 사용한 다단계 연구 파이프라인
- **Supervisor-Worker 패턴**: 연구 감독자가 최대 5개 연구원에게 작업 위임
- **Pydantic 상태 관리**: 타입 안전성과 상태 지속성
- **Tavily 검색 통합**: 비동기 웹 검색 및 AI 기반 요약
- **모듈화된 프롬프트 시스템**: 단계별 전문화된 프롬프트

## 2. 수정된 기술 스택

### 2.1 Backend Stack
```python
# pyproject.toml - 핵심 의존성
[tool.poetry.dependencies]
python = "^3.11"
langgraph = "^0.2.0"           # 워크플로우 엔진
langchain-core = "^0.3.0"      # 핵심 컴포넌트  
langchain-ollama = "^0.2.0"    # Ollama 통합 (OpenAI 대신)
pydantic = "^2.8.0"            # 데이터 모델
fastapi = "^0.115.0"           # 웹 API
uvicorn = "^0.32.0"            # ASGI 서버
tavily-python = "^0.5.0"       # 검색 API
websockets = "^13.0"           # 실시간 통신
aiohttp = "^3.10.0"            # 비동기 HTTP
```

### 2.2 Frontend Stack  
```json
{
  "dependencies": {
    "next": "14.2.0",
    "react": "^18.3.0",
    "@tanstack/react-query": "^5.56.0",
    "zustand": "^4.5.0",
    "socket.io-client": "^4.8.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "latest",
    "lucide-react": "^0.446.0",
    "react-markdown": "^9.0.0",
    "next-intl": "^3.20.0"
  }
}
```

## 3. LangGraph 기반 워크플로우 설계

### 3.1 핵심 StateGraph 구조
```python
# src/core/research_workflow.py
from langgraph.graph import StateGraph, MessagesState
from typing_extensions import TypedDict

class ResearchState(MessagesState):
    """연구 상태 정의 (원본 AgentState 기반)"""
    research_question: str
    clarified_research_goal: Optional[str] = None
    research_brief: Optional[str] = None
    supervisor_requests: Optional[List[ConductResearch]] = None
    research_summaries: List[Summary] = Field(default_factory=list)
    final_report: Optional[str] = None
    language: str = "auto"  # 다국어 지원 추가
    
class ConductResearch(BaseModel):
    """연구 요청 모델 (원본과 동일)"""
    research_question: str
    description: str

# WorkFlow Graph 구성
def create_research_workflow():
    workflow = StateGraph(ResearchState)
    
    # 노드 추가 (원본 구조 유지)
    workflow.add_node("clarify_with_user", clarify_with_user_node)
    workflow.add_node("write_research_brief", write_research_brief_node) 
    workflow.add_node("research_supervisor", research_supervisor_node)
    workflow.add_node("research_individual", research_individual_node)
    workflow.add_node("compress_research", compress_research_node)
    workflow.add_node("final_report_generation", final_report_generation_node)
    
    # 엣지 및 조건부 라우팅 설정
    workflow.set_entry_point("clarify_with_user")
    workflow.add_edge("clarify_with_user", "write_research_brief")
    workflow.add_edge("write_research_brief", "research_supervisor")
    workflow.add_conditional_edges(
        "research_supervisor",
        research_supervisor_router,
        {"continue": "research_individual", "finalize": "compress_research"}
    )
    
    return workflow.compile()
```

### 3.2 Ollama 통합 (OpenAI 대신)
```python
# src/core/ollama_adapter.py
from langchain_ollama import OllamaLLM
from langchain_core.language_models import BaseLLM

class OllamaResearchLLM:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.summarization_llm = OllamaLLM(
            base_url=base_url,
            model="gemma3:12b",
            temperature=0.1
        )
        self.research_llm = OllamaLLM(
            base_url=base_url, 
            model="gemma3:12b",
            temperature=0.3
        )
        self.compression_llm = OllamaLLM(
            base_url=base_url,
            model="gemma3:12b", 
            temperature=0.2
        )

    def get_llm_for_stage(self, stage: str) -> BaseLLM:
        """연구 단계별 LLM 반환"""
        llm_map = {
            "summarization": self.summarization_llm,
            "research": self.research_llm,
            "compression": self.compression_llm,
            "final_report": self.research_llm
        }
        return llm_map.get(stage, self.research_llm)
```

## 4. 다국어 지원 시스템 (원본 확장)

### 4.1 언어별 프롬프트 시스템
```python
# src/prompts/multilingual_prompts.py
from src.prompts import (
    CLARIFICATION_PROMPT, RESEARCH_BRIEF_PROMPT,
    SUPERVISOR_PROMPT, RESEARCHER_PROMPT, COMPRESSION_PROMPT
)

class MultilingualPrompts:
    """다국어 프롬프트 관리"""
    
    PROMPTS = {
        "en": {
            "clarification": CLARIFICATION_PROMPT,  # 원본 사용
            "research_brief": RESEARCH_BRIEF_PROMPT,
            "supervisor": SUPERVISOR_PROMPT,
            "researcher": RESEARCHER_PROMPT,
            "compression": COMPRESSION_PROMPT
        },
        "ko": {
            "clarification": """당신은 연구 목표를 명확히 하는 전문가입니다.
사용자의 질문을 분석하고 다음을 제공하세요:
1. 연구 범위와 깊이 확인
2. 구체적인 연구 질문 도출
3. 필요한 정보 소스 식별

사용자 질문: {research_question}

한국어로 명확하고 구체적인 연구 계획을 제시하세요.""",
            
            "research_brief": """연구 브리프 작성 전문가로서, 다음 연구 목표에 대한 
체계적인 연구 계획을 수립하세요:

연구 목표: {clarified_research_goal}

다음 형식으로 작성하세요:
1. 연구 개요
2. 주요 연구 질문들 (3-5개)
3. 정보 수집 방법론
4. 예상 결과물

한국어로 전문적이고 체계적으로 작성하세요.""",
            
            "supervisor": """연구 감독자로서 다음 연구 브리프를 검토하고 
개별 연구원들에게 할당할 구체적인 연구 과제를 생성하세요:

연구 브리프: {research_brief}

각 연구 과제는 다음을 포함해야 합니다:
- 명확한 연구 질문
- 상세한 연구 범위
- 기대되는 결과물

최대 5개의 병렬 연구 과제를 생성하세요.""",
            
            "researcher": """전문 연구원으로서 다음 연구 과제를 수행하세요:

연구 과제: {research_task}

연구 수행 방법:
1. 관련 정보를 체계적으로 수집
2. 수집된 정보를 비판적으로 분석
3. 핵심 인사이트 도출
4. 근거 기반 결론 제시

한국어로 전문적이고 상세한 연구 결과를 제공하세요.""",
            
            "compression": """연구 통합 전문가로서 다음 개별 연구 결과들을 
종합하여 일관된 최종 보고서를 작성하세요:

개별 연구 결과들:
{research_summaries}

다음 구조로 통합하세요:
1. 연구 요약
2. 주요 발견사항
3. 상세 분석
4. 결론 및 시사점

한국어로 전문적이고 포괄적인 보고서를 작성하세요."""
        }
    }
    
    @classmethod
    def get_prompt(cls, template_name: str, language: str) -> str:
        """언어별 프롬프트 템플릿 반환"""
        return cls.PROMPTS.get(language, cls.PROMPTS["en"]).get(template_name)
```

### 4.2 자동 언어 감지
```python
# src/utils/language_detection.py
import langdetect
from typing import Literal

LanguageCode = Literal["ko", "en"]

class LanguageDetector:
    @staticmethod
    def detect_language(text: str) -> LanguageCode:
        """텍스트 언어 자동 감지"""
        try:
            detected = langdetect.detect(text)
            return "ko" if detected == "ko" else "en"
        except:
            return "en"  # 기본값
    
    @staticmethod
    def is_korean(text: str) -> bool:
        """한국어 여부 확인"""
        return LanguageDetector.detect_language(text) == "ko"
```

## 5. 웹 API 설계 (FastAPI + LangGraph)

### 5.1 주요 엔드포인트
```python
# src/api/research_api.py
from fastapi import FastAPI, WebSocket, BackgroundTasks
from langgraph.graph import CompiledGraph

app = FastAPI()

# LangGraph 워크플로우 인스턴스
research_workflow: CompiledGraph = create_research_workflow()

@app.post("/api/v1/research/start")
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """연구 시작 (비동기 처리)"""
    session_id = generate_session_id()
    
    # 언어 자동 감지
    language = LanguageDetector.detect_language(request.query)
    
    # 백그라운드에서 연구 실행
    background_tasks.add_task(
        execute_research_workflow,
        session_id=session_id,
        query=request.query,
        language=language
    )
    
    return {
        "session_id": session_id,
        "status": "started",
        "language": language
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """실시간 연구 진행 상황 스트리밍"""
    await websocket.accept()
    
    # 세션별 WebSocket 연결 관리
    websocket_manager.add_connection(session_id, websocket)
    
    try:
        while True:
            await websocket.receive_text()  # 연결 유지
    except WebSocketDisconnect:
        websocket_manager.remove_connection(session_id)

async def execute_research_workflow(session_id: str, query: str, language: str):
    """LangGraph 워크플로우 실행"""
    initial_state = ResearchState(
        messages=[HumanMessage(content=query)],
        research_question=query,
        language=language
    )
    
    # 워크플로우 실행 및 상태 스트리밍
    async for state in research_workflow.astream(
        initial_state,
        config={"recursion_limit": 50}
    ):
        # 실시간 상태 브로드캐스트
        await websocket_manager.broadcast(session_id, {
            "type": "state_update",
            "stage": get_current_stage(state),
            "progress": calculate_progress(state),
            "data": serialize_state(state)
        })
```

### 5.2 상태 관리 및 지속성
```python
# src/core/state_manager.py
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.research_session import ResearchSession as DBResearchSession

class ResearchStateManager:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def save_state(self, session_id: str, state: ResearchState):
        """상태를 데이터베이스에 저장"""
        db_session = await self.db.get(DBResearchSession, session_id)
        if not db_session:
            db_session = DBResearchSession(id=session_id)
            self.db.add(db_session)
        
        db_session.state_data = state.dict()
        db_session.last_updated = datetime.utcnow()
        await self.db.commit()
    
    async def load_state(self, session_id: str) -> Optional[ResearchState]:
        """저장된 상태 복원"""
        db_session = await self.db.get(DBResearchSession, session_id)
        if db_session and db_session.state_data:
            return ResearchState(**db_session.state_data)
        return None
```

## 6. 프론트엔드 설계 (Next.js + React Query)

### 6.1 컴포넌트 구조
```typescript
// src/components/research/ResearchInterface.tsx
'use client'

import { useResearchSession } from '@/hooks/useResearchSession'
import { ResearchProgress } from './ResearchProgress'
import { ResearchResults } from './ResearchResults'

export function ResearchInterface() {
  const [query, setQuery] = useState('')
  const { 
    startResearch, 
    sessionState, 
    isLoading,
    error 
  } = useResearchSession()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      await startResearch(query)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="연구하고 싶은 주제를 입력하세요..."
            className="flex-1 px-4 py-2 border rounded-lg"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50"
          >
            {isLoading ? '연구 중...' : '연구 시작'}
          </button>
        </div>
      </form>

      {sessionState && (
        <>
          <ResearchProgress state={sessionState} />
          {sessionState.final_report && (
            <ResearchResults report={sessionState.final_report} />
          )}
        </>
      )}
    </div>
  )
}
```

### 6.2 실시간 상태 관리 훅
```typescript
// src/hooks/useResearchSession.ts
import { useQuery, useMutation } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { io, Socket } from 'socket.io-client'

interface ResearchState {
  stage: string
  progress: number
  research_summaries: any[]
  final_report?: string
  language: 'ko' | 'en'
}

export function useResearchSession() {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sessionState, setSessionState] = useState<ResearchState | null>(null)

  // 연구 시작 뮤테이션
  const startResearchMutation = useMutation({
    mutationFn: async (query: string) => {
      const response = await fetch('/api/v1/research/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })
      return response.json()
    },
    onSuccess: (data) => {
      setSessionId(data.session_id)
      
      // WebSocket 연결 설정
      const newSocket = io(`/ws/${data.session_id}`)
      setSocket(newSocket)
      
      newSocket.on('state_update', (update) => {
        setSessionState(update.data)
      })
    }
  })

  useEffect(() => {
    return () => {
      if (socket) {
        socket.disconnect()
      }
    }
  }, [socket])

  return {
    startResearch: startResearchMutation.mutate,
    isLoading: startResearchMutation.isPending,
    error: startResearchMutation.error,
    sessionState,
    sessionId
  }
}
```

## 7. 배포 및 개발 환경

### 7.1 Docker 구성
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
      - TAVILY_API_KEY=${TAVILY_API_KEY}
    depends_on:
      - ollama
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: >
      sh -c "
        ollama serve &
        sleep 10 &&
        ollama pull gemma3:12b &&
        wait
      "

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: research_db
      POSTGRES_USER: research_user
      POSTGRES_PASSWORD: research_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  ollama_data:
  postgres_data:
```

### 7.2 개발 환경 설정
```bash
# backend/.env
OLLAMA_BASE_URL=http://localhost:11434
TAVILY_API_KEY=your_tavily_api_key
DATABASE_URL=postgresql+asyncpg://research_user:research_pass@localhost:5432/research_db

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 8. 핵심 개선사항

1. **원본 LangGraph 워크플로우 활용**: 검증된 연구 파이프라인 사용
2. **Ollama 로컬 LLM 통합**: OpenAI 대신 로컬 Gemma 2 모델 사용
3. **완전한 다국어 지원**: 한국어/영어 자동 감지 및 처리
4. **실시간 웹 인터페이스**: WebSocket 기반 진행 상황 스트리밍
5. **상태 지속성**: 데이터베이스 기반 세션 관리
6. **확장 가능한 아키텍처**: 마이크로서비스 친화적 설계

이 수정된 설계는 원본 Open Deep Research의 핵심 장점을 유지하면서 웹 환경과 Ollama 통합에 최적화되어 있습니다.

---
*참고: https://github.com/langchain-ai/open_deep_research*