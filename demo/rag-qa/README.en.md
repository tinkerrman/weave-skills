# RAG Q&A Demo

A RAG-based Q&A system for demonstrating Weave Skills.

## File Structure

```
rag-qa/
├── knowledge_base.py   # Document store + embedding search
├── rag_model.py        # RAG model (retrieval + LLM generation)
├── scorers.py          # Evaluation Scorers
├── eval_dataset.py     # Evaluation dataset
├── run_eval.py         # Evaluation runner script
└── requirements.txt
```

## How to Run

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
python run_eval.py
```

---

# Weave Skills Application Scenarios

This demonstrates what happens when each skill is applied to this demo project.

---

## 1. Applying `/init`

**User:** "initialize weave"

**Claude Response:**
```
## Weave Project Settings

Please provide the required information for weave.init().

| Field | Description | Example |
|-------|-------------|---------|
| entity | W&B team or username | my-team, username |
| project | Project name | rag-app, chatbot-v1 |

### Input
- entity: _______
- project: _______ (suggested: rag-qa-demo)

### Initialization Location
- Suggested: run_eval.py (L1, module top)
```

**User:** "entity is hyunwoo, project is rag-qa-demo"

**Result (run_eval.py):**
```python
import weave

weave.init("hyunwoo/rag-qa-demo")

from rag_model import generate_answer
# ... existing code
```

---

## 2. Applying `/add-tracing`

**User:** "add tracing"

**Claude Response:**
```
## Codebase Analysis Results

### knowledge_base.py
| Function | Location | Description |
|----------|----------|-------------|
| get_embedding() | L50-L74 | Text embedding generation |
| get_most_relevant_document() | L84-L110 | Document retrieval |
| cosine_similarity() | L77-L81 | Vector similarity calculation |

### rag_model.py
| Function | Location | Description |
|----------|----------|-------------|
| generate_answer() | L21-L70 | Main RAG function |
| _build_prompt() | L72-L83 | Prompt construction |

## Tracing Recommendations

| # | Function | Reason | Priority |
|---|----------|--------|----------|
| 1 | generate_answer() | Main LLM call | ⭐⭐⭐ |
| 2 | get_embedding() | Embedding API call | ⭐⭐⭐ |
| 3 | get_most_relevant_document() | Document retrieval | ⭐⭐⭐ |

### Excluded Functions
- cosine_similarity() - simple math operation
- _build_prompt() - private utility

Would you like to modify? (default: apply 1, 2, 3)
```

**User:** "yes"

**Claude Response:**
```
## @weave.op() Options

| Option | Description | Example |
|--------|-------------|---------|
| name | Dashboard display name | @weave.op(name="llm-call") |

Would you like to specify custom names?

| # | Function | Default Name | Custom Name |
|---|----------|--------------|-------------|
| 1 | generate_answer | generate_answer | _______ |
| 2 | get_embedding | get_embedding | _______ |
| 3 | get_most_relevant_document | get_most_relevant_document | _______ |

Leave blank to use function name as-is.
```

**User:** "use defaults"

**Result (rag_model.py):**
```python
import weave
from openai import OpenAI

client = OpenAI()

@weave.op()
def generate_answer(question: str, model: str = "gpt-4o-mini") -> dict:
    relevant_docs = get_most_relevant_document(question, top_k=2)
    # ... existing code
```

**Result (knowledge_base.py):**
```python
import weave
import numpy as np
from openai import OpenAI

@weave.op()
def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    # ... existing code

@weave.op()
def get_most_relevant_document(query: str, top_k: int = 1) -> list[dict]:
    # ... existing code
```

---

## 3. Applying `/create-dataset`

**User:** "create evaluation dataset"

**Claude Response:**
```
## Existing Data Analysis

File: eval_dataset.py
Variable: EVAL_DATASET (5 items)

### Column Structure
| Column | Type | Example |
|--------|------|---------|
| question | str | "Who created Python?" |
| expected_answer | str | "Guido van Rossum" |
| category | str | "basic" |

### Column Mapping Suggestion
- question → question (model input)
- expected_answer → expected (ground truth for Scorer)
- category → category (metadata)

Convert to weave.Dataset?
```

**User:** "yes"

**Result (added to eval_dataset.py):**
```python
import weave

# Keep existing EVAL_DATASET

# Convert to weave.Dataset
qa_eval_dataset = weave.Dataset(
    name="rag-qa-eval-v1",
    rows=[
        {
            "question": item["question"],
            "expected": item["expected_answer"],
            "category": item["category"],
        }
        for item in EVAL_DATASET
    ]
)

# Publish to Weave (optional)
# weave.publish(qa_eval_dataset)
```

---

## 4. Applying `/create-scorer`

**User:** "create a hallucination check scorer"

**Claude Response:**
```
## Scorer Creation

What would you like to evaluate?
→ Hallucination (detecting unsupported content)

## Scorer Type Selection

| Type | Recommended For |
|------|-----------------|
| Built-in HallucinationFreeScorer | Quick implementation (recommended) |
| Custom LLM Judge | When fine-tuning needed |

Use the Built-in Scorer?
```

**User:** "yes"

**Result (added to scorers.py):**
```python
from weave.scorers import HallucinationFreeScorer

# Built-in Scorer
hallucination_scorer = HallucinationFreeScorer()
```

---

## 5. Applying `/create-eval`

**User:** "create evaluation pipeline"

**Claude Response:**
```
## Evaluation Component Analysis

### Found
- Dataset: qa_eval_dataset ✅
- Scorers: HallucinationFreeScorer, RelevanceScorer ✅

### Required
- Model: No weave.Model class found ⚠️

Wrap existing generate_answer() function as weave.Model?
```

**User:** "yes"

**Result (run_eval.py full conversion):**
```python
import asyncio
import weave
from weave import Model, Evaluation
from weave.scorers import HallucinationFreeScorer

from rag_model import generate_answer
from eval_dataset import qa_eval_dataset
from scorers import RelevanceScorer

weave.init("hyunwoo/rag-qa-demo")


class RAGModel(Model):
    """Weave Model-based RAG system"""

    model_name: str = "gpt-4o-mini"

    @weave.op()
    def predict(self, question: str) -> dict:
        return generate_answer(question, model=self.model_name)


async def run_weave_evaluation():
    model = RAGModel()

    evaluation = Evaluation(
        name="rag-qa-eval-v1",
        dataset=qa_eval_dataset,
        scorers=[
            HallucinationFreeScorer(),
            RelevanceScorer(),
        ]
    )

    results = await evaluation.evaluate(model)

    print("=== Evaluation Complete ===")
    print(f"Results: {results}")
    print(f"Dashboard: https://wandb.ai/hyunwoo/rag-qa-demo")

    return results


if __name__ == "__main__":
    asyncio.run(run_weave_evaluation())
```

---

## Final Result

What becomes possible after applying all skills:

| Feature | Description |
|---------|-------------|
| Trace Visualization | Track all LLM calls, embedding generation, document retrieval |
| Evaluation Dashboard | Per-scorer scores, failed case analysis |
| Model Versioning | Automatic version creation when RAGModel parameters change |
| Dataset Versioning | Track evaluation data changes |

**W&B Weave Dashboard:** https://wandb.ai/weave
