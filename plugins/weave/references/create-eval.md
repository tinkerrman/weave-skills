# Create Weave Evaluation

This skill builds Weave evaluation pipelines. It analyzes the codebase to compose complete evaluation workflows combining Model, Dataset, and Scorer components.

**Related assets:** [eval_examples.py](../assets/eval_examples.py)

## Workflow

### Step 1: Codebase Analysis

Analyze components needed for evaluation.

```
## Evaluation Component Analysis

### Models Found
| # | Model | Location | predict Method |
|---|-------|----------|----------------|
| 1 | [RAGModel](src/models/rag.py#L15) | L15-L50 | ✅ predict(question) → answer |
| 2 | [ChatBot](src/models/chat.py#L8) | L8-L40 | ✅ predict(messages) → response |

### Datasets Found
| # | Dataset | Location | Columns |
|---|---------|----------|---------|
| 1 | [qa_dataset](src/data/eval_data.py#L10) | L10 | question, expected_answer |
| 2 | Stored in Weave `test-questions-v2` | W&B | question, context |

### Scorers Found
| # | Scorer | Location | Evaluation Target |
|---|--------|----------|-------------------|
| 1 | [LLMJudgeScorer](src/scorers/judge.py#L12) | L12 | relevance |
| 2 | [exact_match](src/scorers/basic.py#L5) | L5 | correctness |

### Status
- ✅ Model: Ready
- ✅ Dataset: Ready
- ✅ Scorer: Ready
- ⚠️ Evaluation script: Not found

Would you like to create an evaluation script?
```

---

### Step 2: Evaluation Configuration

Confirm the combination for evaluation.

```
## Evaluation Configuration

**Select Model:**
- [1] RAGModel (src/models/rag.py)
- [2] ChatBot (src/models/chat.py)
→ Selection: 1

**Select Dataset:**
- [1] qa_dataset (local)
- [2] test-questions-v2 (Weave)
→ Selection: 1

**Select Scorers (multiple allowed):**
- [1] LLMJudgeScorer (relevance)
- [2] exact_match (correctness)
- [3] Create new (/create-scorer)
→ Selection: 1, 2

---

### Configuration Summary

```
Model:    RAGModel
Dataset:  qa_dataset (50 examples)
Scorers:  LLMJudgeScorer, exact_match
```

Would you like to generate the evaluation script with this configuration?
```

---

### Step 3: Generate Evaluation Script

```python
# src/evaluation/run_eval.py

import asyncio
import weave
from src.models.rag import RAGModel
from src.data.eval_data import qa_dataset
from src.scorers.judge import LLMJudgeScorer
from src.scorers.basic import exact_match

# Initialize Weave
weave.init("my-rag-eval")

async def run_evaluation():
    # Model instance
    model = RAGModel()

    # Evaluation configuration
    evaluation = weave.Evaluation(
        name="rag-evaluation-v1",
        dataset=qa_dataset,
        scorers=[
            LLMJudgeScorer(criteria="relevance"),
            exact_match,
        ],
    )

    # Run evaluation
    results = await evaluation.evaluate(model)

    print("=== Evaluation Complete ===")
    print(f"View results: https://wandb.ai/weave/{weave.get_current_project()}")

    return results

if __name__ == "__main__":
    asyncio.run(run_evaluation())
```

---

### Step 4: File Creation Location

```
## File Creation

Files to create:
- [src/evaluation/run_eval.py](src/evaluation/run_eval.py) (new file)
- [src/evaluation/__init__.py](src/evaluation/__init__.py) (new file)

Proceed?
```

---

### Step 5: Run and View Results

```
## Complete

✅ Evaluation script created

### How to Run
```bash
python src/evaluation/run_eval.py
```

### View Results
- **Terminal**: Summary statistics after execution
- **W&B Dashboard**: https://wandb.ai/weave/<project>
  - Per-example scores
  - Aggregated statistics per Scorer
  - Failed case analysis

### Sample Output
```
=== Evaluation Results ===
Total: 50 examples evaluated

LLMJudgeScorer:
  - Average score: 4.2/5
  - Pass rate: 84%

exact_match:
  - Match rate: 72%

Detailed results: https://wandb.ai/weave/my-rag-eval
```
```

---

## Advanced Options

### Parallel Evaluation
```python
evaluation = weave.Evaluation(
    dataset=qa_dataset,
    scorers=[LLMJudgeScorer()],
    # Parallel processing configuration
    max_concurrent=10,
)
```

### Partial Dataset Evaluation
```python
# Test with first 10 examples only
small_dataset = qa_dataset.select(range(10))

evaluation = weave.Evaluation(
    dataset=small_dataset,
    scorers=[LLMJudgeScorer()],
)
```

### Model Comparison Evaluation
```python
async def compare_models():
    models = [
        RAGModel(retriever="bm25"),
        RAGModel(retriever="semantic"),
    ]

    evaluation = weave.Evaluation(
        dataset=qa_dataset,
        scorers=[LLMJudgeScorer()],
    )

    for model in models:
        results = await evaluation.evaluate(model)
        print(f"{model.__class__.__name__}: {results}")
```

### Programmatic Access to Results
```python
results = await evaluation.evaluate(model)

# Overall statistics
print(results.summary)

# Access individual results
for row in results.rows:
    if not row.scores["exact_match"]["match"]:
        print(f"Failed: {row.input} → {row.output}")
```

---

## When Components Are Missing

### When Model is Missing
```
⚠️ No class inheriting weave.Model found.

Would you like to wrap an existing function as a Model?

Candidates found:
- [generate_answer()](src/llm.py#L20) - LLM call function

→ "yes" or create manually
```

**Auto-wrapping example:**
```python
import weave

class SimpleModel(weave.Model):
    @weave.op
    def predict(self, question: str) -> str:
        return generate_answer(question)  # Use existing function
```

### When Dataset is Missing
```
⚠️ No evaluation dataset found.

Please choose:
1. Create new dataset (/create-dataset)
2. Load from existing file (CSV, JSON)
3. Fetch from Weave
```

### When Scorer is Missing
```
⚠️ No Scorer found.

For a quick start:
1. Use basic Scorer (exact_match)
2. Generate LLM Judge (/create-scorer)
```

---

## Environment Configuration

### Parallelism Limit (Rate Limit Prevention)

For evaluations with many LLM API calls, limit parallelism to avoid rate limits.

```bash
# Set via environment variable
export WEAVE_PARALLELISM=5
```

```python
# Set in code
import os
os.environ["WEAVE_PARALLELISM"] = "5"
```

### Recommended Settings

| API Provider | Recommended WEAVE_PARALLELISM |
|--------------|-------------------------------|
| OpenAI (Tier 1) | 3-5 |
| OpenAI (Tier 2+) | 10-20 |
| Anthropic | 5-10 |
| Local models | Unlimited (no setting needed) |

---

## Important Notes

- `evaluate()` is an async function → requires `asyncio.run()`
- Dataset column names must match Model's predict parameter names
- Scorer parameter names must match Dataset column names for automatic mapping
- Be mindful of LLM API costs for large evaluations
- **Rate Limit**: Use `WEAVE_PARALLELISM` environment variable to limit concurrent executions
- **Timeout**: Large datasets may take significant time
