# RAG Q&A Demo

Weave Skills 데모를 위한 RAG 기반 Q&A 시스템입니다.

[English](README.en.md)

## 파일 구조

```
rag-qa/
├── knowledge_base.py   # 문서 저장소 + 임베딩 검색
├── rag_model.py        # RAG 모델 (검색 + LLM 생성)
├── scorers.py          # 평가 Scorer들
├── eval_dataset.py     # 평가 데이터셋
├── run_eval.py         # 평가 실행 스크립트
└── requirements.txt
```

## 실행 방법

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
python run_eval.py
```

---

# Weave Skills 적용 시나리오

이 데모 프로젝트에 각 스킬을 적용하면 어떻게 되는지 보여줍니다.

---

## 1. `/init` 적용

**사용자:** "weave 초기화해줘"

**Claude 응답:**
```
## Weave 프로젝트 설정

weave.init()에 필요한 정보를 입력해주세요.

| 항목 | 설명 | 예시 |
|------|------|------|
| entity | W&B 팀 또는 사용자명 | my-team, username |
| project | 프로젝트 이름 | rag-app, chatbot-v1 |

### 입력
- entity: _______
- project: _______ (제안: rag-qa-demo)

### 초기화 위치
- 제안: run_eval.py (L1, 모듈 최상단)
```

**사용자:** "entity는 hyunwoo, project는 rag-qa-demo"

**적용 결과 (run_eval.py):**
```python
import weave

weave.init("hyunwoo/rag-qa-demo")

from rag_model import generate_answer
# ... 기존 코드
```

---

## 2. `/add-tracing` 적용

**사용자:** "트레이싱 추가해줘"

**Claude 응답:**
```
## 코드베이스 분석 결과

### knowledge_base.py
| 함수명 | 위치 | 설명 |
|--------|------|------|
| get_embedding() | L50-L74 | 텍스트 임베딩 생성 |
| get_most_relevant_document() | L84-L110 | 문서 검색 |
| cosine_similarity() | L77-L81 | 벡터 유사도 계산 |

### rag_model.py
| 함수명 | 위치 | 설명 |
|--------|------|------|
| generate_answer() | L21-L70 | 메인 RAG 함수 |
| _build_prompt() | L72-L83 | 프롬프트 생성 |

## 트레이싱 추가 제안

| # | 함수 | 이유 | 추천 |
|---|------|------|------|
| 1 | generate_answer() | 메인 LLM 호출 | ⭐⭐⭐ |
| 2 | get_embedding() | 임베딩 API 호출 | ⭐⭐⭐ |
| 3 | get_most_relevant_document() | 문서 검색 | ⭐⭐⭐ |

### 제외된 함수
- cosine_similarity() - 단순 수학 연산
- _build_prompt() - private 유틸리티

수정하시겠습니까? (기본: 1, 2, 3번 적용)
```

**사용자:** "ㅇㅇ"

**Claude 응답:**
```
## @weave.op() 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| name | 대시보드 표시 이름 | @weave.op(name="llm-call") |

커스텀 이름을 지정하시겠습니까?

| # | 함수 | 기본 이름 | 커스텀 이름 |
|---|------|-----------|------------|
| 1 | generate_answer | generate_answer | _______ |
| 2 | get_embedding | get_embedding | _______ |
| 3 | get_most_relevant_document | get_most_relevant_document | _______ |

비워두면 함수 이름 그대로 사용합니다.
```

**사용자:** "기본으로"

**적용 결과 (rag_model.py):**
```python
import weave
from openai import OpenAI

client = OpenAI()

@weave.op()
def generate_answer(question: str, model: str = "gpt-4o-mini") -> dict:
    relevant_docs = get_most_relevant_document(question, top_k=2)
    # ... 기존 코드
```

**적용 결과 (knowledge_base.py):**
```python
import weave
import numpy as np
from openai import OpenAI

@weave.op()
def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    # ... 기존 코드

@weave.op()
def get_most_relevant_document(query: str, top_k: int = 1) -> list[dict]:
    # ... 기존 코드
```

---

## 3. `/create-dataset` 적용

**사용자:** "평가 데이터셋 만들어줘"

**Claude 응답:**
```
## 기존 데이터 분석

