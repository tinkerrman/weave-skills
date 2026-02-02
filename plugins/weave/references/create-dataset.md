# Create Weave Dataset

This skill generates Weave Datasets for evaluation. It supports various data sources and transforms them into evaluation-ready formats.

**Related assets:** [dataset_examples.py](../assets/dataset_examples.py)

## Workflow

### Step 1: Identify Data Source

Determine the user's data source.

```
## Dataset Creation

Where is your data located?

| # | Source | Description |
|---|--------|-------------|
| 1 | **Manual input** | Write examples manually |
| 2 | **CSV file** | Local CSV file |
| 3 | **JSON file** | Local JSON/JSONL file |
| 4 | **Existing traces** | Execution logs recorded in Weave |
| 5 | **HuggingFace** | HuggingFace datasets |
| 6 | **Pandas DataFrame** | DataFrame from existing code |

Please provide a number.
```

---

### Step 2: Data Analysis and Preview

Analyze the structure of the selected source.

#### For CSV/JSON files:

```
## Data Analysis

File: data/eval_questions.csv

### Column Structure
| Column | Type | Example | Notes |
|--------|------|---------|-------|
| id | int | 1 | - |
| question | str | "What is the capital of France?" | ✅ Input |
| answer | str | "Paris" | ✅ Expected |
| category | str | "Geography" | Metadata |

### Preview (first 3 rows)
| question | answer | category |
|----------|--------|----------|
| What is the capital of France? | Paris | Geography |
| What is 1+1? | 2 | Math |
| Who created Python? | Guido van Rossum | IT |

Total: 50 rows

### Column Mapping Suggestion
- `question` → Model input (parameter for predict)
- `answer` → Expected answer (referenced as `expected` in Scorer)
- `category` → Metadata (optional)

Proceed with this configuration? Or would you like to rename columns?
```

#### For creating from existing traces:

```
## Trace Analysis

Weave Project: my-rag-app

### Recent Traces
| Function | Call Count | Input | Output |
|----------|------------|-------|--------|
| [RAGModel.predict](weave://...) | 1,234 | question: str | answer: str |
| [call_openai](weave://...) | 2,500 | prompt: str | response: str |

### Selection
Which traces would you like to convert to a dataset?
- [1] RAGModel.predict (recent 100)
- [2] Specify filter conditions (date, status, etc.)

→ Selection: 1
```

---

### Step 3: Generate Dataset Code

#### Direct Definition

```python
# src/data/eval_dataset.py

import weave

# Define Dataset
qa_dataset = weave.Dataset(
    name="qa-eval-v1",
    rows=[
        {"question": "What is the capital of France?", "expected": "Paris"},
        {"question": "What is 1+1?", "expected": "2"},
        {"question": "Who created Python?", "expected": "Guido van Rossum"},
        # Add more examples...
    ]
)

# Publish to Weave (version controlled)
weave.publish(qa_dataset)
```

#### Load from CSV

```python
# src/data/eval_dataset.py

import weave
import pandas as pd

# Load CSV
df = pd.read_csv("data/eval_questions.csv")

# Column mapping (if needed)
df = df.rename(columns={
    "answer": "expected"  # Rename for Scorer reference
})

# Create Dataset
qa_dataset = weave.Dataset(
    name="qa-eval-v1",
    rows=df.to_dict("records")
)

# Publish to Weave
weave.publish(qa_dataset)
```

#### Load from JSON/JSONL

```python
# src/data/eval_dataset.py

import weave
import json

# Load JSONL
rows = []
with open("data/eval_questions.jsonl") as f:
    for line in f:
        rows.append(json.loads(line))

# Create Dataset
qa_dataset = weave.Dataset(
    name="qa-eval-v1",
    rows=rows
)

weave.publish(qa_dataset)
```

#### Create from Traces

```python
# src/data/eval_dataset.py

import weave

weave.init("my-rag-app")
client = weave.get_client()

# Query traces
calls = client.get_calls(
    filter={
        "op_name": "RAGModel.predict",
        "started_at": {"$gte": "2024-01-01"},
    },
    limit=100
)

# Convert to Dataset
rows = []
for call in calls:
    rows.append({
        "question": call.inputs["question"],
        "expected": call.output,  # Use actual output as expected
    })

qa_dataset = weave.Dataset(
    name="qa-from-traces-v1",
    rows=rows
)

weave.publish(qa_dataset)
```

#### Load from HuggingFace

```python
# src/data/eval_dataset.py

import weave
from datasets import load_dataset

# Load HuggingFace dataset
hf_dataset = load_dataset("squad", split="validation[:100]")

# Convert to Weave Dataset
rows = [
    {
        "question": item["question"],
        "context": item["context"],
        "expected": item["answers"]["text"][0],
    }
    for item in hf_dataset
]

qa_dataset = weave.Dataset(
    name="squad-eval-v1",
    rows=rows
)

weave.publish(qa_dataset)
```

---

### Step 4: File Creation Confirmation

```
## Dataset Creation Complete

File to create:
- [src/data/eval_dataset.py](src/data/eval_dataset.py) (new file)

### Dataset to be Created
- Name: `qa-eval-v1`
- Rows: 50
- Columns: question, expected, category

Proceed?
```

---

### Step 5: Completion and Next Steps

```
## Complete

✅ Dataset created

### Created File
- [src/data/eval_dataset.py](src/data/eval_dataset.py)

### To Publish to Weave
```python
python src/data/eval_dataset.py
```

After publishing, view at: https://wandb.ai/weave/<project>/datasets

### Using in Code
```python
from src.data.eval_dataset import qa_dataset

# Or load from Weave
dataset = weave.ref("qa-eval-v1:latest").get()
```

### Next Steps
1. **Run evaluation** - Set up evaluation pipeline with `/create-eval`
2. **Add data** - Add more examples
3. **Version control** - Publishing after modifications creates a new version
```

---

## Advanced Options

### Partial Selection
```python
# Filter by condition
filtered = qa_dataset.select(
    lambda row: row["category"] == "Geography"
)
```

### Data Validation
```python
# Check required columns
required_columns = ["question", "expected"]
for col in required_columns:
    assert col in qa_dataset.rows[0], f"Missing column: {col}"
```

### Version References
```python
# Load specific version
dataset_v1 = weave.ref("qa-eval-v1:v0").get()
dataset_latest = weave.ref("qa-eval-v1:latest").get()
```

---

## Column Naming Guide

For automatic mapping in evaluation:

| Purpose | Recommended Column Names | Description |
|---------|--------------------------|-------------|
| Model input | `question`, `input`, `prompt` | Match Model.predict() parameters |
| Expected answer | `expected`, `answer`, `label` | Referenced by Scorer |
| Context (RAG) | `context`, `contexts` | Retrieved documents |
| Metadata | `category`, `source`, `difficulty` | For analysis |

---

## Important Notes

- Dataset names: only alphanumeric, hyphens, and underscores allowed
- Large datasets may take time to publish
- Mask sensitive data (PII) before publishing
- Column names cannot contain spaces
