"""
Weave Model Example Code

Based on official docs: https://docs.wandb.ai/weave/guides/core-types/models
"""

import weave
from weave import Model

weave.init("model-examples")


# ===== 1. Basic Model =====

class BasicQAModel(Model):
    """Simple question answering model"""

    @weave.op()
    def predict(self, question: str) -> str:
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}],
        )
        return response.choices[0].message.content


# ===== 2. Configurable Model =====

class ConfigurableModel(Model):
    """Model with typed configuration attributes (auto-versioned by Weave)"""

    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: str = "You are a helpful assistant."

    @weave.op()
    def predict(self, question: str) -> str:
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question},
            ],
        )
        return response.choices[0].message.content


# ===== 3. RAG Model =====

class RAGModel(Model):
    """Retrieval-Augmented Generation model"""

    model_name: str = "gpt-4o-mini"
    top_k: int = 3

    @weave.op()
    def retrieve(self, query: str) -> list[str]:
        """Retrieve relevant documents"""
        # Replace with actual retrieval logic (vector DB, BM25, etc.)
        return ["Document 1 content", "Document 2 content"]

    @weave.op()
    def predict(self, question: str) -> dict:
        contexts = self.retrieve(question)
        context_str = "\n".join(contexts)

        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": f"Answer based on context:\n{context_str}"},
                {"role": "user", "content": question},
            ],
        )
        return {
            "answer": response.choices[0].message.content,
            "contexts": contexts,
        }


# ===== 4. Anthropic Model =====

class AnthropicModel(Model):
    """Model using Anthropic API"""

    model_name: str = "claude-sonnet-4-20250514"
    max_tokens: int = 1024

    @weave.op()
    def predict(self, question: str) -> str:
        from anthropic import Anthropic

        client = Anthropic()
        message = client.messages.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": question}],
        )
        return message.content[0].text


# ===== 5. Model Comparison =====

async def compare_models():
    """Compare multiple model configurations in evaluation"""
    from weave import Evaluation

    models = [
        ConfigurableModel(model_name="gpt-4o-mini", temperature=0.0),
        ConfigurableModel(model_name="gpt-4o", temperature=0.0),
    ]

    dataset = [
        {"question": "What is Python?", "expected": "A programming language"},
        {"question": "What is 2+2?", "expected": "4"},
    ]

    @weave.op()
    def length_scorer(output: str) -> dict:
        return {"length": len(output), "has_content": len(output) > 10}

    evaluation = Evaluation(dataset=dataset, scorers=[length_scorer])

    for model in models:
        print(f"\n=== {model.model_name} ===")
        results = await evaluation.evaluate(model)
        print(f"Results: {results}")


# ===== 6. Wrapping Existing Function =====

# Before: standalone function
def existing_llm_call(question: str) -> str:
    """An existing function you want to track as a Model"""
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content


# After: wrapped as Model
class WrappedModel(Model):
    """Wrapping an existing function as a Model"""

    @weave.op()
    def predict(self, question: str) -> str:
        return existing_llm_call(question)


# ===== 7. Production Attributes =====

def production_tracking():
    """Track model calls with environment attributes"""
    model = ConfigurableModel(model_name="gpt-4o", temperature=0.0)

    with weave.attributes({"env": "production", "version": "v1.2"}):
        result = model.predict("What is Python?")
        print(result)


if __name__ == "__main__":
    # Test basic model
    model = BasicQAModel()
    result = model.predict("What is the capital of France?")
    print(f"Basic: {result}")

    # Test configurable model with different settings
    model_v1 = ConfigurableModel(temperature=0.0)
    model_v2 = ConfigurableModel(temperature=1.0, system_prompt="Be creative.")
    print(f"v1: {model_v1.predict('What is 2+2?')}")
    print(f"v2: {model_v2.predict('What is 2+2?')}")

    # Test model comparison
    import asyncio

    asyncio.run(compare_models())
