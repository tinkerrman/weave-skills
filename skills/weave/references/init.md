# Initialize Weave Project

This skill initializes a Weave project by analyzing the codebase, finding the optimal entry point, and configuring `weave.init()`.

**Related assets:** [init_examples.py](../assets/init_examples.py)

## Workflow

### Step 1: Project Structure Analysis

Analyze the codebase to find entry point candidates.

**Analysis targets:**
- Main files: `main.py`, `app.py`, `run.py`
- `if __name__ == "__main__":` blocks
- FastAPI/Flask app initialization
- CLI entry points (click, argparse, typer)
- Existing `weave.init()` calls

**Output format:**

```
## Project Analysis Results

### Detected Frameworks
- FastAPI (src/main.py)
- Python CLI (src/cli.py)

### Entry Point Candidates

| # | File | Location | Type | Recommendation |
|---|------|----------|------|----------------|
| 1 | [main.py](src/main.py#L1) | L1 (module top) | FastAPI app | ⭐⭐⭐ |
| 2 | [cli.py](src/cli.py#L45) | L45 (`if __name__`) | CLI | ⭐⭐ |
| 3 | [run.py](run.py#L10) | L10 | Script | ⭐⭐ |

### Current Settings
- ⚠️ No weave.init() found
- ✅ WANDB_API_KEY environment variable detected
```

---

### Step 2: Project Settings Input

**Collect entity and project name from the user.**

```
## Weave Project Settings

Please provide the required information for weave.init().

### Required Input

| Field | Description | Example |
|-------|-------------|---------|
| **entity** | W&B team or username | `my-team`, `username` |
| **project** | Project name | `rag-app`, `chatbot-v1` |

> 💡 You can find your entity at https://wandb.ai/settings

### Input
- entity: _______
- project: _______ (suggested: `my-llm-app` based on folder name)

### Initialization Location
- Suggested: [src/main.py](src/main.py#L1) (before FastAPI app creation)

### Environment Settings
- WANDB_API_KEY: ✅ Configured
- (or) ⚠️ API key required - get it at https://wandb.ai/authorize
```

**Input example:**
- entity: `hyunwoo`
- project: `rag-qa-demo`
→ `weave.init("hyunwoo/rag-qa-demo")`

---

### Step 3: Apply Initialization Code

Generate code with the user-provided entity/project.

**FastAPI example:**
```python
import weave
from fastapi import FastAPI

weave.init("{entity}/{project}")  # e.g., "hyunwoo/rag-qa-demo"

app = FastAPI()
```

**CLI script example:**
```python
import weave

def main():
    weave.init("{entity}/{project}")
    # ... rest of the code

if __name__ == "__main__":
    main()
```

**Jupyter Notebook example:**
```python
import weave
weave.init("{entity}/{project}")
```

> Note: You can also use just the project name without entity: `weave.init("project-name")`

---

### Step 4: Completion and Next Steps

```
## Complete

✅ Weave initialization complete

Changed files:
- [src/main.py](src/main.py#L3) - weave.init() added

### Next Steps

1. **Add tracing** - Use `/add-tracing` to add @weave.op to functions
2. **Check dashboard** - View your project at https://wandb.ai/weave
3. **Set API key** (if needed):
   ```bash
   export WANDB_API_KEY="your-api-key"
   ```

💡 Traces will be automatically recorded when you run your app!
```

---

## Framework-specific Recommendations

| Framework | Recommended Location | Notes |
|-----------|---------------------|-------|
| FastAPI | Before app creation (module top) | Can use lifespan events |
| Flask | Before `app = Flask()` | |
| Django | settings.py or wsgi.py | |
| CLI (click/typer) | Start of main function | |
| Jupyter | First cell | |
| Script | Inside `if __name__` block | |

---

## Advanced Options

Available upon user request:

### Environment-based Project Separation
```python
import os
import weave

env = os.getenv("ENV", "dev")
weave.init(f"my-app-{env}")  # my-app-dev, my-app-prod
```

### Conditional Initialization
```python
import os
import weave

if os.getenv("WEAVE_ENABLED", "true").lower() == "true":
    weave.init("my-app")
```

---

## Important Notes

- `weave.init()` should only be called once per process
- In multiprocess environments, initialize in each process
- Without API key, runs in local mode (no W&B dashboard sync)
