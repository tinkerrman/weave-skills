"""
RAG Q&A Application (Weave Model 적용 완료)

Observability + Evaluation 시나리오 결과:
- weave.init + @weave.op 트레이싱 (Observability)
- weave.Model 래핑 (Evaluation)
"""

import weave
from openai import OpenAI
from knowledge_base import get_most_relevant_document

weave.init("rag-qa-production")
client = OpenAI()


class RAGModel(weave.Model):
    model_name: str = "gpt-4o-mini"
    top_k: int = 2

    @weave.op()
    def predict(self, question: str) -> dict:
        """질문에 대한 RAG 기반 답변을 생성합니다."""
        relevant_docs = get_most_relevant_document(question, top_k=self.top_k)
        context = "\n\n".join(
            f"[{doc['title']}]\n{doc['content']}" for doc in relevant_docs
        )

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "당신은 주어진 컨텍스트를 기반으로 질문에 답변하는 도우미입니다. 컨텍스트에 없는 내용은 답변하지 마세요.",
                },
                {
                    "role": "user",
                    "content": f"컨텍스트:\n{context}\n\n질문: {question}\n\n답변:",
                },
            ],
            temperature=0.3,
        )

        return {
            "answer": response.choices[0].message.content,
            "context": context,
            "sources": [doc["title"] for doc in relevant_docs],
        }
