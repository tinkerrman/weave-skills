"""
Evaluation Runner for RAG Q&A Demo

이 파일은 RAG 시스템 평가를 실행합니다.

스킬 적용 대상:
- /init: weave.init() 추가
- /create-eval: weave.Evaluation으로 변환

현재 상태: Weave 없이 수동 평가
"""

# ===== 스킬 적용 전 버전 =====

from rag_model import generate_answer
from eval_dataset import get_dataset
from scorers import (
    answer_length_score,
    source_citation_score,
    context_used_score,
    RelevanceScorer,
    FaithfulnessScorer,
)


def run_simple_evaluation():
    """간단한 수동 평가 실행"""
    dataset = get_dataset()
    results = []

    print("=== RAG Q&A 평가 시작 ===\n")

    for item in dataset:
        question = item["question"]
        expected = item["expected_answer"]

        print(f"Q: {question}")

        # 모델 실행
        output = generate_answer(question)
        answer = output["answer"]

        print(f"A: {answer}")
        print(f"Expected: {expected}")

        # 수동 평가
        length_result = answer_length_score(output)
        source_result = source_citation_score(output)
        context_result = context_used_score(output)

        result = {
            "question": question,
            "answer": answer,
            "expected": expected,
            "scores": {
                "length": length_result,
                "source": source_result,
                "context": context_result,
            }
        }
        results.append(result)

        print(f"Scores: length={length_result['is_valid']}, sources={source_result['has_sources']}")
        print("-" * 50)

    return results


def run_llm_judge_evaluation():
    """LLM Judge를 사용한 평가"""
    dataset = get_dataset()
    results = []

    relevance_scorer = RelevanceScorer()
    faithfulness_scorer = FaithfulnessScorer()

    print("=== LLM Judge 평가 시작 ===\n")

    for item in dataset:
        question = item["question"]

        print(f"Q: {question}")

        # 모델 실행
        output = generate_answer(question)

        # LLM Judge 평가
        relevance_result = relevance_scorer.score(question, output)
        faithfulness_result = faithfulness_scorer.score(output)

        result = {
            "question": question,
            "output": output,
            "scores": {
                "relevance": relevance_result,
                "faithfulness": faithfulness_result,
            }
        }
        results.append(result)

        print(f"Relevance: {relevance_result['relevance_score']}/5 - {relevance_result['reason']}")
        print(f"Faithful: {faithfulness_result['is_faithful']}")
        print("-" * 50)

    return results


def summarize_results(results: list[dict]) -> dict:
    """평가 결과 요약"""
    total = len(results)

    # 기본 스코어 집계
    valid_lengths = sum(1 for r in results if r["scores"].get("length", {}).get("is_valid", False))
    has_sources = sum(1 for r in results if r["scores"].get("source", {}).get("has_sources", False))

    summary = {
        "total": total,
        "valid_length_rate": valid_lengths / total if total > 0 else 0,
        "source_citation_rate": has_sources / total if total > 0 else 0,
    }

    return summary


# ===== 스킬 적용 후 버전 (참고용 주석) =====
#
# import asyncio
# import weave
# from weave import Model, Evaluation
#
# # Weave 초기화
# weave.init("rag-qa-demo")
#
# # Model 클래스 정의
# class RAGModel(Model):
#     model_name: str = "gpt-4o-mini"
#
#     @weave.op()
#     def predict(self, question: str) -> dict:
#         return generate_answer(question, model=self.model_name)
#
#
# # Evaluation 실행
# async def run_weave_evaluation():
#     model = RAGModel()
#
#     evaluation = Evaluation(
#         name="rag-qa-eval-v1",
#         dataset=qa_eval_dataset,  # weave.Dataset
#         scorers=[
#             RelevanceScorer(),
#             FaithfulnessScorer(),
#             answer_length_score,  # 함수 기반 scorer
#         ]
#     )
#
#     results = await evaluation.evaluate(model)
#     return results
#
#
# if __name__ == "__main__":
#     asyncio.run(run_weave_evaluation())


if __name__ == "__main__":
    # 간단한 평가 실행
    print("=" * 60)
    print("RAG Q&A Demo - Evaluation (Before Weave)")
    print("=" * 60)
    print()

    # 1. 간단한 평가
    results = run_simple_evaluation()

    # 2. 결과 요약
    print("\n=== 평가 결과 요약 ===")
    summary = summarize_results(results)
    print(f"Total: {summary['total']} questions")
    print(f"Valid length rate: {summary['valid_length_rate']:.1%}")
    print(f"Source citation rate: {summary['source_citation_rate']:.1%}")

    # 3. LLM Judge 평가 (선택적)
    # print("\n" + "=" * 60)
    # llm_results = run_llm_judge_evaluation()
