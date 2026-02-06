# Add Weave Guardrails

This skill adds production guardrails and monitors using existing Scorers and the `call.apply_scorer()` API. It supports blocking guardrails for safety checks and non-blocking monitors for quality tracking.

**Related assets:** [guardrail_examples.py](../assets/guardrail_examples.py)

## Workflow

### Step 1: Codebase Analysis

Analyze the codebase for existing Scorers and traced functions.

**Analysis targets:**
- `Scorer` subclasses (custom and built-in)
- `@weave.op` decorated functions (scoring targets)
- Existing `call.apply_scorer()` usage
- LLM-calling functions that could benefit from guardrails

**Output format:**

```
## Guardrail Analysis Results

### Available Scorers
| # | Scorer | Location | Evaluation Target |
|---|--------|----------|-------------------|
| 1 | [ToxicityScorer](src/scorers.py#L10) | L10 | Safety |
| 2 | [RelevanceScorer](src/scorers.py#L30) | L30 | Quality |
| 3 | HallucinationFreeScorer | Built-in | Hallucination |
| 4 | ValidJSONScorer | Built-in | Format |

### Traced Functions (Scoring Targets)
| # | Function | Location | Returns |
|---|----------|----------|---------|
| 1 | [generate_response()](src/llm.py#L15) | L15 | str |
| 2 | [generate_json()](src/api.py#L20) | L20 | str (JSON) |

### Current Guardrails
- ⚠️ No call.apply_scorer() usage found

Which function would you like to add guardrails to?
```

---

### Step 2: Pattern Selection

Choose between guardrail and monitor patterns.

```
## Guardrail Pattern Selection

| Pattern | Purpose | Timing | Sampling |
|---------|---------|--------|----------|
| **Blocking Guardrail** | Prevent unsafe outputs | Real-time, synchronous | ~100% |
| **Non-blocking Monitor** | Track quality trends | Asynchronous | Configurable |
| **Sampled Monitor** | Reduce monitoring cost | Asynchronous | 10-50% |

### Comparison
| Aspect | Guardrail | Monitor |
|--------|-----------|---------|
| Impact on response | May block/modify | No impact |
| Latency | Adds to response time | No added latency |
| Cost | Every request | Sampled |
| Use case | Safety, compliance | Quality tracking |

Suggestion: **Blocking Guardrail** for safety scorers, **Sampled Monitor** for quality scorers

Which pattern would you like to use for each scorer?
```

---

### Step 3: Scorer Selection

Select and assign scorers to patterns.

```
## Scorer Assignment

| # | Scorer | Pattern | Rationale |
|---|--------|---------|-----------|
| 1 | ToxicityScorer | ⛔ Blocking Guardrail | Safety — must check every response |
| 2 | RelevanceScorer | 📊 Sampled Monitor (10%) | Quality — reduce LLM judge costs |
| 3 | ValidJSONScorer | ⛔ Blocking Guardrail | Format — must be valid JSON |

Would you like to adjust?
- "ok" — proceed with this configuration
- "change 2 to blocking" — modify assignment
- "add HallucinationFreeScorer" — add more scorers
```

---

### Step 4: Generate Integration Code

#### 4-1. Blocking Guardrail

```python
import weave

@weave.op()
def generate_response(question: str) -> str:
    # Your existing LLM call
    ...

async def safe_generate(question: str) -> str:
    """Generate with safety guardrail"""
    # .call() returns (result, Call object)
    result, call = generate_response.call(question)

    # Apply scorer as guardrail
    from src.scorers import ToxicityScorer
    safety = await call.apply_scorer(ToxicityScorer())

    if not safety.result["is_safe"]:
        return "I cannot provide that response."

    return result
```

#### 4-2. Non-blocking Monitor

```python
import asyncio
import weave

async def monitored_generate(question: str) -> str:
    """Generate with quality monitoring (non-blocking)"""
    result, call = generate_response.call(question)

    # Fire-and-forget: score in background
    from src.scorers import RelevanceScorer
    asyncio.create_task(call.apply_scorer(RelevanceScorer()))

    return result  # Return immediately
```

