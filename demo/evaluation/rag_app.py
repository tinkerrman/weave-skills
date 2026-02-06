"""
RAG Q&A Application (Weave 관찰성 적용 완료)

Observability 시나리오에서 /weave 스킬을 적용한 결과입니다:
- weave.init() 추가됨
- @weave.op 트레이싱 추가됨
- 프롬프트 버전 관리 추가됨
"""

import weave
from openai import OpenAI
from knowledge_base import get_most_relevant_document

weave.init("rag-qa-eval")
client = OpenAI()

# 버전 관리되는 프롬프트
rag_prompt = weave.MessagesPrompt(
    [
        {
            "role": "system",
            "content": "당신은 주어진 컨텍스트를 기반으로 질문에 답변하는 도우미입니다. 컨텍스트에 없는 내용은 답변하지 마세요.",
        },
        {
            "role": "user",
            "content": "다음 컨텍스트를 참고하여 질문에 답변해주세요.\n\n### 컨텍스트:\n{context}\n\n### 질문:\n{question}\n\n### 답변:",
        },
    ]
)


@weave.op()
def generate_answer(question: str, model: str = "gpt-4o-mini") -> dict:
    """질문에 대한 RAG 기반 답변을 생성합니다."""
    relevant_docs = get_most_relevant_document(question, top_k=2)
    context = "\n\n".join(
        f"[{doc['title']}]\n{doc['content']}" for doc in relevant_docs
    )

    messages = rag_prompt.format(context=context, question=question)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
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
    ]

    for q in questions:
        print(f"\nQ: {q}")
        result = generate_answer(q)
        print(f"A: {result['answer']}")
        print(f"Sources: {result['sources']}")
        print("-" * 50)
