"""
Scorers for RAG Q&A Evaluation

이 파일은 RAG 시스템 평가를 위한 다양한 Scorer를 구현합니다.

스킬 적용 대상:
- /create-scorer: 이 파일의 Scorer들을 템플릿으로 활용

Scorer 종류:
1. 함수 기반 Scorer (간단한 평가)
2. 클래스 기반 Scorer (복잡한 평가)
3. LLM Judge Scorer (주관적 평가)
"""

import json
from openai import OpenAI

# ===== 스킬 적용 전 버전 =====

client = OpenAI()


# ----- 1. 함수 기반 Scorer -----

def answer_length_score(output: dict, min_length: int = 10) -> dict:
    """
    답변 길이 평가

    Args:
        output: 모델 출력 (answer 키 포함)
        min_length: 최소 길이

    Returns:
        dict: length, is_valid
    """
    answer = output.get("answer", "")
    length = len(answer)

    return {
        "length": length,
        "is_valid": length >= min_length
    }


def source_citation_score(output: dict) -> dict:
    """
    출처 인용 여부 평가

    Returns:
        dict: has_sources, source_count
    """
    sources = output.get("sources", [])

    return {
        "has_sources": len(sources) > 0,
        "source_count": len(sources)
    }


def context_used_score(output: dict) -> dict:
    """
    컨텍스트가 답변에 활용되었는지 평가 (키워드 기반)

    Returns:
        dict: context_overlap_ratio
    """
    answer = output.get("answer", "").lower()
    context = output.get("context", "").lower()

    if not context:
        return {"context_overlap_ratio": 0.0}

    # 컨텍스트의 주요 단어가 답변에 포함되었는지 확인
    context_words = set(context.split())
    answer_words = set(answer.split())

    # 불용어 제거 (간단한 버전)
    stopwords = {"은", "는", "이", "가", "을", "를", "의", "에", "와", "과", "도", "로", "a", "the", "is", "are"}
    context_words = context_words - stopwords
    answer_words = answer_words - stopwords

    if not context_words:
        return {"context_overlap_ratio": 0.0}

    overlap = len(context_words & answer_words)
    ratio = overlap / len(context_words)

    return {
        "context_overlap_ratio": round(ratio, 3),
        "overlap_count": overlap
    }


# ----- 2. 클래스 기반 Scorer (Weave 적용 후 버전 참고) -----

class RelevanceScorer:
    """
    질문과 답변의 관련성을 평가하는 Scorer

    Note: Weave 적용 시 weave.Scorer를 상속받아야 합니다.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = OpenAI()

    def score(self, question: str, output: dict) -> dict:
        """
        LLM을 사용하여 관련성을 평가합니다.

        Args:
            question: 원본 질문
            output: 모델 출력

        Returns:
            dict: relevance_score (1-5), is_relevant, reason
        """
        answer = output.get("answer", "")

        prompt = f"""다음 질문과 답변의 관련성을 1-5점으로 평가해주세요.

질문: {question}
답변: {answer}

평가 기준:
- 5점: 질문에 정확하고 완전하게 답변
- 4점: 대체로 관련있고 유용한 답변
- 3점: 부분적으로 관련있는 답변
- 2점: 거의 관련없는 답변
- 1점: 전혀 관련없는 답변

JSON 형식으로 응답해주세요:
{{"score": <1-5>, "reason": "<평가 이유>"}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )

        result = json.loads(response.choices[0].message.content)

        return {
            "relevance_score": result["score"],
            "is_relevant": result["score"] >= 4,
            "reason": result["reason"]
        }


# ----- 3. LLM Judge Scorer -----

class FaithfulnessScorer:
    """
    답변이 컨텍스트에 충실한지 평가 (Hallucination 검출)

    Note: Weave 적용 시 weave.Scorer를 상속받아야 합니다.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = OpenAI()

    def score(self, output: dict) -> dict:
        """
        답변이 주어진 컨텍스트에만 기반하는지 평가합니다.

        Args:
            output: 모델 출력 (answer, context 포함)

        Returns:
            dict: is_faithful, hallucination_detected, reason
        """
        answer = output.get("answer", "")
        context = output.get("context", "")

        prompt = f"""다음 답변이 주어진 컨텍스트에만 기반하는지 평가해주세요.

### 컨텍스트:
{context}

### 답변:
{answer}

평가 기준:
- 답변의 모든 정보가 컨텍스트에서 찾을 수 있으면 "faithful"
- 컨텍스트에 없는 정보가 포함되어 있으면 "hallucination"

JSON 형식으로 응답:
{{"verdict": "faithful" | "hallucination", "reason": "<이유>", "hallucinated_parts": ["<환각 부분1>", ...]}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )

        result = json.loads(response.choices[0].message.content)

        return {
            "is_faithful": result["verdict"] == "faithful",
            "hallucination_detected": result["verdict"] == "hallucination",
            "reason": result["reason"],
            "hallucinated_parts": result.get("hallucinated_parts", [])
        }


class ContextPrecisionScorer:
    """
    검색된 컨텍스트가 답변 생성에 얼마나 유용했는지 평가

    RAGAS framework 기반
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = OpenAI()

    def score(self, question: str, output: dict) -> dict:
        """
        컨텍스트의 정밀도를 평가합니다.

        Args:
            question: 원본 질문
            output: 모델 출력 (context 포함)

        Returns:
            dict: precision_score, useful_context_ratio
        """
        context = output.get("context", "")

        prompt = f"""다음 질문에 답변하기 위해 주어진 컨텍스트가 얼마나 유용한지 평가해주세요.

### 질문:
{question}

### 컨텍스트:
{context}

각 컨텍스트 부분이 질문에 답하는 데 유용한지 판단해주세요.

JSON 형식으로 응답:
{{"useful_parts": <유용한 부분 수>, "total_parts": <전체 부분 수>, "precision": <0.0-1.0>, "reason": "<이유>"}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )

        result = json.loads(response.choices[0].message.content)

        return {
            "precision_score": result["precision"],
            "useful_parts": result["useful_parts"],
            "total_parts": result["total_parts"],
            "reason": result["reason"]
        }


# ===== 스킬 적용 후 버전 예시 (주석) =====
#
# import weave
# from weave import Scorer
#
# class RelevanceScorer(Scorer):
#     """Weave Scorer 기반 관련성 평가"""
#
#     model: str = "gpt-4o-mini"
#
#     @weave.op()
#     def score(self, question: str, output: dict) -> dict:
#         # ... 동일한 로직 ...
#         return {"relevance_score": score, "is_relevant": score >= 4}


if __name__ == "__main__":
    # 테스트
    test_output = {
        "answer": "RAG는 Retrieval-Augmented Generation의 약자로, 검색과 생성을 결합한 아키텍처입니다.",
        "context": "RAG(Retrieval-Augmented Generation)는 검색과 생성을 결합한 아키텍처입니다.",
        "sources": ["RAG 아키텍처"]
    }

    print("=== 함수 기반 Scorer 테스트 ===")
    print(f"Length: {answer_length_score(test_output)}")
    print(f"Source: {source_citation_score(test_output)}")
    print(f"Context: {context_used_score(test_output)}")

    print("\n=== 클래스 기반 Scorer 테스트 ===")
    relevance = RelevanceScorer()
    print(f"Relevance: {relevance.score('RAG가 뭔가요?', test_output)}")

    faithfulness = FaithfulnessScorer()
    print(f"Faithfulness: {faithfulness.score(test_output)}")
