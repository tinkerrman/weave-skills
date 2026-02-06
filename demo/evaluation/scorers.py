"""
RAG 평가 Scorers

질문-답변 품질을 평가하는 Scorer들입니다.
현재 일반 Python 클래스로 구현되어 있습니다.
"""

import json
from openai import OpenAI

client = OpenAI()


def answer_length_score(output: dict) -> dict:
    """답변 길이를 평가합니다."""
    answer = output.get("answer", "")
    return {"length": len(answer), "is_valid": len(answer) >= 10}


class RelevanceScorer:
    """질문과 답변의 관련성을 LLM으로 평가합니다."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def score(self, question: str, output: dict) -> dict:
        answer = output.get("answer", "")
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "다음 질문과 답변의 관련성을 1-5점으로 평가해주세요.\n\n"
                        f"질문: {question}\n"
                        f"답변: {answer}\n\n"
                        "JSON 형식으로 응답: "
                        '{"score": <1-5>, "reason": "<평가 이유>"}'
                    ),
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        result = json.loads(response.choices[0].message.content)
        return {
            "relevance_score": result["score"],
            "is_relevant": result["score"] >= 4,
            "reason": result["reason"],
        }


class FaithfulnessScorer:
    """답변이 컨텍스트에 충실한지 평가합니다 (환각 검출)."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def score(self, output: dict) -> dict:
        answer = output.get("answer", "")
        context = output.get("context", "")
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "답변이 주어진 컨텍스트에만 기반하는지 판단하세요.\n\n"
                        f"컨텍스트:\n{context[:500]}\n\n"
                        f"답변:\n{answer}\n\n"
                        "JSON 형식으로 응답: "
                        '{"verdict": "faithful" 또는 "hallucination", "reason": "<이유>"}'
                    ),
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        result = json.loads(response.choices[0].message.content)
        return {
            "is_faithful": result["verdict"] == "faithful",
            "reason": result["reason"],
        }
