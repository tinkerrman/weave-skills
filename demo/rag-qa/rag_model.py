"""
RAG Model for Q&A Demo

이 파일은 RAG 기반 Q&A 모델을 구현합니다.
- 문서 검색 + LLM 답변 생성

스킬 적용 대상:
- /add-tracing: generate_answer(), _build_prompt()
- /init: weave.init() 추가 필요
"""

from openai import OpenAI

from knowledge_base import get_most_relevant_document

client = OpenAI()


# ===== 스킬 적용 전 버전 =====

def generate_answer(question: str, model: str = "gpt-4o-mini") -> dict:
    """
    질문에 대한 답변을 생성합니다.

    1. 관련 문서 검색
    2. 컨텍스트와 함께 LLM에 질문
    3. 답변 반환

    Args:
        question: 사용자 질문
        model: 사용할 LLM 모델

    Returns:
        dict: answer, context, model 정보
    """
    # 1. 관련 문서 검색
    relevant_docs = get_most_relevant_document(question, top_k=2)
    context = "\n\n".join([
        f"[{doc['title']}]\n{doc['content']}"
        for doc in relevant_docs
    ])

    # 2. 프롬프트 구성
    prompt = _build_prompt(question, context)

    # 3. LLM 호출
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "당신은 주어진 컨텍스트를 기반으로 질문에 답변하는 도우미입니다. 컨텍스트에 없는 내용은 답변하지 마세요."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "context": context,
        "model": model,
        "sources": [doc["title"] for doc in relevant_docs]
    }


def _build_prompt(question: str, context: str) -> str:
    """질문과 컨텍스트를 결합하여 프롬프트를 생성합니다."""
    return f"""다음 컨텍스트를 참고하여 질문에 답변해주세요.

### 컨텍스트:
{context}

### 질문:
{question}

### 답변:"""


# ===== 스킬 적용 후 버전 (참고용 주석) =====
#
# import weave
# from weave import Model
#
# class RAGModel(Model):
#     """Weave Model 기반 RAG 시스템"""
#
#     model_name: str = "gpt-4o-mini"
#     top_k: int = 2
#
#     @weave.op()
#     def predict(self, question: str) -> dict:
#         relevant_docs = get_most_relevant_document(question, top_k=self.top_k)
#         context = "\n\n".join([
#             f"[{doc['title']}]\n{doc['content']}"
#             for doc in relevant_docs
#         ])
#
#         prompt = self._build_prompt(question, context)
#
#         response = client.chat.completions.create(
#             model=self.model_name,
#             messages=[
#                 {"role": "system", "content": "..."},
#                 {"role": "user", "content": prompt}
#             ]
#         )
#
#         return {
#             "answer": response.choices[0].message.content,
#             "context": context,
#             "sources": [doc["title"] for doc in relevant_docs]
#         }
#
#     def _build_prompt(self, question: str, context: str) -> str:
#         return f"..."


if __name__ == "__main__":
    # 테스트
    question = "RAG가 뭔가요?"
    result = generate_answer(question)
    print(f"Q: {question}")
    print(f"A: {result['answer']}")
    print(f"Sources: {result['sources']}")
