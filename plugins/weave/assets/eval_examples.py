"""
Weave Evaluation Example Code

Based on official docs: https://docs.wandb.ai/weave/tutorial-eval
"""

import asyncio
import weave
from weave import Model, Evaluation

weave.init("eval-examples")


# ===== 1. Basic Model Definition =====

class FruitExtractor(Model):
    """Model that extracts fruit information (official tutorial example)"""

    model_name: str = "gpt-4o-mini"
    system_prompt: str = "Extract fruit information from the text."

    @weave.op()
    def predict(self, sentence: str) -> dict:
        from openai import OpenAI
        client = OpenAI()

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": sentence}
            ],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)


# ===== 2. Dataset Definition =====

# Inline dataset
dataset = [
    {"sentence": "There is a red apple on the table.", "expected": {"fruit": "apple", "color": "red"}},
    {"sentence": "I ate a yellow banana for breakfast.", "expected": {"fruit": "banana", "color": "yellow"}},
    {"sentence": "The orange is very juicy.", "expected": {"fruit": "orange", "color": "orange"}},
]

# Or use weave.Dataset
fruit_dataset = weave.Dataset(
    name="fruit-extraction-v1",
    rows=dataset
)


# ===== 3. Scorer Definition =====

@weave.op()
def fruit_match_scorer(output: dict, expected: dict) -> dict:
    """Evaluate if fruit name matches"""
    return {
        "fruit_match": output.get("fruit", "").lower() == expected.get("fruit", "").lower()
    }


@weave.op()
def color_match_scorer(output: dict, expected: dict) -> dict:
    """Evaluate if color matches"""
    return {
        "color_match": output.get("color", "").lower() == expected.get("color", "").lower()
    }


# ===== 4. Run Evaluation =====

async def run_basic_evaluation():
    """Run basic evaluation"""
    model = FruitExtractor()

    evaluation = Evaluation(
        dataset=dataset,
        scorers=[fruit_match_scorer, color_match_scorer]
    )

    results = await evaluation.evaluate(model)
    print(f"Results: {results}")
    return results


# ===== 5. Model Comparison Evaluation =====

async def compare_models():
    """Compare multiple models"""
    models = [
        FruitExtractor(model_name="gpt-4o-mini"),
        FruitExtractor(model_name="gpt-4o"),
    ]

    evaluation = Evaluation(
        dataset=dataset,
        scorers=[fruit_match_scorer, color_match_scorer]
    )

    for model in models:
        print(f"\n=== Evaluating {model.model_name} ===")
        results = await evaluation.evaluate(model)
        print(f"Results: {results}")


# ===== 6. Partial Dataset Evaluation =====

async def evaluate_subset():
    """Test with partial data"""
    model = FruitExtractor()

    # First 2 items only
    small_dataset = dataset[:2]

    evaluation = Evaluation(
        dataset=small_dataset,
        scorers=[fruit_match_scorer]
    )

    results = await evaluation.evaluate(model)
    return results


# ===== 7. Environment Variable Settings =====

# Parallelism settings (rate limit prevention)
import os
os.environ["WEAVE_PARALLELISM"] = "5"  # Limit concurrent executions


# ===== 8. RAG Evaluation Example =====

class RAGModel(Model):
    """RAG Model"""

    model_name: str = "gpt-4o-mini"

    @weave.op()
    def predict(self, question: str) -> dict:
        # In practice: retrieval + generation
        from openai import OpenAI
        client = OpenAI()

        # Simple example
        context = "Paris is the capital of France. It is known for the Eiffel Tower."

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": f"Answer based on context: {context}"},
                {"role": "user", "content": question}
            ]
        )

        return {
            "answer": response.choices[0].message.content,
            "context": context
        }


# RAG evaluation scorer
@weave.op()
def answer_relevance_scorer(output: dict, question: str) -> dict:
    """Check if answer is relevant to question"""
    answer = output.get("answer", "")
    # Simple heuristic
    return {"is_relevant": len(answer) > 10}


rag_dataset = [
    {"question": "What is the capital of France?"},
    {"question": "What is Paris known for?"},
]


async def evaluate_rag():
    """Evaluate RAG model"""
    model = RAGModel()

    evaluation = Evaluation(
        dataset=rag_dataset,
        scorers=[answer_relevance_scorer]
    )

    results = await evaluation.evaluate(model)
    return results


if __name__ == "__main__":
    # Run basic evaluation
    asyncio.run(run_basic_evaluation())
