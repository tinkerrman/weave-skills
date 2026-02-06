---
name: weave
description: W&B Weave integration for LLM observability and evaluation. Initialize projects, add tracing, create models, manage prompts, create scorers, build evaluation pipelines, manage datasets, and add production guardrails.
---

# W&B Weave Integration

This skill provides comprehensive W&B Weave support for LLM observability and evaluation.

## Request Classification

| Keywords | Feature | Reference | Assets |
|----------|---------|-----------|--------|
| init, initialize, setup, weave.init | Project initialization | [init.md](references/init.md) | [init_examples.py](assets/init_examples.py) |
| trace, tracing, @weave.op, decorator | Add tracing | [add-tracing.md](references/add-tracing.md) | [tracing_examples.py](assets/tracing_examples.py) |
| scorer, score, evaluate metric, judge | Create scorer | [create-scorer.md](references/create-scorer.md) | [scorer_examples.py](assets/scorer_examples.py) |
| eval, evaluation, pipeline, benchmark | Create evaluation | [create-eval.md](references/create-eval.md) | [eval_examples.py](assets/eval_examples.py) |
| dataset, data, csv, json, examples | Create dataset | [create-dataset.md](references/create-dataset.md) | [dataset_examples.py](assets/dataset_examples.py) |
| model, weave.Model, predict, Model class | Create model | [create-model.md](references/create-model.md) | [model_examples.py](assets/model_examples.py) |
| prompt, StringPrompt, MessagesPrompt, template, versioning | Create prompt | [create-prompt.md](references/create-prompt.md) | [prompt_examples.py](assets/prompt_examples.py) |
| guardrail, guard, monitor, online eval, safety, production | Add guardrails | [add-guardrails.md](references/add-guardrails.md) | [guardrail_examples.py](assets/guardrail_examples.py) |

## Workflow

### 1. Analyze Request

When user's request is **clear**, read the appropriate reference and follow its workflow.

When user's request is **ambiguous** (e.g., "add weave", "set up observability"):

1. Scan codebase for patterns:
   ```
   Grep: "weave.init" → check if already initialized
   Grep: "@weave.op" → check existing tracing
   Grep: "weave.Model" → check existing models
   Grep: "StringPrompt\|MessagesPrompt" → check existing prompts
   Grep: "weave.Evaluation" → check existing evaluation
   Grep: "apply_scorer" → check existing guardrails
   Glob: "**/*scorer*.py", "**/*eval*.py", "**/*model*.py" → find related files
   ```

2. Based on analysis, recommend features:
   ```
   ## Weave Integration Analysis

   | Status | Feature | Recommendation |
   |--------|---------|----------------|
   | ⚠️ Not found | weave.init() | Initialize first |
   | ⚠️ 0 functions | @weave.op tracing | Add to LLM calls |
   | ⚠️ Not found | weave.Model | Create model class |
   | ⚠️ Not found | Prompts | Create versioned prompts |
   | ✅ Found | Scorers | 2 scorers exist |
   | ⚠️ Not found | Evaluation pipeline | Create after tracing |
   | ⚠️ Not found | Guardrails | Add production guardrails |

   Which would you like to start with?
   ```

3. If still unclear, ask user to choose from available features.

### 2. Execute Feature

Read the appropriate reference file and follow its step-by-step workflow:

- **init**: Analyze entry points → collect entity/project → apply code
- **add-tracing**: Analyze functions → propose candidates → apply decorators
- **create-scorer**: Identify goal → select type → generate code
- **create-eval**: Find components → configure pipeline → generate script
- **create-dataset**: Identify source → analyze structure → generate code
- **create-model**: Analyze codebase → select type → generate Model class
- **create-prompt**: Discover prompts → select type → generate code → publish
- **add-guardrails**: Find scorers → select pattern → generate integration

### 3. Suggest Complementary Features

After completing a feature, check if related features would be useful:

| Completed | Suggest Next | Condition |
|-----------|--------------|-----------|
| init | add-tracing | No @weave.op found |
| add-tracing | init | No weave.init() found |
| add-tracing | create-model | Functions suitable for wrapping |
| add-tracing | create-eval | Model exists, no evaluation |
| create-model | create-eval | No evaluation pipeline |
| create-model | create-prompt | Hardcoded prompts found |
| create-prompt | create-model | No model exists |
| create-scorer | create-eval | Scorers exist, no evaluation |
| create-scorer | add-guardrails | Scorers exist, production context |
| create-dataset | create-eval | Dataset exists, no evaluation |
| create-eval | add-guardrails | Evaluation exists, production context |
| add-guardrails | - | All complete for production |

Example prompt after completing init:
```
✅ weave.init() added to main.py

💡 Next: I found 5 LLM-calling functions without tracing.
   Would you like to add @weave.op to them?
```

---

## Read-Only Analysis

For analysis/scan requests that don't modify files:

**Keywords**: "analyze", "scan", "check", "status", "what needs"

**⚠️ DO NOT modify files for these requests.**

Output analysis results only:

```
## Weave Integration Status

### Current State
- weave.init(): ✅ Found in main.py:3
- @weave.op: 3 functions traced
- weave.Model: 1 model class
- Prompts: Not managed
- Scorers: 2 custom scorers
- Evaluation: Not configured
- Guardrails: Not configured

### Recommendations
1. Add tracing to 4 more LLM-calling functions
2. Create versioned prompts from hardcoded strings
3. Create evaluation pipeline with existing scorers
4. Add guardrails for production safety
```

---

## Quick Reference

### weave.init()
```python
import weave
weave.init("entity/project")  # or just "project"
```

### @weave.op
```python
@weave.op
def my_function():
    ...
```

### Evaluation
```python
evaluation = weave.Evaluation(dataset=data, scorers=[scorer])
results = await evaluation.evaluate(model)
```

### weave.Model
```python
class MyModel(weave.Model):
    model_name: str = "gpt-4o-mini"

    @weave.op
    def predict(self, question: str) -> str:
        ...
```

### Prompts
```python
prompt = weave.StringPrompt("Answer: {question}")
weave.publish(prompt, name="my-prompt")
prompt = weave.ref("my-prompt:latest").get()
```

### Guardrails
```python
result, call = my_op.call(input)
score = await call.apply_scorer(my_scorer)
```

### Built-in Scorers
`HallucinationFreeScorer`, `ValidJSONScorer`, `PydanticScorer`, `EmbeddingSimilarityScorer`, `OpenAIModerationScorer`

---

## Resources

- [Weave Docs](https://docs.wandb.ai/weave)
- [W&B Dashboard](https://wandb.ai/weave)
