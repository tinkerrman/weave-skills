"""
Weave Dataset Example Code

Based on official docs: https://docs.wandb.ai/weave/guides/core-types/datasets
"""

import weave

weave.init("dataset-examples")


# ===== 1. Direct Definition =====

# Inline list
inline_dataset = [
    {"question": "What is Python?", "expected": "A programming language"},
    {"question": "What is FastAPI?", "expected": "A web framework"},
]

# weave.Dataset object
qa_dataset = weave.Dataset(
    name="qa-dataset-v1",
    rows=[
        {"question": "What is the capital of France?", "expected": "Paris"},
        {"question": "What is 2 + 2?", "expected": "4"},
        {"question": "Who created Python?", "expected": "Guido van Rossum"},
    ]
)


# ===== 2. Load from CSV =====

def load_from_csv(filepath: str) -> weave.Dataset:
    """Create Dataset from CSV file"""
    import pandas as pd

    df = pd.read_csv(filepath)

    # Column name mapping (if needed)
    # df = df.rename(columns={"answer": "expected"})

    return weave.Dataset(
        name="csv-dataset-v1",
        rows=df.to_dict("records")
    )


# ===== 3. Load from JSON/JSONL =====

def load_from_jsonl(filepath: str) -> weave.Dataset:
    """Create Dataset from JSONL file"""
    import json

    rows = []
    with open(filepath, "r") as f:
        for line in f:
            rows.append(json.loads(line))

    return weave.Dataset(
        name="jsonl-dataset-v1",
        rows=rows
    )


def load_from_json(filepath: str) -> weave.Dataset:
    """Create Dataset from JSON file"""
    import json

    with open(filepath, "r") as f:
        data = json.load(f)

    # If data is a list
    if isinstance(data, list):
        rows = data
    # If data is a dict with a list under a specific key
    else:
        rows = data.get("examples", data.get("data", []))

    return weave.Dataset(
        name="json-dataset-v1",
        rows=rows
    )


# ===== 4. Load from HuggingFace =====

def load_from_huggingface(dataset_name: str, split: str = "validation[:100]") -> weave.Dataset:
    """Load from HuggingFace datasets"""
    from datasets import load_dataset

    hf_dataset = load_dataset(dataset_name, split=split)

    # SQuAD example
    rows = [
        {
            "question": item["question"],
            "context": item["context"],
            "expected": item["answers"]["text"][0] if item["answers"]["text"] else "",
        }
        for item in hf_dataset
    ]

    return weave.Dataset(
        name=f"{dataset_name.replace('/', '-')}-v1",
        rows=rows
    )


# ===== 5. Convert from Pandas DataFrame =====

def from_dataframe(df, name: str = "df-dataset-v1") -> weave.Dataset:
    """Create Dataset from Pandas DataFrame"""
    return weave.Dataset(
        name=name,
        rows=df.to_dict("records")
    )


# ===== 6. Create from Traces =====

def from_traces(project_name: str, op_name: str, limit: int = 100) -> weave.Dataset:
    """Create Dataset from existing traces"""
    client = weave.init(project_name)

    # Query traces
    calls = client.get_calls(
        filter={"op_name": op_name},
        limit=limit
    )

    # Convert to Dataset
    rows = []
    for call in calls:
        rows.append({
            "input": call.inputs,
            "output": call.output,
        })

    return weave.Dataset(
        name=f"traces-{op_name}-v1",
        rows=rows
    )


# ===== 7. Publish Dataset =====

def publish_dataset():
    """Publish Dataset to Weave (version controlled)"""
    dataset = weave.Dataset(
        name="my-eval-dataset",
        rows=[
            {"question": "Q1", "expected": "A1"},
            {"question": "Q2", "expected": "A2"},
        ]
    )

    # Publish
    weave.publish(dataset)

    print(f"Published: {dataset.name}")
    return dataset


# ===== 8. Load Dataset =====

def load_published_dataset(name: str, version: str = "latest"):
    """Load published Dataset"""
    # Latest version
    dataset = weave.ref(f"{name}:{version}").get()
    return dataset


# ===== 9. Filter Dataset =====

def filter_dataset(dataset: weave.Dataset, condition):
    """Filter Dataset"""
    filtered_rows = [row for row in dataset.rows if condition(row)]
    return weave.Dataset(
        name=f"{dataset.name}-filtered",
        rows=filtered_rows
    )


# Usage example
# filtered = filter_dataset(qa_dataset, lambda row: len(row["question"]) > 20)


# ===== 10. RAG Evaluation Dataset Example =====

rag_eval_dataset = weave.Dataset(
    name="rag-eval-v1",
    rows=[
        {
            "question": "What is RAG?",
            "context": "RAG (Retrieval-Augmented Generation) combines retrieval and generation.",
            "expected": "RAG is a technique that combines retrieval and generation.",
        },
        {
            "question": "What is a vector database?",
            "context": "Vector databases store embeddings and enable similarity search.",
            "expected": "A database for storing embeddings and performing similarity search.",
        },
    ]
)


if __name__ == "__main__":
    # Dataset creation test
    print("=== QA Dataset ===")
    print(f"Name: {qa_dataset.name}")
    print(f"Rows: {len(qa_dataset.rows)}")
    for row in qa_dataset.rows:
        print(f"  - {row['question']}")

    # Publish test (when actually running)
    # publish_dataset()
