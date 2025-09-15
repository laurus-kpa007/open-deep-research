# System Architecture - Open Deep Research Agent

## 목차
1. [시스템 개요](#시스템-개요)
2. [전체 아키텍처](#전체-아키텍처)
3. [컴포넌트 구성](#컴포넌트-구성)
4. [데이터 플로우](#데이터-플로우)
5. [워크플로우 상세](#워크플로우-상세)
6. [기술 스택](#기술-스택)
7. [배포 아키텍처](#배포-아키텍처)

## 시스템 개요

Open Deep Research Agent는 LangGraph 기반의 AI 연구 에이전트로, 복잡한 연구 질문에 대해 단계별 분석과 종합을 수행합니다.

### 주요 특징
- 🤖 **Ollama 통합**: 로컬 LLM을 활용한 프라이버시 보장 (Gemma 3:4B/12B)
- 🔄 **LangGraph 워크플로우**: 체계적인 연구 프로세스 자동화
- 🌐 **다국어 지원**: 한국어, 영어 자동 감지 및 응답
- ⚡ **실시간 진행상황**: WebSocket/Socket.IO를 통한 세부 진행률 업데이트
- 💾 **세션 지속성**: SQLite 기반 연구 세션 저장 및 재개
- 🔍 **Tavily 검색**: 웹 검색을 통한 최신 정보 수집
- 🔄 **원격 접속**: 네트워크 내 여러 디바이스에서 접속 가능

## 전체 아키텍처

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Next.js 14 UI<br/>React + TypeScript]
        WS[Socket.IO Client]
        ZS[Zustand Store]
    end

    subgraph "Backend Layer"
        API[FastAPI Server]
        SIO[Socket.IO Server]
        CORS[CORS Handler]
    end

    subgraph "Core Engine"
        WF[Research Workflow<br/>LangGraph]
        OC[Ollama Client]
        SS[Search Service<br/>Tavily API]
        SM[Session Manager]
    end

    subgraph "External Services"
        OL[Ollama Server<br/>Gemma 3:4B/12B]
        TA[Tavily API<br/>Web Search]
    end

    subgraph "Data Layer"
        DB[(SQLite DB<br/>Sessions)]
        SF[Session Files<br/>JSON Storage]
        CACHE[Cache<br/>Search Results]
    end

    UI <--> API
    UI <--> SIO
    UI <--> ZS

    API --> CORS
    API --> WF
    WF --> OC
    WF --> SS
    WF --> SM

    OC --> OL
    SS --> TA

    SM --> DB
    SM --> SF
    SS --> CACHE

    style UI fill:#e1f5fe
    style API fill:#fff3e0
    style WF fill:#f3e5f5
    style OL fill:#e8f5e9
    style DB fill:#fce4ec
```

## 컴포넌트 구성

### Frontend Components

```mermaid
graph LR
    subgraph "React Components"
        App[App.tsx]
        RF[ResearchForm.tsx]
        DP[DetailedProgress.jsx]
        RR[ResearchResults.tsx]
        HC[HealthCheck.tsx]
        RP[ResearchProgress.tsx]
    end

    subgraph "Hooks & Utils"
        URS[useResearchSession.ts]
        API[api.ts<br/>API Client]
    end

    subgraph "State Management"
        ZS[Zustand Store]
        RS[Research State]
        PS[Progress State]
        SS[Session State]
    end

    App --> RF
    App --> DP
    App --> RR
    URS --> API
    URS --> ZS
    App --> RR
    App --> HC
    
    RF --> URS
    RP --> WSH
    URS --> RS
    WSH --> PS
```

### Backend Architecture

```mermaid
graph TD
    subgraph "API Layer"
        MAIN[main.py]
        ROUTES[API Routes]
        WS_EP[WebSocket Endpoints]
    end
    
    subgraph "Core Modules"
        RW[research_workflow.py]
        OC[ollama_client.py]
        SS[search_service.py]
    end
    
    subgraph "Models"
        STATE[state.py<br/>ResearchState]
        REQ[Request Models]
        RES[Response Models]
    end
    
    subgraph "Utils"
        LD[language_detector.py]
        MP[multilingual_prompts.py]
    end
    
    MAIN --> ROUTES
    MAIN --> WS_EP
    ROUTES --> RW
    RW --> OC
    RW --> SS
    RW --> STATE
    RW --> LD
    RW --> MP
```

## 데이터 플로우

### Research Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Workflow
    participant Ollama
    participant Tavily
    
    User->>Frontend: Submit Research Query
    Frontend->>API: POST /research/start
    API->>API: Create Session
    API-->>Frontend: Session ID
    
    Frontend->>API: WebSocket Connect
    
    API->>Workflow: Start Research
    
    loop Research Process
        Workflow->>API: Progress Update
        API-->>Frontend: WebSocket Event
        Frontend-->>User: Show Progress
        
        Workflow->>Ollama: Generate Response
        Ollama-->>Workflow: AI Response
        
        Workflow->>Tavily: Search Web
        Tavily-->>Workflow: Search Results
    end
    
    Workflow->>API: Final Report
    API-->>Frontend: Complete Event
    Frontend-->>User: Display Results
```

## 워크플로우 상세

### LangGraph Research Workflow

```mermaid
graph TD
    Start([Start]) --> CWU[Clarify with User]
    CWU --> WRB[Write Research Brief]
    WRB --> RS[Research Supervisor]
    
    RS --> CheckTasks{Tasks Complete?}
    CheckTasks -->|No| RI[Research Individual]
    RI --> RS
    CheckTasks -->|Yes| CR[Compress Research]
    
    CR --> FRG[Final Report Generation]
    FRG --> End([End])
    
    style Start fill:#4caf50
    style End fill:#f44336
    style CWU fill:#2196f3
    style WRB fill:#ff9800
    style RS fill:#9c27b0
    style RI fill:#00bcd4
    style CR fill:#ffeb3b
    style FRG fill:#8bc34a
```

### State Management

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> Clarifying: Start Research
    Clarifying --> Briefing: Goal Clarified
    Briefing --> Planning: Brief Written
    Planning --> Researching: Tasks Assigned
    Researching --> Researching: More Tasks
    Researching --> Synthesizing: All Tasks Done
    Synthesizing --> Finalizing: Compressed
    Finalizing --> Completed: Report Ready
    Completed --> [*]
    
    Clarifying --> Error: Exception
    Briefing --> Error: Exception
    Planning --> Error: Exception
    Researching --> Error: Exception
    Synthesizing --> Error: Exception
    Finalizing --> Error: Exception
    Error --> [*]
```

## 기술 스택

### Backend Stack
```mermaid
graph LR
    subgraph "Python Backend"
        FA[FastAPI<br/>v0.115.14]
        LG[LangGraph<br/>Latest]
        LC[LangChain Core<br/>v0.3.76]
        UV[Uvicorn<br/>ASGI Server]
    end
    
    subgraph "AI/ML"
        OLL[Ollama<br/>Local LLM]
        TAV[Tavily<br/>Search API]
    end
    
    subgraph "Data"
        SQL[SQLAlchemy<br/>v2.0.43]
        PYD[Pydantic<br/>v2.x]
    end
```

### Frontend Stack
```mermaid
graph LR
    subgraph "React Ecosystem"
        NX[Next.js<br/>v14.2.32]
        RT[React<br/>v18]
        TS[TypeScript<br/>v5]
    end
    
    subgraph "Styling"
        TW[Tailwind CSS<br/>v3.4]
        SUI[Shadcn/ui]
    end
    
    subgraph "Communication"
        SIO[Socket.IO Client]
        AX[Axios]
    end
```

## 배포 아키텍처

### Docker Deployment

```mermaid
graph TB
    subgraph "Docker Network"
        subgraph "Backend Container"
            BACK[Python App<br/>Port 8000]
        end
        
        subgraph "Frontend Container"
            FRONT[Next.js App<br/>Port 3000]
        end
        
        subgraph "Ollama Container"
            OLLAMA[Ollama Server<br/>Port 11434]
        end
    end
    
    subgraph "Host System"
        NGINX[Nginx<br/>Reverse Proxy]
        VOL[Docker Volumes<br/>Data Persistence]
    end
    
    NGINX --> FRONT
    NGINX --> BACK
    BACK --> OLLAMA
    VOL --> BACK
```

### Environment Configuration

```yaml
Services:
  Backend:
    - Port: 8000
    - Environment:
      - OLLAMA_BASE_URL
      - TAVILY_API_KEY
      - DATABASE_URL
  
  Frontend:
    - Port: 3000
    - Environment:
      - NEXT_PUBLIC_API_URL
      - NEXT_PUBLIC_WS_URL
  
  Ollama:
    - Port: 11434
    - Models:
      - gemma3:12b
      - qwen3:8b
      - gemma3:4b
```

## Security Considerations

```mermaid
graph LR
    subgraph "Security Layers"
        CORS[CORS Policy]
        AUTH[JWT Auth<br/>Optional]
        VAL[Input Validation]
        RATE[Rate Limiting]
    end
    
    subgraph "Data Protection"
        ENV[Environment Variables]
        SEC[Secret Management]
        LOG[Secure Logging]
    end
    
    CORS --> API
    AUTH --> API
    VAL --> API
    RATE --> API
    
    ENV --> Configuration
    SEC --> Configuration
    LOG --> Monitoring
```

## Performance Optimization

### Caching Strategy
- Search results: 15분 캐시
- LLM responses: Session-based 캐시
- Static assets: CDN 캐싱

### Scaling Options
1. **Horizontal Scaling**: Multiple API instances
2. **Load Balancing**: Nginx/HAProxy
3. **Queue System**: Celery for async tasks
4. **Database**: PostgreSQL for production

## Monitoring & Logging

```mermaid
graph TD
    subgraph "Monitoring Stack"
        APP[Application]
        LOG[Logging<br/>Python Logger]
        MET[Metrics<br/>Prometheus]
        TRACE[Tracing<br/>OpenTelemetry]
    end
    
    subgraph "Visualization"
        GRAF[Grafana]
        ELK[ELK Stack]
    end
    
    APP --> LOG
    APP --> MET
    APP --> TRACE
    
    LOG --> ELK
    MET --> GRAF
    TRACE --> GRAF
```

## Future Enhancements

1. **Multi-Agent Collaboration**: 여러 연구원 에이전트 협업
2. **Knowledge Graph**: 연구 결과 지식 그래프 구축
3. **Custom Models**: 도메인별 특화 모델 지원
4. **Real-time Collaboration**: 실시간 협업 기능
5. **Export Options**: PDF, Markdown, Word 내보내기

---

*Last Updated: 2025-09-13*