# Scenario: Evaluation Pipeline (평가 파이프라인)

트레이싱이 적용된 RAG 앱에 Weave 평가 파이프라인을 구축합니다.

## 현재 상태

- `rag_app.py` — Weave 트레이싱 적용 완료 (Observability 시나리오 결과)
- `scorers.py` — 일반 Python 클래스 Scorer (Weave 미적용)
- `eval_data.py` — 일반 Python 리스트 데이터셋
- `run_eval.py` — for 루프 수동 평가

## 적용할 스킬

| 순서 | 스킬 | 대상 파일 | 설명 |
|------|------|-----------|------|
| 1 | `/weave create-model` | `rag_app.py` | `generate_answer()`를 `weave.Model` 클래스로 래핑 |
| 2 | `/weave create-dataset` | `eval_data.py` | `EVAL_DATASET`을 `weave.Dataset`으로 변환 |
| 3 | `/weave create-scorer` | `scorers.py` | `RelevanceScorer`를 `weave.Scorer`로 변환 |
| 4 | `/weave create-eval` | `run_eval.py` | for 루프를 `weave.Evaluation`으로 교체 |

## 데모 순서

```bash
# 1. 현재 수동 평가 확인
python run_eval.py

# 2. Claude Code에서 /weave 스킬 적용
#    → create-model, create-dataset, create-scorer, create-eval 순서로 적용

# 3. 적용 후 평가 실행하여 W&B 대시보드에서 결과 확인
python run_eval.py
```

## 기대 결과

- `RAGModel(weave.Model)` 클래스 생성 → 모델 버전 관리
- `weave.Dataset` → 데이터셋 발행 및 버전 관리
- `weave.Scorer` 서브클래스 → 스코어러 자동 추적
- `weave.Evaluation` → 한 줄로 평가 실행, 대시보드에서 결과 비교
