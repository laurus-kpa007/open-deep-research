# 성능 최적화 가이드

## 현재 문제
- 2명 이상 동시 접속 시 매우 느려짐
- Ollama가 한 번에 하나의 요청만 처리

## 원인 분석

### 1. Ollama 병목 현상
- **단일 모델 인스턴스**: deepseek-r1:8b 모델 하나만 실행 중
- **동기식 처리**: 한 사용자의 요청이 끝나야 다음 사용자 처리
- **Context Length**: 4096 토큰 제한

### 2. 시스템 구조 문제
- 각 연구 단계마다 여러 LLM 호출 (최소 6-10회)
- 동시 세션 처리 불가

## 즉시 적용 가능한 해결책

### 1. Ollama 동시 처리 설정
```bash
# Windows 환경변수 설정 (관리자 권한 CMD)
setx OLLAMA_NUM_PARALLEL 4
setx OLLAMA_MAX_LOADED_MODELS 2

# 또는 PowerShell
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_PARALLEL", "4", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_MAX_LOADED_MODELS", "2", "User")

# Ollama 재시작
ollama serve
```

### 2. 더 작은 모델 사용
```bash
# 더 빠른 모델로 변경 (.env 파일)
OLLAMA_MODEL=gemma2:2b  # 2B 파라미터 (더 빠름)
# 또는
OLLAMA_MODEL=qwen2.5:3b  # 3B 파라미터
```

### 3. 연구 깊이 조정
`.env` 파일에서:
```env
# 연구 반복 횟수 줄이기
MAX_ITERATIONS=3  # 기본값 6에서 3으로
MAX_RESEARCHERS=1  # 동시 연구원 수 제한
```

## 코드 레벨 최적화

### 1. 캐싱 추가 (backend/src/open_deep_research/core/ollama_client.py)
```python
from functools import lru_cache
import hashlib

class OllamaClient:
    def __init__(self):
        self.cache = {}

    @lru_cache(maxsize=100)
    async def generate_cached(self, prompt_hash: str, stage: str):
        # 동일한 프롬프트는 캐시에서 반환
        if prompt_hash in self.cache:
            return self.cache[prompt_hash]
        result = await self.generate(prompt, stage)
        self.cache[prompt_hash] = result
        return result
```

### 2. 배치 처리
여러 요청을 모아서 처리하도록 수정

### 3. 비동기 큐 시스템
```python
import asyncio
from asyncio import Queue

class RequestQueue:
    def __init__(self):
        self.queue = Queue()
        self.workers = []

    async def process_requests(self):
        while True:
            request = await self.queue.get()
            # 처리
```

## 임시 해결책 (즉시 적용)

### 1. 사용자별 시간차 두기
- 동시에 연구 시작하지 않도록 안내
- 한 명씩 순차적으로 실행

### 2. 연구 설정 조정
프론트엔드에서:
- Depth: "shallow" 선택 (빠른 연구)
- Max Researchers: 1로 설정

### 3. Ollama 서버 분리
```bash
# 다른 포트에서 추가 Ollama 실행
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

## 장기 해결책

### 1. 로드 밸런서 구성
여러 Ollama 인스턴스를 실행하고 부하 분산

### 2. GPU 가속
CUDA 지원 GPU 사용 시 성능 대폭 향상

### 3. 클라우드 API 사용
- OpenAI API
- Anthropic Claude API
- Google Gemini API

### 4. Redis 큐 시스템
Celery + Redis로 비동기 작업 큐 구현

## 모니터링

### Ollama 상태 확인
```bash
# 실행 중인 모델 확인
curl http://192.168.0.244:11434/api/ps

# 모델 정보
curl http://192.168.0.244:11434/api/show -d '{"name":"deepseek-r1:8b"}'
```

### 시스템 리소스 확인
```bash
# CPU/메모리 사용률
tasklist | findstr ollama
```

## 권장 설정

### 개발/테스트용
```env
OLLAMA_MODEL=gemma2:2b
MAX_ITERATIONS=3
MAX_RESEARCHERS=1
OLLAMA_NUM_PARALLEL=2
```

### 프로덕션용
- 여러 Ollama 서버 인스턴스
- 로드 밸런서
- Redis 캐시
- 작업 큐 시스템