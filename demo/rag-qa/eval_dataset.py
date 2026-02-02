"""
Evaluation Dataset for RAG Q&A Demo

이 파일은 RAG 시스템 평가를 위한 데이터셋을 정의합니다.

스킬 적용 대상:
- /create-dataset: weave.Dataset으로 변환 및 발행
"""

# ===== 스킬 적용 전 버전 =====

# 평가용 질문-답변 데이터셋 (일반 Python 리스트)
EVAL_DATASET = [
    {
        "id": "q1",
        "question": "Python은 누가 만들었나요?",
        "expected_answer": "귀도 반 로섬",
        "category": "기본",
    },
    {
        "id": "q2",
        "question": "FastAPI의 특징은 무엇인가요?",
        "expected_answer": "높은 성능과 자동 문서화 기능",
        "category": "프레임워크",
    },
    {
        "id": "q3",
        "question": "RAG 아키텍처란 무엇인가요?",
        "expected_answer": "검색과 생성을 결합한 아키텍처",
        "category": "AI",
    },
    {
        "id": "q4",
        "question": "벡터 데이터베이스는 무엇인가요?",
        "expected_answer": "임베딩 벡터를 저장하고 유사도 검색을 수행하는 데이터베이스",
        "category": "데이터",
    },
    {
        "id": "q5",
        "question": "프롬프트 엔지니어링이란?",
        "expected_answer": "LLM에게 원하는 출력을 얻기 위해 입력 프롬프트를 설계하는 기술",
        "category": "AI",
    },
]


def get_dataset() -> list[dict]:
    """평가 데이터셋 반환"""
    return EVAL_DATASET


def get_questions_only() -> list[str]:
    """질문만 반환"""
    return [item["question"] for item in EVAL_DATASET]


def get_by_category(category: str) -> list[dict]:
    """카테고리별 필터링"""
    return [item for item in EVAL_DATASET if item["category"] == category]


# ===== 스킬 적용 후 버전 (참고용 주석) =====
#
# import weave
#
# # weave.Dataset으로 변환
# qa_eval_dataset = weave.Dataset(
#     name="rag-qa-eval-v1",
#     rows=[
#         {
#             "question": item["question"],
#             "expected": item["expected_answer"],  # 컬럼명 통일
#             "category": item["category"],
#         }
#         for item in EVAL_DATASET
#     ]
# )
#
# # Weave에 발행 (버전 관리)
# weave.publish(qa_eval_dataset)


if __name__ == "__main__":
    # 데이터셋 확인
    dataset = get_dataset()
    print(f"Total: {len(dataset)} questions")
    print("\nSample:")
    for item in dataset[:2]:
        print(f"  Q: {item['question']}")
        print(f"  A: {item['expected_answer']}")
        print()
