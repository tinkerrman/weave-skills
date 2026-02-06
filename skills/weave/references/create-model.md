# Create Weave Model

This skill generates `weave.Model` subclasses with typed attributes and a `predict()` method. It analyzes the codebase for existing functions that could be wrapped as Models.

**Related assets:** [model_examples.py](../assets/model_examples.py)

## Workflow

### Step 1: Codebase Analysis

Analyze the codebase to find existing functions/classes suitable for Model wrapping.

**Analysis targets:**
- Existing `weave.Model` subclasses
- LLM API call functions (OpenAI, Anthropic, Cohere, etc.)
- Functions decorated with `@weave.op`
- Classes with `predict`, `generate`, `invoke` methods
- Hardcoded model configurations (model names, temperatures, etc.)

**Output format:**

```
## Model Analysis Results

### Existing Models
- ⚠️ No weave.Model subclasses found

### Candidate Functions
| # | Function | Location | Type | Recommendation |
|---|----------|----------|------|----------------|
| 1 | [call_openai()](src/llm.py#L15) | L15-L28 | LLM call | ⭐⭐⭐ Wrap as Model |
| 2 | [generate()](src/pipeline.py#L10) | L10-L35 | Pipeline | ⭐⭐⭐ Wrap as Model |
| 3 | [embed()](src/utils.py#L5) | L5-L20 | Utility | ⭐ Keep as function |

### Detected Configuration
- model: "gpt-4o-mini" (src/llm.py:5)
- temperature: 0.7 (src/llm.py:6)
- max_tokens: 1000 (src/llm.py:7)

Would you like to wrap an existing function or create a new Model?
```

---

### Step 2: Model Type Selection

Suggest a Model type based on the analysis.

```
## Model Type Selection

| Type | Recommended For | Characteristics |
|------|-----------------|-----------------|
| **Basic** | Simple function wrapper | Minimal, just predict() |
| **Configurable** | Tunable parameters | Typed attributes auto-versioned |
| **RAG** | Retrieval + generation | retrieve() + predict() methods |
| **Wrap existing** | Existing function → Model | Minimal change to existing code |

Suggestion: **Configurable Model** (detected hardcoded config values)

Would you like to proceed with this type?
```

---

### Step 3: Generate Model Code

Generate code based on the selected type.

#### 3-1. Basic Model

```python
import weave
from weave import Model

class MyModel(Model):
    """Simple model"""

    @weave.op()
    def predict(self, question: str) -> str:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}],
        )
        return response.choices[0].message.content
```

#### 3-2. Configurable Model

```python
import weave
from weave import Model

class MyModel(Model):
    """Model with versioned configuration"""

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
```

#### 3-3. RAG Model

```python
import weave
from weave import Model

class RAGModel(Model):
    """Retrieval-Augmented Generation model"""

    model_name: str = "gpt-4o-mini"
    top_k: int = 3

    @weave.op()
    def retrieve(self, query: str) -> list[str]:
        """Retrieve relevant documents"""
        # Replace with actual retrieval logic
        pass

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
```

#### 3-4. Wrap Existing Function

```python
import weave
from weave import Model

# Existing function (unchanged)
def existing_llm_call(question: str) -> str:
    ...

# New Model wrapper
class WrappedModel(Model):
    """Wrapping an existing function as a Model"""

    @weave.op()
    def predict(self, question: str) -> str:
        return existing_llm_call(question)
```

---

### Step 4: File Creation and Location

```
## File Creation

File to create:
- [src/models/my_model.py](src/models/my_model.py) (new file)

Or add to existing file:
- [src/llm.py](src/llm.py#L1) (add Model class)

Where would you like to create it?
```

---

### Step 5: Completion and Next Steps

```
## Complete

✅ weave.Model created

Created files:
- [src/models/my_model.py](src/models/my_model.py) - MyModel class

### Usage
```python
from src.models.my_model import MyModel

model = MyModel(temperature=0.0)
result = model.predict("What is Python?")
```

### Next Steps

1. **Run evaluation** - Use `/create-eval` to evaluate your model
2. **Add prompts** - Use `/create-prompt` to version your prompts
3. **Compare configs** - Change attributes to auto-create new versions:
   ```python
   model_v1 = MyModel(temperature=0.0)
   model_v2 = MyModel(temperature=1.0)
   ```
4. **View in dashboard** - https://wandb.ai/weave/<project>
```

---

## Advanced Options

Available upon request:

### Model Comparison in Evaluation

```python
import asyncio
from weave import Evaluation

models = [
    MyModel(model_name="gpt-4o-mini", temperature=0.0),
    MyModel(model_name="gpt-4o", temperature=0.0),
]

evaluation = Evaluation(dataset=dataset, scorers=[my_scorer])

for model in models:
    results = asyncio.run(evaluation.evaluate(model))
    print(f"{model.model_name}: {results}")
```

### Production Tracking with Attributes

```python
with weave.attributes({"env": "production", "version": "v1.2"}):
    result = model.predict("user question")
```

### Serving a Model

```bash
# Deploy as FastAPI endpoint
pip install fastapi uvicorn
weave serve weave:///entity/project/MyModel:<hash>
# → http://0.0.0.0:9996/docs
```

---

## Important Notes

- `predict()` method is **required** and must be decorated with `@weave.op()`
- All typed attributes (with type annotations) are **automatically versioned** by Weave
- Changing attribute values or `predict()` code creates a **new version**
- Attributes must be JSON-serializable types (`str`, `int`, `float`, `bool`, `list`, `dict`)
- `weave.Model` inherits from Pydantic `BaseModel` — standard Pydantic validation applies
- The Model class is the standard input to `weave.Evaluation.evaluate(model)`
