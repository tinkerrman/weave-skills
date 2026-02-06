# Create Weave Prompt

This skill creates and manages versioned prompts using Weave's prompt management system. It supports `StringPrompt`, `MessagesPrompt`, and custom `Prompt` subclasses with parameterization and version control.

**Related assets:** [prompt_examples.py](../assets/prompt_examples.py)

## Workflow

### Step 1: Prompt Discovery and Analysis

Analyze the codebase for existing prompts and LLM message patterns.

**Analysis targets:**
- Hardcoded prompt strings (f-strings, triple-quoted strings)
- Message arrays (`[{"role": "system", ...}]`)
- Existing `weave.StringPrompt`, `weave.MessagesPrompt`
- Template patterns (`{variable}`, `.format()`)

**Output format:**

```
## Prompt Analysis Results

### Existing Prompts
| # | Location | Current Form | Type | Parameterized? |
|---|----------|-------------|------|----------------|
| 1 | [llm.py:15](src/llm.py#L15) | `f"Answer: {question}"` | Inline f-string | ✅ |
| 2 | [llm.py:25](src/llm.py#L25) | `[{"role": "system", ...}]` | Message array | ❌ Hardcoded |
| 3 | [scorer.py:10](src/scorer.py#L10) | `"""Evaluate..."""` | Triple-quoted | ❌ Hardcoded |

### Weave Prompts
- ⚠️ No weave.StringPrompt or MessagesPrompt found

### Recommendation
3 prompts found that would benefit from version management.
Would you like to convert them to Weave prompts?
```

---

### Step 2: Prompt Type Selection

Suggest a type based on the detected pattern.

```
## Prompt Type Selection

| Type | Recommended For | Characteristics |
|------|-----------------|-----------------|
| **StringPrompt** | Single template string | Simple, `{var}` substitution |
| **MessagesPrompt** | Chat message arrays | Multi-role (system/user/assistant) |
| **Custom Prompt** | Complex formatting logic | Subclass with `format()` override |

### When to Use Each
- **StringPrompt**: System prompts, user queries, evaluation prompts
- **MessagesPrompt**: Chat applications, multi-turn templates
- **Custom Prompt**: Conditional sections, dynamic assembly

Suggestion: **MessagesPrompt** (chat message array detected)

Would you like to proceed with this type?
```

---

### Step 3: Generate Prompt Code

Provide templates based on selection.

#### 3-1. StringPrompt

```python
import weave

# Simple template with parameters
qa_prompt = weave.StringPrompt(
    "Answer the following question concisely.\n\n"
    "Question: {question}\n\nAnswer:"
)

# Use the prompt
formatted = qa_prompt.format(question="What is Python?")
```

#### 3-2. MessagesPrompt

```python
import weave

# Chat template with role-based messages
chat_prompt = weave.MessagesPrompt([
    {"role": "system", "content": "You are a helpful {domain} expert."},
    {"role": "user", "content": "{question}"},
])

# Use the prompt
messages = chat_prompt.format(domain="Python", question="What is a decorator?")
```

#### 3-3. Custom Prompt Subclass

```python
import weave

class RAGPrompt(weave.Prompt):
    """Custom prompt with conditional context handling"""

    context_header: str = "Use the following context to answer:"

    def format(self, question: str, contexts: list[str] = None) -> str:
        if contexts:
            context_str = "\n".join(f"- {c}" for c in contexts)
            return f"{self.context_header}\n{context_str}\n\nQuestion: {question}\nAnswer:"
        return f"Question: {question}\nAnswer:"
```

---

### Step 4: Publishing and Versioning

```
## Publishing and Version Control

### Publish
```python
import weave

weave.init("my-project")

prompt = weave.StringPrompt("Answer: {question}")
weave.publish(prompt, name="my-qa-prompt")
```

### Retrieve
```python
# Latest version
prompt = weave.ref("my-qa-prompt:latest").get()

# Specific version
prompt_v0 = weave.ref("my-qa-prompt:v0").get()
```

### Version Tracking
- Each `weave.publish()` with same name creates a **new version**
- Versions are immutable once published
- View version history in W&B dashboard → Assets → Prompts

### Using in Models
```python
class MyModel(weave.Model):
    prompt_name: str = "my-qa-prompt"

    @weave.op()
    def predict(self, question: str) -> str:
        prompt = weave.ref(f"{self.prompt_name}:latest").get()
        formatted = prompt.format(question=question)
        # Use formatted prompt with LLM...
```
```

---

### Step 5: Completion and Next Steps

```
## Complete

✅ Weave prompt created and published

Created files:
- [src/prompts.py](src/prompts.py) - Prompt definitions

### Published Prompts
| Name | Type | Parameters | Version |
|------|------|-----------|---------|
| my-qa-prompt | StringPrompt | question | v0 |

### Next Steps

1. **Create Model** - Use `/create-model` to build a Model that uses your prompts
2. **Iterate versions** - Modify and re-publish to create new versions
3. **View in dashboard** - https://wandb.ai/weave/<project> → Assets → Prompts

💡 Use `weave.ref("prompt-name:latest").get()` in production to always load the newest version!
```

---

## Advanced Options

Available upon request:

### A/B Testing Prompts in Evaluation

```python
import asyncio
from weave import Model, Evaluation

class PromptModel(Model):
    prompt_version: str = "latest"

    @weave.op()
    def predict(self, question: str) -> str:
        prompt = weave.ref(f"my-qa-prompt:{self.prompt_version}").get()
        formatted = prompt.format(question=question)
        # Use formatted prompt with LLM...

# Compare prompt versions
models = [
    PromptModel(prompt_version="v0"),
    PromptModel(prompt_version="v1"),
]

evaluation = Evaluation(dataset=dataset, scorers=[my_scorer])
for model in models:
    results = asyncio.run(evaluation.evaluate(model))
```

### Environment-specific Prompts

```python
import os

env = os.getenv("ENV", "dev")
prompt = weave.ref(f"my-prompt-{env}:latest").get()
```

### Evaluation Scorer Prompts

```python
# Version-manage your LLM judge prompts
judge_prompt = weave.StringPrompt(
    "Evaluate the {criteria} of the response on a scale of 1-5.\n\n"
    "Question: {question}\nResponse: {response}\n\n"
    'JSON: {{"score": <1-5>, "reason": "<explanation>"}}'
)
weave.publish(judge_prompt, name="judge-prompt")
```

---

## Important Notes

- Prompt names: alphanumeric, hyphens, and underscores only
- Parameters use Python `.format()` style `{name}` placeholders
- Published prompts are **immutable** — modifications create new versions
- `weave.ref()` requires `weave.init()` to be called first
- `StringPrompt.format()` returns a `str`
- `MessagesPrompt.format()` returns a `list[dict]` (OpenAI-compatible messages)
- Custom `Prompt` subclasses must implement `format()` method
