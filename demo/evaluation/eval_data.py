"""
평가 데이터셋

RAG 시스템 평가를 위한 질문-답변 쌍입니다.
현재 일반 Python 리스트로 정의되어 있습니다.
"""

EVAL_DATASET = [
    {
        "question": "Python은 누가 만들었나요?",
        "expected": "귀도 반 로섬",
        "category": "기본",
    },
    {
        "question": "FastAPI의 특징은 무엇인가요?",
        "expected": "높은 성능과 자동 문서화 기능",
        "category": "프레임워크",
    },
    {
        "question": "RAG 아키텍처란 무엇인가요?",
        "expected": "검색과 생성을 결합한 아키텍처",
        "category": "AI",
    },
    {
        "question": "벡터 데이터베이스는 무엇인가요?",
        "expected": "임베딩 벡터를 저장하고 유사도 검색을 수행하는 데이터베이스",
        "category": "데이터",
    },
    {
        "question": "프롬프트 엔지니어링이란?",
        "expected": "LLM에게 원하는 출력을 얻기 위해 입력 프롬프트를 설계하는 기술",
        "category": "AI",
    },
]
