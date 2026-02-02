"""
Weave Scorer Example Code

Based on official docs: https://docs.wandb.ai/weave/guides/evaluation/scorers
"""

import json
import weave
from weave import Scorer
from openai import OpenAI

weave.init("scorer-examples")


# ===== 1. Function-based Scorer =====

@weave.op()
def exact_match_scorer(output: str, expected: str) -> dict:
    """Evaluate exact match"""
    return {
        "match": output.strip().lower() == expected.strip().lower()
    }


@weave.op()
def contains_scorer(output: str, expected: str) -> dict:
    """Evaluate if expected answer is contained in output"""
    return {
        "contains": expected.lower() in output.lower()
    }


@weave.op()
def length_scorer(output: str, min_length: int = 10, max_length: int = 500) -> dict:
    """Evaluate output length"""
    length = len(output)
    return {
        "length": length,
        "valid_length": min_length <= length <= max_length
    }


# ===== 2. Class-based Scorer =====

class SummarizationScorer(Scorer):
    """Scorer for evaluating summary quality (official docs example)"""

    model_id: str = "gpt-4o"
    system_prompt: str = "Evaluate whether the summary is good."

    @weave.op()
    def some_complicated_preprocessing(self, text: str) -> str:
        """Complex preprocessing logic"""
        processed_text = "Original text: \n" + text + "\n"
        return processed_text

    @weave.op()
    def score(self, output: str, text: str) -> dict:
        """Main evaluation logic"""
        processed_text = self.some_complicated_preprocessing(text)
        # In actual implementation, call LLM for evaluation
        return {"summary_quality": processed_text}


class RelevanceScorer(Scorer):
    """Evaluate question-answer relevance"""

    model: str = "gpt-4o-mini"
    threshold: float = 0.7

    @weave.op()
    def score(self, question: str, output: str) -> dict:
        client = OpenAI()

        prompt = f"""Rate the relevance of the answer to the question on a scale of 0 to 1.

Question: {question}
Answer: {output}

Respond with JSON: {{"relevance": <0.0-1.0>, "reason": "<explanation>"}}"""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return {
            "relevance": result["relevance"],
            "is_relevant": result["relevance"] >= self.threshold,
            "reason": result["reason"]
        }


class FaithfulnessScorer(Scorer):
    """Evaluate if RAG answer is faithful to context (Hallucination detection)"""

    model: str = "gpt-4o-mini"

    @weave.op()
    def score(self, output: str, context: str) -> dict:
        client = OpenAI()

        prompt = f"""Evaluate if the answer is faithful to the given context.
Does the answer contain only information from the context?

Context: {context}
Answer: {output}

Respond with JSON: {{"is_faithful": true/false, "hallucinated_claims": ["claim1", ...]}}"""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return {
            "is_faithful": result["is_faithful"],
            "hallucination_free": result["is_faithful"],
            "hallucinated_claims": result.get("hallucinated_claims", [])
        }


# ===== 3. Built-in Scorers Usage =====

from weave.scorers import (
    HallucinationFreeScorer,
    ValidJSONScorer,
    ValidXMLScorer,
    # PydanticScorer,  # Requires Pydantic model
    # EmbeddingSimilarityScorer,
    # OpenAIModerationScorer,
    # ContextEntityRecallScorer,
    # ContextRelevancyScorer,
)

# Hallucination detection
hallucination_scorer = HallucinationFreeScorer()

# JSON validity check
json_scorer = ValidJSONScorer()

# XML validity check
xml_scorer = ValidXMLScorer()


# ===== 4. Pydantic Scorer Example =====

from pydantic import BaseModel
from weave.scorers import PydanticScorer

class FruitExtraction(BaseModel):
    """Fruit extraction result schema"""
    name: str
    color: str
    taste: str

# Schema validation scorer
fruit_schema_scorer = PydanticScorer(model=FruitExtraction)


# ===== 5. Column Mapping =====

class MyScorer(Scorer):
    """Mapping when column names differ"""

    # Dataset column: "model_output" -> Scorer parameter: "output"
    column_map = {"output": "model_output"}

    @weave.op()
    def score(self, output: str) -> dict:
        return {"length": len(output)}


# ===== Usage in Evaluation =====

if __name__ == "__main__":
    # Test data
    test_output = "Paris is the capital of France."
    test_expected = "Paris"

    # Function-based Scorer test
    print("=== Function Scorers ===")
    print(f"Exact match: {exact_match_scorer(test_output, test_expected)}")
    print(f"Contains: {contains_scorer(test_output, test_expected)}")
    print(f"Length: {length_scorer(test_output)}")

    # Class-based Scorer test
    print("\n=== Class Scorers ===")
    relevance = RelevanceScorer()
    result = relevance.score(
        question="What is the capital of France?",
        output=test_output
    )
    print(f"Relevance: {result}")
