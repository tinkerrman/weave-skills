# Create Weave Scorer

This skill generates custom Scorers for Weave evaluation. It suggests appropriate Scorer types based on evaluation goals and provides templates.

**Related assets:** [scorer_examples.py](../assets/scorer_examples.py)

## Workflow

### Step 1: Identify Evaluation Goal

Ask the user what they want to evaluate.

```
## Scorer Creation

What would you like to evaluate?

| # | Evaluation Type | Description | Examples |
|---|-----------------|-------------|----------|
| 1 | **Correctness** | Compare against expected answer | QA, Classification |
| 2 | **Relevance** | Question-answer relevance | RAG, Search |
| 3 | **Fluency** | Grammar, naturalness | Generation, Translation |
| 4 | **Safety** | Harmful content detection | Chatbot |
| 5 | **Hallucination** | Unsupported content detection | RAG |
| 6 | **Custom** | Define your own | - |

Please provide a number or description. (e.g., "1", "RAG relevance evaluation")
```

---

### Step 2: Scorer Type Selection

Suggest a type based on evaluation complexity.

```
## Scorer Type Selection

| Type | Recommended For | Characteristics |
|------|-----------------|-----------------|
| **Function-based** | Simple metrics, quick implementation | Simple, @weave.op decorator |
| **Class-based** | Complex logic, state required | Configurable, highly reusable |
| **LLM Judge** | Subjective evaluation, complex criteria | LLM (GPT-4, etc.) performs evaluation |

Suggestion: **LLM Judge** (suitable for relevance evaluation)

Would you like to proceed with this type?
```

---

### Step 3: Generate Scorer Code

Provide templates based on selection.

#### 3-1. Function-based Scorer

```python
import weave

@weave.op
def exactmatch_scorer(output: str, expected: str) -> dict:
    """Evaluate exact match"""
    return {
        "match": output.strip() == expected.strip()
    }
```

#### 3-2. Class-based Scorer

```python
import weave
from weave import Scorer

class RelevanceScorer(Scorer):
    """Evaluate question-answer relevance"""

    threshold: float = 0.7  # Configurable parameter

    @weave.op
    def score(self, output: str, question: str) -> dict:
        # Calculate relevance score
        relevance_score = self._calculate_relevance(output, question)

        return {
            "relevance": relevance_score,
            "is_relevant": relevance_score >= self.threshold
        }

    def _calculate_relevance(self, output: str, question: str) -> float:
        # Implement actual relevance calculation
        # e.g., embedding similarity, keyword matching
        pass
```

#### 3-3. LLM Judge Scorer

```python
import weave
from weave import Scorer
from openai import OpenAI

class LLMJudgeScorer(Scorer):
    """Evaluate response quality using LLM"""

    model: str = "gpt-4o"
    criteria: str = "relevance"  # relevance, accuracy, helpfulness

    @weave.op
    def score(self, output: str, question: str) -> dict:
        client = OpenAI()

        prompt = f"""Evaluate the {self.criteria} of the following question and answer on a scale of 1-5.

Question: {question}
Answer: {output}

Respond in JSON format:
{{"score": <1-5>, "reason": "<evaluation reason>"}}
"""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return {
            "score": result["score"],
            "reason": result["reason"],
            "pass": result["score"] >= 4
        }
```

---

### Step 4: File Creation and Location

```
## Scorer Creation Complete

File to create:
- [src/scorers/relevance.py](src/scorers/relevance.py) (new file)

Or add to existing file:
- [src/evaluation.py](src/evaluation.py#L50) (below existing scorers)

Where would you like to create it?
```

---

### Step 5: Usage Guide

```
## Usage

### Using in Evaluation
```python
from weave import Evaluation
from src.scorers.relevance import LLMJudgeScorer

evaluation = Evaluation(
    dataset=my_dataset,
    scorers=[
        LLMJudgeScorer(criteria="relevance"),
        LLMJudgeScorer(criteria="accuracy"),
    ]
)

results = await evaluation.evaluate(my_model)
```

### Standalone Test
```python
scorer = LLMJudgeScorer(criteria="relevance")
result = scorer.score(
    output="Paris is the capital of France.",
    question="What is the capital of France?"
)
print(result)  # {"score": 5, "reason": "Correctly answered", "pass": True}
```

💡 Next step: Use `/create-eval` to set up a complete evaluation pipeline
```

