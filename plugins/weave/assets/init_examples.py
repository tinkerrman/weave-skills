"""
Weave Init Example Code

Based on official docs: https://docs.wandb.ai/weave/quickstart
"""

# ===== Basic Initialization =====

import weave

# Initialize with project name
weave.init("my-project")


# ===== With Team/Organization =====

weave.init("my-team/my-project")


# ===== With FastAPI =====

import weave
from fastapi import FastAPI

weave.init("my-api-project")

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


# ===== Environment-based Separation =====

import os
import weave

env = os.getenv("ENV", "dev")
weave.init(f"my-project-{env}")  # my-project-dev, my-project-prod


# ===== Conditional Initialization =====

import os
import weave

if os.getenv("WEAVE_ENABLED", "true").lower() == "true":
    weave.init("my-project")


# ===== CLI Script =====

import weave

def main():
    weave.init("my-cli-project")
    # ... main logic

if __name__ == "__main__":
    main()


# ===== Jupyter Notebook =====
# In the first cell:
# import weave
# weave.init("my-notebook-project")
