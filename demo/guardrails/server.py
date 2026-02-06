"""
프로덕션 RAG 서버

질문을 받아 RAG 모델로 답변을 생성합니다.
현재 답변의 품질이나 안전성을 검증하는 로직이 없습니다.

실행: python server.py
"""

from rag_app import RAGModel

model = RAGModel()


def handle_question(question: str) -> dict:
    """
    질문을 처리하고 답변을 반환합니다.

    현재 문제점:
    - 환각(hallucination) 검증 없이 바로 반환
    - 답변 품질 모니터링 없음
    - 부적절한 답변 필터링 없음
    """
    result = model.predict(question)
    return {
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"],
    }


if __name__ == "__main__":
    questions = [
        "RAG 아키텍처란 무엇인가요?",
        "Python은 누가 만들었나요?",
        "양자 컴퓨터의 원리는?",  # 지식 베이스에 없는 질문 → 환각 가능성
    ]

    print("=" * 50)
    print("프로덕션 RAG 서버 테스트")
    print("=" * 50)

    for q in questions:
        print(f"\nQ: {q}")
        result = handle_question(q)
        print(f"A: {result['answer']}")
        print(f"Sources: {result['sources']}")
        print("-" * 50)