#### 4-3. Sampled Monitor

```python
import random
import weave

async def sampled_generate(question: str, sample_rate: float = 0.1) -> str:
    """Generate with sampled monitoring"""
    result, call = generate_response.call(question)

    # Only score 10% of calls
    if random.random() < sample_rate:
        from src.scorers import RelevanceScorer
        await call.apply_scorer(RelevanceScorer())

    return result
```

#### 4-4. Multiple Scorers (Guardrail + Monitor)

```python
import asyncio
import random
import weave

async def production_generate(question: str) -> str:
    """Complete production setup: guardrail + monitor"""
    result, call = generate_response.call(question)

    # 1. Blocking guardrail — always check safety
    from src.scorers import ToxicityScorer
    safety = await call.apply_scorer(ToxicityScorer())
    if not safety.result["is_safe"]:
        return "I cannot provide that response."

    # 2. Sampled monitor — track quality on 10% of calls
    if random.random() < 0.1:
        from src.scorers import RelevanceScorer
        asyncio.create_task(call.apply_scorer(RelevanceScorer()))

    return result
```

---

### Step 5: Completion and Next Steps

```
## Complete

✅ Guardrails added to generate_response()

Modified files:
- [src/api.py](src/api.py) - Added guardrail wrapper

### Configuration Summary
| Scorer | Pattern | Sampling |
|--------|---------|----------|
| ToxicityScorer | ⛔ Blocking | 100% |
| RelevanceScorer | 📊 Monitor | 10% |

### View Results
- **W&B Dashboard**: https://wandb.ai/weave/<project>
  - Filter by scorer name to see results
  - Track quality trends over time

### Next Steps

1. **Monitor dashboard** - Check scorer results in W&B
2. **Adjust sampling** - Increase/decrease sample rate based on cost vs coverage
3. **Add more scorers** - Reuse any existing Scorer as a guardrail or monitor

💡 Scorer results are automatically stored in Weave — view them in the Calls tab!
```

---

## Advanced Options

Available upon request:

### Additional Scorer Kwargs

When scorer parameter names don't match the function's parameters:

```python
from src.scorers import ReferenceScorer

result, call = generate_response.call(question)

# Pass extra context to scorer
await call.apply_scorer(
    ReferenceScorer(),
    additional_scorer_kwargs={"reference": expected_answer},
)
```

### Parallel Scoring

Run multiple scorers simultaneously:

```python
import asyncio

result, call = generate_response.call(question)

toxicity_result, quality_result = await asyncio.gather(
    call.apply_scorer(ToxicityScorer()),
    call.apply_scorer(QualityScorer()),
)
```

### Retrieving Scorer Results

```python
# Query calls scored by a specific scorer
client = weave.init("my-project")
calls = client.get_calls(scored_by=["ToxicityScorer"], include_feedback=True)
for call in calls:
    feedback = list(call.feedback)
    print(feedback)
```

### Custom Rejection Responses

```python
async def custom_rejection(question: str) -> dict:
    result, call = generate_response.call(question)

    safety = await call.apply_scorer(ToxicityScorer())
    if not safety.result["is_safe"]:
        return {
            "response": "I cannot help with that request.",
            "blocked": True,
            "reason": safety.result.get("reason", "Safety policy"),
        }

    return {"response": result, "blocked": False}
```

---

## Important Notes

- `call.apply_scorer()` works on any call from a `@weave.op` decorated function
- The scorer's `output` parameter automatically maps to the call's return value
- Blocking guardrails add latency — use non-blocking monitors for non-critical checks
- Scorer results are automatically logged to Weave regardless of pattern
- The same Scorer class works in both `weave.Evaluation` and `call.apply_scorer()`
- For async scorers, the `score` method should be `async def score(...)`
- Sampling rate should be calibrated to balance cost vs monitoring coverage
