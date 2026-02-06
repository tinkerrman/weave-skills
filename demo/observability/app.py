"""
RAG Q&A Application

질문에 대해 지식 베이스를 검색하고 답변을 생성하는 RAG 앱입니다.

실행: python app.py
"""

from openai import OpenAI
from knowledge_base import get_most_relevant_document

client = OpenAI()


def generate_answer(question: str, model: str = "gpt-4o-mini") -> dict:
    """질문에 대한 RAG 기반 답변을 생성합니다."""
    # 1. 관련 문서 검색
    relevant_docs = get_most_relevant_document(question, top_k=2)
    context = "\n\n".join(
        f"[{doc['title']}]\n{doc['content']}" for doc in relevant_docs
    )

    # 2. LLM 호출
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "당신은 주어진 컨텍스트를 기반으로 질문에 답변하는 도우미입니다. 컨텍스트에 없는 내용은 답변하지 마세요.",
            },
            {
                "role": "user",
                "content": f"다음 컨텍스트를 참고하여 질문에 답변해주세요.\n\n### 컨텍스트:\n{context}\n\n### 질문:\n{question}\n\n### 답변:",
            },
        ],
        temperature=0.3,
    )

    return {
        "answer": response.choices[0].message.content,
        "context": context,
        "model": model,
        "sources": [doc["title"] for doc in relevant_docs],
    }


if __name__ == "__main__":
    questions = [
        "RAG 아키텍처란 무엇인가요?",
        "Python은 누가 만들었나요?",
        "벡터 데이터베이스는 무엇인가요?",
    ]

    for q in questions:
        print(f"\nQ: {q}")
        result = generate_answer(q)
        print(f"A: {result['answer']}")
        print(f"Sources: {result['sources']}")
        print("-" * 50)
