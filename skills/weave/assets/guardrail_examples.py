"""
Weave Guardrail and Monitor Example Code

Based on official docs: https://docs.wandb.ai/weave/guides/evaluation/guardrails_and_monitors
"""

import weave
from weave import Scorer

weave.init("guardrail-examples")


# ===== 1. Blocking Guardrail =====

class ToxicityGuardrail(Scorer):
    """Block toxic responses before returning to user"""

    @weave.op()
    async def score(self, output: str) -> dict:
        # In practice, use an ML model or moderation API
        toxic_terms = ["harmful", "offensive", "dangerous"]
        is_toxic = any(term in output.lower() for term in toxic_terms)
        return {"is_safe": not is_toxic, "blocked": is_toxic}


@weave.op()
def generate_response(question: str) -> str:
    """Generate a response (traced function)"""
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content


async def blocking_guardrail_example(question: str) -> str:
    """Apply guardrail: block unsafe responses"""
    # .call() returns (result, Call object)
    result, call = generate_response.call(question)

    # Apply scorer as guardrail
    guardrail = ToxicityGuardrail()
    score_result = await call.apply_scorer(guardrail)

    if score_result.result["is_safe"]:
        return result
    else:
        return "I'm sorry, I cannot provide that response."


# ===== 2. Non-blocking Monitor =====

class QualityMonitor(Scorer):
    """Monitor response quality without blocking"""

    @weave.op()
    async def score(self, output: str, question: str) -> dict:
        return {
            "has_content": len(output) > 10,
            "appropriate_length": 10 < len(output) < 5000,
        }


async def non_blocking_monitor_example(question: str) -> str:
    """Score asynchronously — results logged to Weave, no blocking"""
    import asyncio

    result, call = generate_response.call(question)

    # Fire-and-forget: log quality without waiting
    monitor = QualityMonitor()
    asyncio.create_task(call.apply_scorer(monitor))

    # Return immediately
    return result


# ===== 3. Sampled Monitor =====

import random


async def sampled_monitor_example(
    question: str, sample_rate: float = 0.1
) -> str:
    """Score only a percentage of calls to reduce cost"""
    result, call = generate_response.call(question)

    # Only score 10% of calls
    if random.random() < sample_rate:
        monitor = QualityMonitor()
        await call.apply_scorer(monitor)

    return result


# ===== 4. Multiple Scorers in Parallel =====

import asyncio


class LengthScorer(Scorer):
    """Check response length"""

    @weave.op()
    async def score(self, output: str) -> dict:
        return {"appropriate_length": 10 < len(output) < 5000}


async def multi_scorer_example(question: str) -> str:
    """Apply multiple scorers to a single call in parallel"""
    result, call = generate_response.call(question)

    toxicity = ToxicityGuardrail()
    length = LengthScorer()

    # Run scorers in parallel
    toxicity_result, length_result = await asyncio.gather(
        call.apply_scorer(toxicity),
        call.apply_scorer(length),
    )

    if not toxicity_result.result["is_safe"]:
        return "Response blocked by safety guardrail."
    if not length_result.result["appropriate_length"]:
        return "Response was too short or too long."

    return result


# ===== 5. Additional Scorer Kwargs =====

class ReferenceScorer(Scorer):
    """Score output against a reference answer"""

    @weave.op()
    async def score(self, output: str, reference: str) -> dict:
        return {"matches_reference": reference.lower() in output.lower()}


async def additional_kwargs_example(question: str, expected: str) -> str:
    """Pass extra context to scorer via additional_scorer_kwargs"""
    result, call = generate_response.call(question)

    scorer = ReferenceScorer()
    score_result = await call.apply_scorer(
        scorer,
        additional_scorer_kwargs={"reference": expected},
    )

    return result


# ===== 6. Reusing Evaluation Scorers as Guardrails =====

from weave.scorers import ValidJSONScorer


@weave.op()
def generate_json(question: str) -> str:
    """Generate JSON response"""
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


async def json_guardrail_example(question: str) -> str:
    """Use a built-in evaluation scorer as a production guardrail"""
    result, call = generate_json.call(question)

    # Same scorer used in weave.Evaluation works as guardrail
    json_scorer = ValidJSONScorer()
    score_result = await call.apply_scorer(json_scorer)

    if score_result.result["valid_json"]:
        return result
    else:
        return '{"error": "Invalid JSON response"}'


if __name__ == "__main__":

    async def main():
        # Blocking guardrail
        print("=== Blocking Guardrail ===")
        response = await blocking_guardrail_example("What is Python?")
        print(f"Response: {response}")

        # Multi-scorer
        print("\n=== Multi-Scorer ===")
        response = await multi_scorer_example("Explain machine learning.")
        print(f"Response: {response}")

        # JSON guardrail
        print("\n=== JSON Guardrail ===")
        response = await json_guardrail_example("List 3 fruits as JSON")
        print(f"Response: {response}")

    asyncio.run(main())
