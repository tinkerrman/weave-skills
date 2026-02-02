# Add Weave Tracing

This skill analyzes the codebase to identify functions that would benefit from Weave tracing (`@weave.op`), proposes candidates for user review, and applies the decorators upon confirmation.

**Related assets:** [tracing_examples.py](../assets/tracing_examples.py)

## Workflow

### Step 1: Codebase Structure Analysis

Analyze the **complete function structure** of the user-specified directory or files.

**Output format:**

```
## Codebase Analysis Results

### src/llm.py
| Function | Location | Type | Description |
|----------|----------|------|-------------|
| [call_openai()](src/llm.py#L15) | L15-L28 | async | OpenAI API call |
| [call_anthropic()](src/llm.py#L30) | L30-L45 | sync | Anthropic API call |
| [_parse_response()](src/llm.py#L47) | L47-L52 | sync | Response parsing (private) |

### src/pipeline.py
| Function | Location | Type | Description |
|----------|----------|------|-------------|
| [process_data()](src/pipeline.py#L10) | L10-L35 | sync | Data preprocessing |
| [run_pipeline()](src/pipeline.py#L40) | L40-L80 | async | Main pipeline execution |

### src/utils.py
| Function | Location | Type | Description |
|----------|----------|------|-------------|
| [format_output()](src/utils.py#L5) | L5-L10 | sync | Output formatting |
| [fetch_from_api()](src/utils.py#L12) | L12-L25 | async | External API call |

Total: 7 functions found
```

**Click links to navigate directly to the line.**

---

### Step 2: Tracing Candidates Proposal

Propose functions for tracing from the analyzed codebase.

**Recommendation criteria (by priority):**
1. ⭐⭐⭐ LLM API calls (OpenAI, Anthropic, Cohere, etc.)
2. ⭐⭐⭐ Core business logic (predict, generate, process, run, etc.)
3. ⭐⭐ External API/DB calls
4. ⭐⭐ Data transformation/preprocessing functions
5. ⭐ Computationally expensive operations

**Exclusions:**
- Functions already decorated with `@weave.op`
- Simple utilities (getters/setters, formatting)
- Test functions

**Output format:**

```
## Tracing Recommendations

The following functions are recommended for `@weave.op` tracing:

| # | Function | Reason | Priority |
|---|----------|--------|----------|
| 1 | [call_openai()](src/llm.py#L15) | LLM API call | ⭐⭐⭐ |
| 2 | [call_anthropic()](src/llm.py#L30) | LLM API call | ⭐⭐⭐ |
| 3 | [run_pipeline()](src/pipeline.py#L40) | Main pipeline | ⭐⭐⭐ |
| 4 | [process_data()](src/pipeline.py#L10) | Data processing | ⭐⭐ |
| 5 | [fetch_from_api()](src/utils.py#L12) | External API call | ⭐⭐ |

### Excluded Functions
- [_parse_response()](src/llm.py#L47) - private utility
- [format_output()](src/utils.py#L5) - simple formatting

---

**Would you like to modify the selection?**
- "only 1, 2, 3" - apply selected items only
- "exclude 4" - remove specific function
- "add _parse_response" - include excluded function
- "ok" or "yes" - proceed with recommendations
```

---

### Step 3: @weave.op Options

Before applying tracing, explain the `@weave.op()` decorator options and ask about customization preferences.

```
## @weave.op() Options

The following options are available:

| Option | Description | Default |
|--------|-------------|---------|
| `name` | Op name displayed in dashboard | function name |
| `call_display_name` | Display name for individual calls (can be dynamic) | None |

### Examples

**Basic (no options):**
```python
@weave.op()
def my_function():
    ...
```

**Custom name:**
```python
@weave.op(name="llm-call-openai")
def call_openai():
    ...
```

**Dynamic display name:**
```python
@weave.op(call_display_name=lambda call: f"Query: {call.inputs['query'][:20]}")
def search(query: str):
    ...
```

---

### Custom Names

Would you like to specify custom names for any functions?

| # | Function | Default Name | Custom Name (optional) |
|---|----------|--------------|------------------------|
| 1 | call_openai() | call_openai | _______ |
| 2 | call_anthropic() | call_anthropic | _______ |
| 3 | run_pipeline() | run_pipeline | _______ |

- Leave blank to use function name as-is
- "default" or "ok" - use default names for all
```

---

### Step 4: User Confirmation and Apply

Once the user confirms their selection:

1. **Final confirmation**
```
## Ready to Apply

Adding @weave.op to the following 5 functions:
1. [call_openai()](src/llm.py#L15)
2. [call_anthropic()](src/llm.py#L30)
3. [run_pipeline()](src/pipeline.py#L40)
4. [process_data()](src/pipeline.py#L10)
5. [fetch_from_api()](src/utils.py#L12)

Proceed?
```

2. **Apply changes**
   - Add `import weave` if needed
   - Add `@weave.op` decorator to each function
   - If existing decorators present, add as outermost decorator

3. **Report results**
```
## Complete

✅ @weave.op tracing added to 5 functions

Modified files:
- [src/llm.py](src/llm.py) - 2 functions
- [src/pipeline.py](src/pipeline.py) - 2 functions
- [src/utils.py](src/utils.py) - 1 function

💡 weave.init("your-project") is required.
   Would you like to add it to the entry point?
```

---

## Application Examples

**Before:**
```python
async def call_openai(prompt: str) -> str:
    response = await client.chat.completions.create(...)
    return response.choices[0].message.content
```

**After:**
```python
import weave

@weave.op
async def call_openai(prompt: str) -> str:
    response = await client.chat.completions.create(...)
    return response.choices[0].message.content
```

---

## Additional Options

Available upon request:

### Custom op names
```python
@weave.op(name="openai-chat-completion")
def call_openai():
    ...
```

### Class method tracing
```python
class MyModel:
    @weave.op
    def predict(self, input):
        ...
```

---

## Important Notes

- Async functions work the same way with `@weave.op`
- Generator functions may need verification for support
- Decorator order: `@weave.op` should be the outermost decorator