파일: eval_dataset.py
변수: EVAL_DATASET (5개 항목)

### 컬럼 구조
| 컬럼 | 타입 | 예시 |
|------|------|------|
| question | str | "Python은 누가 만들었나요?" |
| expected_answer | str | "귀도 반 로섬" |
| category | str | "기본" |

### 컬럼 매핑 제안
- question → question (모델 입력)
- expected_answer → expected (정답, Scorer용)
- category → category (메타데이터)

weave.Dataset으로 변환할까요?
```

**사용자:** "ㅇㅇ"

**적용 결과 (eval_dataset.py에 추가):**
```python
import weave

# 기존 EVAL_DATASET 유지

# weave.Dataset으로 변환
qa_eval_dataset = weave.Dataset(
    name="rag-qa-eval-v1",
    rows=[
        {
            "question": item["question"],
            "expected": item["expected_answer"],
            "category": item["category"],
        }
        for item in EVAL_DATASET
    ]
)

# Weave에 발행 (선택)
# weave.publish(qa_eval_dataset)
```

---

## 4. `/create-scorer` 적용

**사용자:** "hallucination 체크하는 scorer 만들어줘"

**Claude 응답:**
```
## Scorer 생성

어떤 것을 평가하고 싶으신가요?
→ Hallucination (출처 없는 내용 검출)

## Scorer 타입 선택

| 타입 | 추천 상황 |
|------|-----------|
| Built-in HallucinationFreeScorer | 빠른 구현 (추천) |
| 커스텀 LLM Judge | 세부 조정 필요시 |

Built-in Scorer를 사용할까요?
```

**사용자:** "ㅇㅇ"

**적용 결과 (scorers.py에 추가):**
```python
from weave.scorers import HallucinationFreeScorer

# Built-in Scorer
hallucination_scorer = HallucinationFreeScorer()
```

---

## 5. `/create-eval` 적용

**사용자:** "평가 파이프라인 만들어줘"

**Claude 응답:**
```
## 평가 구성요소 분석

### 발견됨
- Dataset: qa_eval_dataset ✅
- Scorers: HallucinationFreeScorer, RelevanceScorer ✅

### 필요함
- Model: weave.Model 클래스 없음 ⚠️

기존 generate_answer() 함수를 weave.Model로 래핑할까요?
```

**사용자:** "ㅇㅇ"

**적용 결과 (run_eval.py 전체 변환):**
```python
import asyncio
import weave
from weave import Model, Evaluation
from weave.scorers import HallucinationFreeScorer

from rag_model import generate_answer
from eval_dataset import qa_eval_dataset
from scorers import RelevanceScorer

weave.init("hyunwoo/rag-qa-demo")


class RAGModel(Model):
    """Weave Model 기반 RAG 시스템"""

    model_name: str = "gpt-4o-mini"

    @weave.op()
    def predict(self, question: str) -> dict:
        return generate_answer(question, model=self.model_name)


async def run_weave_evaluation():
    model = RAGModel()

    evaluation = Evaluation(
        name="rag-qa-eval-v1",
        dataset=qa_eval_dataset,
        scorers=[
            HallucinationFreeScorer(),
            RelevanceScorer(),
        ]
    )

    results = await evaluation.evaluate(model)

    print("=== 평가 완료 ===")
    print(f"결과: {results}")
    print(f"대시보드: https://wandb.ai/hyunwoo/rag-qa-demo")

    return results


if __name__ == "__main__":
    asyncio.run(run_weave_evaluation())
```

---

## 최종 결과

모든 스킬 적용 후 가능해지는 것들:

| 기능 | 설명 |
|------|------|
| 트레이스 시각화 | 모든 LLM 호출, 임베딩 생성, 문서 검색 추적 |
| 평가 결과 대시보드 | Scorer별 점수, 실패 케이스 분석 |
| 모델 버전 관리 | RAGModel 파라미터 변경 시 자동 버전 생성 |
| 데이터셋 버전 관리 | 평가 데이터 변경 추적 |

**W&B Weave 대시보드:** https://wandb.ai/weave
