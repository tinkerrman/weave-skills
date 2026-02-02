---
name: weave
description: W&B Weave integration for LLM observability and evaluation. Initialize projects, add tracing, create scorers, build evaluation pipelines, and manage datasets.
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

## Workflow

### 1. Analyze Request

When user's request is **clear**, read the appropriate reference and follow its workflow.

When user's request is **ambiguous** (e.g., "add weave", "set up observability"):

1. Scan codebase for patterns:
   ```
   Grep: "weave.init" → check if already initialized
   Grep: "@weave.op" → check existing tracing
   Grep: "weave.Evaluation" → check existing evaluation
   Glob: "**/*scorer*.py", "**/*eval*.py" → find related files
   ```

2. Based on analysis, recommend features:
   ```
   ## Weave Integration Analysis

   | Status | Feature | Recommendation |
   |--------|---------|----------------|
   | ⚠️ Not found | weave.init() | Initialize first |
   | ⚠️ 0 functions | @weave.op tracing | Add to LLM calls |
   | ✅ Found | Scorers | 2 scorers exist |
   | ⚠️ Not found | Evaluation pipeline | Create after tracing |

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

### 3. Suggest Complementary Features

After completing a feature, check if related features would be useful:

| Completed | Suggest Next | Condition |
|-----------|--------------|-----------|
| init | add-tracing | No @weave.op found |
| add-tracing | init | No weave.init() found |
| add-tracing | create-eval | Model exists, no evaluation |
| create-scorer | create-eval | Scorers exist, no evaluation |
| create-dataset | create-eval | Dataset exists, no evaluation |
| create-eval | All complete | - |

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
- Scorers: 2 custom scorers
- Evaluation: Not configured

### Recommendations
1. Add tracing to 4 more LLM-calling functions
2. Create evaluation pipeline with existing scorers
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

### Built-in Scorers
`HallucinationFreeScorer`, `ValidJSONScorer`, `PydanticScorer`, `EmbeddingSimilarityScorer`, `OpenAIModerationScorer`

---

## Resources

- [Weave Docs](https://docs.wandb.ai/weave)
- [W&B Dashboard](https://wandb.ai/weave)
