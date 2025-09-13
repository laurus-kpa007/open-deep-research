# 빠른 성능 최적화 설정

## .env 파일에서 조정 가능한 설정

```env
# 1. 더 작은 모델 사용
OLLAMA_MODEL=gemma2:2b  # 4b → 2b (2배 빠름)

# 2. 반복 횟수 줄이기 (아직 환경변수로 노출 안됨)
# backend/src/open_deep_research/models/state.py 100행
# max_iterations=6 → max_iterations=3 으로 변경

# 3. 검색 결과 수 줄이기
# backend/src/open_deep_research/core/research_workflow.py 275행
# max_results=10 → max_results=5 로 변경
```

## 코드 수정으로 즉시 개선

### 1. 반복 횟수 줄이기 (가장 효과적)
`backend/src/open_deep_research/models/state.py` 100행:
```python
max_iterations=3  # 6 → 3 (50% 단축)
```

### 2. 검색 결과 줄이기
`backend/src/open_deep_research/core/research_workflow.py` 275행:
```python
max_results=5  # 10 → 5 (검색 시간 단축)
```

### 3. 컨텍스트 길이 줄이기
`backend/src/open_deep_research/core/research_workflow.py` 294행:
```python
f"Content: {result.get('content', '')[:500]}..."  # 1000 → 500
```

## 예상 성능 향상

| 변경 사항 | 성능 향상 |
|-----------|-----------|
| max_iterations: 6→3 | 50% 단축 |
| 모델: 4b→2b | 40% 단축 |
| 검색: 10→5개 | 20% 단축 |
| 컨텍스트: 1000→500 | 10% 단축 |

**종합: 약 70% 시간 단축 가능**