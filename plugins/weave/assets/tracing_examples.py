"""
Weave Tracing (@weave.op) Example Code

Based on official docs: https://docs.wandb.ai/weave/guides/tracking/tracing
"""

import weave
import json
from openai import OpenAI

weave.init("tracing-examples")
client = OpenAI()


# ===== Basic Function Tracing =====

@weave.op()
def simple_function(x: int, y: int) -> int:
    """Add tracing to a basic function"""
    return x + y


# ===== LLM Call Tracing =====

@weave.op()
def call_llm(prompt: str) -> str:
    """Trace LLM API calls"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# ===== Async Function Tracing =====

@weave.op()
async def async_call_llm(prompt: str) -> str:
    """Same decorator works for async functions"""
    response = await client.chat.completions.acreate(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# ===== Nested Tracing (Automatic Hierarchy) =====

@weave.op()
def preprocess(text: str) -> str:
    """Preprocessing function"""
    return text.strip().lower()

@weave.op()
def postprocess(text: str) -> str:
    """Postprocessing function"""
    return text.capitalize()

@weave.op()
def pipeline(text: str) -> str:
    """Pipeline - internal calls are automatically traced"""
    processed = preprocess(text)
    result = call_llm(processed)
    return postprocess(result)


# ===== Class Method Tracing =====

class TextProcessor:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = OpenAI()

    @weave.op()
    def process(self, text: str) -> str:
        """Instance method tracing"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": text}]
        )
        return response.choices[0].message.content

    @staticmethod
    @weave.op()
    def static_process(text: str) -> str:
        """Static method tracing"""
        return text.upper()


# ===== Custom Op Name =====

@weave.op(name="custom-extraction-op")
def extract_data(text: str) -> dict:
    """Specify custom op name"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract JSON data"},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)


# ===== Official Quickstart Example =====

@weave.op()
def extract_dinos(sentence: str) -> dict:
    """Dinosaur extraction example from official docs"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """In JSON format extract a list of `dinosaurs`,
with their `name`, their `common_name`, and whether its `diet` is a herbivore or carnivore"""
            },
            {"role": "user", "content": sentence}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)


if __name__ == "__main__":
    # Test execution
    result = simple_function(1, 2)
    print(f"Simple: {result}")

    result = extract_dinos("I saw a T-rex and a Triceratops at the museum.")
    print(f"Dinos: {result}")
