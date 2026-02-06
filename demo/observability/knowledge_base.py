"""
Knowledge Base - 문서 저장소

RAG 시스템의 문서 임베딩 및 검색을 담당합니다.
"""

import numpy as np
from openai import OpenAI

client = OpenAI()

DOCUMENTS = [
    {
        "id": "doc1",
        "title": "Python 소개",
        "content": "Python은 1991년 귀도 반 로섬이 만든 프로그래밍 언어입니다. 간결하고 읽기 쉬운 문법이 특징이며, 웹 개발, 데이터 분석, 인공지능 등 다양한 분야에서 사용됩니다.",
    },
    {
        "id": "doc2",
        "title": "FastAPI 개요",
        "content": "FastAPI는 Python으로 API를 만들기 위한 현대적인 웹 프레임워크입니다. 높은 성능과 자동 문서화 기능을 제공하며, 타입 힌트를 활용한 데이터 검증을 지원합니다.",
    },
    {
        "id": "doc3",
        "title": "RAG 아키텍처",
        "content": "RAG(Retrieval-Augmented Generation)는 검색과 생성을 결합한 아키텍처입니다. 먼저 관련 문서를 검색하고, 검색된 문서를 컨텍스트로 활용하여 LLM이 답변을 생성합니다.",
    },
    {
        "id": "doc4",
        "title": "벡터 데이터베이스",
        "content": "벡터 데이터베이스는 임베딩 벡터를 저장하고 유사도 검색을 수행하는 데이터베이스입니다. Pinecone, Weaviate, Chroma 등이 대표적인 벡터 DB입니다.",
    },
    {
        "id": "doc5",
        "title": "프롬프트 엔지니어링",
        "content": "프롬프트 엔지니어링은 LLM에게 원하는 출력을 얻기 위해 입력 프롬프트를 설계하는 기술입니다. 명확한 지시, 예시 제공, 역할 부여 등의 기법이 있습니다.",
    },
]

_embedding_cache: dict[str, list[float]] = {}


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """텍스트의 임베딩 벡터를 생성합니다."""
    cache_key = f"{model}:{text[:100]}"
    if cache_key in _embedding_cache:
        return _embedding_cache[cache_key]

    response = client.embeddings.create(model=model, input=text)
    embedding = response.data[0].embedding
    _embedding_cache[cache_key] = embedding
    return embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """두 벡터의 코사인 유사도를 계산합니다."""
    a_np, b_np = np.array(a), np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))


def get_most_relevant_document(query: str, top_k: int = 1) -> list[dict]:
    """쿼리와 가장 관련있는 문서를 검색합니다."""
    query_embedding = get_embedding(query)
    similarities = []
    for doc in DOCUMENTS:
        doc_text = f"{doc['title']}\n{doc['content']}"
        doc_embedding = get_embedding(doc_text)
        similarity = cosine_similarity(query_embedding, doc_embedding)
        similarities.append((doc, similarity))
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in similarities[:top_k]]
