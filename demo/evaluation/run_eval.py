"""
수동 평가 실행

데이터셋의 각 질문에 대해 모델을 실행하고 Scorer로 평가합니다.
현재 for 루프로 수동 실행됩니다.

실행: python run_eval.py
"""

from rag_app import generate_answer
from eval_data import EVAL_DATASET
from scorers import answer_length_score, RelevanceScorer, FaithfulnessScorer


def run_evaluation():
    relevance = RelevanceScorer()
    faithfulness = FaithfulnessScorer()
    results = []

    print("=" * 50)
    print("RAG Q&A 평가 시작")
    print("=" * 50)

    for item in EVAL_DATASET:
        question = item["question"]
        print(f"\nQ: {question}")

        output = generate_answer(question)
        print(f"A: {output['answer'][:100]}...")

        # 평가
        length = answer_length_score(output)
        rel = relevance.score(question, output)
        faith = faithfulness.score(output)

        results.append(
            {
                "question": question,
                "length_valid": length["is_valid"],
                "relevance": rel["relevance_score"],
                "faithful": faith["is_faithful"],
            }
        )

        print(
            f"  Length: {'OK' if length['is_valid'] else 'TOO SHORT'} | "
            f"Relevance: {rel['relevance_score']}/5 | "
            f"Faithful: {'Yes' if faith['is_faithful'] else 'No'}"
        )

    # 요약
    total = len(results)
    print("\n" + "=" * 50)
    print("평가 결과 요약")
    print("=" * 50)
    print(f"Total: {total}")
    print(f"Length valid: {sum(r['length_valid'] for r in results)}/{total}")
    print(f"Avg relevance: {sum(r['relevance'] for r in results) / total:.1f}/5")
    print(f"Faithful: {sum(r['faithful'] for r in results)}/{total}")


if __name__ == "__main__":
    run_evaluation()