---

## Template Library

### Correctness Evaluation
```python
@weave.op
def exact_match(output: str, expected: str) -> dict:
    return {"match": output.strip().lower() == expected.strip().lower()}

@weave.op
def contains_answer(output: str, expected: str) -> dict:
    return {"contains": expected.lower() in output.lower()}
```

### RAG Evaluation
```python
@weave.op
def context_precision(output: str, contexts: list[str]) -> dict:
    """Check if retrieved contexts are used in the answer"""
    used = sum(1 for ctx in contexts if ctx.lower() in output.lower())
    return {"precision": used / len(contexts) if contexts else 0}

@weave.op
def answer_faithfulness(output: str, contexts: list[str]) -> dict:
    """Check if answer is grounded in context (hallucination detection)"""
    # Recommend using LLM Judge
    pass
```

### Safety Evaluation
```python
@weave.op
def toxicity_check(output: str) -> dict:
    """Detect harmful content"""
    toxic_keywords = ["bad_word1", "bad_word2"]  # Use ML model in practice
    is_toxic = any(kw in output.lower() for kw in toxic_keywords)
    return {"is_safe": not is_toxic}
```

### Length/Format Evaluation
```python
@weave.op
def length_check(output: str, min_len: int = 10, max_len: int = 500) -> dict:
    length = len(output)
    return {
        "length": length,
        "in_range": min_len <= length <= max_len
    }

@weave.op
def json_valid(output: str) -> dict:
    try:
        json.loads(output)
        return {"valid_json": True}
    except:
        return {"valid_json": False}
```

---

## Built-in Scorers

Weave provides **9 built-in Scorers** for common evaluation needs.
Review these before implementing custom scorers.

```
## Built-in Scorer Recommendations

There are built-in Scorers that match your needs:

| Scorer | Purpose | Use Case |
|--------|---------|----------|
| `HallucinationFreeScorer` | Hallucination detection | RAG answer verification |
| `SummarizationScorer` | Summary quality | Summarization tasks |
| `OpenAIModerationScorer` | Harmful content | Safety checks |
| `EmbeddingSimilarityScorer` | Semantic similarity | Answer quality |
| `ValidJSONScorer` | JSON validation | Structured output |
| `ValidXMLScorer` | XML validation | Structured output |
| `PydanticScorer` | Schema validation | Type checking |
| `ContextEntityRecallScorer` | Entity recall | RAG retrieval quality |
| `ContextRelevancyScorer` | Context relevance | RAG retrieval quality |

Would you like to use a built-in Scorer or create a custom one?
```

### Built-in Scorer Usage Examples

```python
from weave.scorers import (
    HallucinationFreeScorer,
    SummarizationScorer,
    OpenAIModerationScorer,
    EmbeddingSimilarityScorer,
    ValidJSONScorer,
    ValidXMLScorer,
    PydanticScorer,
    ContextEntityRecallScorer,
    ContextRelevancyScorer,
)

# 1. Hallucination detection (RAG)
hallucination_scorer = HallucinationFreeScorer()

# 2. Summarization quality
summarization_scorer = SummarizationScorer()

# 3. Harmful content check (using OpenAI Moderation API)
moderation_scorer = OpenAIModerationScorer()

# 4. Embedding similarity
similarity_scorer = EmbeddingSimilarityScorer()

# 5. JSON validity check
json_scorer = ValidJSONScorer()

# 6. Pydantic schema validation
from pydantic import BaseModel

class FruitOutput(BaseModel):
    name: str
    color: str

pydantic_scorer = PydanticScorer(model=FruitOutput)

# 7. RAG context evaluation (RAGAS-based)
entity_recall_scorer = ContextEntityRecallScorer()
relevancy_scorer = ContextRelevancyScorer()
```

### Using Built-in Scorers in Evaluation

```python
import weave
from weave.scorers import HallucinationFreeScorer, ValidJSONScorer

evaluation = weave.Evaluation(
    dataset=my_dataset,
    scorers=[
        HallucinationFreeScorer(),
        ValidJSONScorer(),
    ]
)

results = await evaluation.evaluate(my_model)
```

---

## Important Notes

- The `score` method must return a `dict`
- Parameter names should match Dataset column names for automatic mapping
- Boolean values are automatically aggregated as count/fraction
- Numeric values are automatically averaged
