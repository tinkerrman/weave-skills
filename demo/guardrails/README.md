# Scenario: Production Guardrails (프로덕션 가드레일)

프로덕션 RAG 서버에 가드레일과 품질 모니터링을 추가합니다.

## 현재 상태

- `rag_app.py` — `weave.Model` 적용 완료 (Evaluation 시나리오 결과)
- `scorers.py` — `weave.Scorer` 적용 완료 (Evaluation 시나리오 결과)
- `server.py` — 프로덕션 엔드포인트 (가드레일 없음)
- `knowledge_base.py` — 문서 저장소

## 적용할 스킬

| 순서 | 스킬 | 대상 파일 | 설명 |
|------|------|-----------|------|
| 1 | `/weave add-guardrails` | `server.py` | `FaithfulnessScorer`를 블로킹 가드레일로 적용 |

## 데모 순서

```bash
# 1. 현재 상태 확인 - 가드레일 없이 모든 답변 그대로 반환
python server.py
# → "양자 컴퓨터" 질문에 환각 답변이 그대로 나옴

# 2. Claude Code에서 /weave add-guardrails 적용
#    → server.py에 call.apply_scorer() 가드레일 추가

# 3. 적용 후 실행 - 환각 답변이 차단되는지 확인
python server.py
```

## 기대 결과

- `model.predict.call()` → `(result, call)` 패턴으로 변경
- `call.apply_scorer(FaithfulnessScorer())` → 환각 검출
- 환각 감지 시 답변 차단 또는 경고
- W&B Weave 대시보드에서 가드레일 스코어 확인 가능
