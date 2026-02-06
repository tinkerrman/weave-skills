# Scenario: Observability (관찰성 구축)

Weave 없는 RAG 앱에 관찰성을 추가합니다.

## 현재 상태

- `app.py` — RAG Q&A 앱 (Weave 없음)
- `knowledge_base.py` — 문서 저장소 + 임베딩 검색

## 적용할 스킬

| 순서 | 스킬 | 설명 |
|------|------|------|
| 1 | `/weave init` | Weave 프로젝트 초기화 |
| 2 | `/weave add-tracing` | 함수에 `@weave.op` 트레이싱 추가 |
| 3 | `/weave create-prompt` | 하드코딩된 프롬프트를 `MessagesPrompt`로 버전 관리 |

## 데모 순서

```bash
# 1. 먼저 현재 상태 확인
python app.py

# 2. Claude Code에서 /weave 스킬 적용
#    → init, add-tracing, create-prompt 순서로 적용

# 3. 적용 후 다시 실행하여 W&B 대시보드에서 트레이스 확인
python app.py
```

## 기대 결과

- `weave.init()` 추가
- `generate_answer()`, `get_embedding()`, `get_most_relevant_document()`에 `@weave.op` 추가
- 하드코딩 프롬프트 → `weave.MessagesPrompt` + `weave.publish()`
- W&B Weave 대시보드에서 호출 트레이스 확인 가능
