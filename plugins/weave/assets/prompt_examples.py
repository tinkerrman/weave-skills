"""
Weave Prompt Example Code

Based on official docs: https://docs.wandb.ai/weave/guides/core-types/prompts
"""

import weave

weave.init("prompt-examples")


# ===== 1. StringPrompt =====

system_prompt = weave.StringPrompt("You speak like a pirate")

# Use with OpenAI
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt.format()},
        {"role": "user", "content": "Explain general relativity."},
    ],
)


# ===== 2. MessagesPrompt =====

chat_prompt = weave.MessagesPrompt(
    [
        {"role": "system", "content": "You are a helpful {domain} expert."},
        {"role": "user", "content": "{question}"},
    ]
)

# Format with parameters
messages = chat_prompt.format(domain="Python", question="What is a decorator?")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
)


# ===== 3. Custom Prompt Subclass =====

class RAGPrompt(weave.Prompt):
    """Custom prompt with conditional context handling"""

    context_header: str = "Use the following context to answer:"

    def format(self, question: str, contexts: list[str] = None) -> str:
        if contexts:
            context_str = "\n".join(f"- {c}" for c in contexts)
            return f"{self.context_header}\n{context_str}\n\nQuestion: {question}\nAnswer:"
        return f"Question: {question}\nAnswer:"


rag_prompt = RAGPrompt()
formatted = rag_prompt.format(
    question="What is RAG?",
    contexts=["RAG combines retrieval and generation."],
)


# ===== 4. Parameterized Prompts =====

# StringPrompt with parameters
eval_prompt = weave.StringPrompt(
    "Evaluate the {criteria} of the following response on a scale of 1-5.\n\n"
    "Question: {question}\nResponse: {response}\n\n"
    'Respond in JSON: {{"score": <1-5>, "reason": "<explanation>"}}'
)

formatted = eval_prompt.format(
    criteria="relevance",
    question="What is ML?",
    response="Machine learning is a subset of AI.",
)

# MessagesPrompt with parameters
scorer_prompt = weave.MessagesPrompt(
    [
        {"role": "system", "content": "Provide a single word describing the emotion."},
        {"role": "user", "content": "{scene}"},
    ]
)

messages = scorer_prompt.format(scene="A dog is lying on a dock next to a fisherman.")


# ===== 5. Publishing Prompts =====

def publish_prompts():
    """Publish prompts to Weave for version control"""
    # Publish StringPrompt
    prompt_v1 = weave.StringPrompt("Answer the question: {question}")
    weave.publish(prompt_v1, name="my-qa-prompt")

    # Modify and publish again → creates new version
    prompt_v2 = weave.StringPrompt(
        "Please answer the following question thoroughly: {question}"
    )
    weave.publish(prompt_v2, name="my-qa-prompt")

    # Publish MessagesPrompt
    chat = weave.MessagesPrompt(
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "{question}"},
        ]
    )
    weave.publish(chat, name="my-chat-prompt")


# ===== 6. Retrieving Published Prompts =====

def load_prompts():
    """Load published prompts by reference"""
    # Latest version
    prompt = weave.ref("my-qa-prompt:latest").get()

    # Specific version
    prompt_v0 = weave.ref("my-qa-prompt:v0").get()

    # Use retrieved prompt
    formatted = prompt.format(question="What is Weave?")
    return formatted


# ===== 7. Using Prompts with Models =====

from weave import Model


class PromptDrivenModel(Model):
    """Model that loads a versioned prompt from Weave"""

    model_name: str = "gpt-4o-mini"
    prompt_name: str = "my-qa-prompt"

    @weave.op()
    def predict(self, question: str) -> str:
        # Load latest prompt version at inference time
        prompt = weave.ref(f"{self.prompt_name}:latest").get()
        formatted = prompt.format(question=question)

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": formatted}],
        )
        return response.choices[0].message.content


# ===== 8. Version Comparison =====

def compare_prompt_versions():
    """Compare different prompt versions"""
    v0 = weave.ref("my-qa-prompt:v0").get()
    v1 = weave.ref("my-qa-prompt:v1").get()

    print(f"v0: {v0.format(question='test')}")
    print(f"v1: {v1.format(question='test')}")


if __name__ == "__main__":
    # StringPrompt
    print("=== StringPrompt ===")
    simple = weave.StringPrompt("Hello {name}!")
    print(simple.format(name="World"))

    # MessagesPrompt
    print("\n=== MessagesPrompt ===")
    chat = weave.MessagesPrompt(
        [
            {"role": "system", "content": "You are a {role}."},
            {"role": "user", "content": "{question}"},
        ]
    )
    print(chat.format(role="teacher", question="What is Python?"))

    # Custom Prompt
    print("\n=== Custom RAGPrompt ===")
    rag = RAGPrompt()
    print(rag.format(question="What is RAG?", contexts=["RAG combines retrieval and generation."]))
    print(rag.format(question="What is RAG?"))  # Without context

    # Publishing
    print("\n=== Publishing ===")
    publish_prompts()
    print("Prompts published successfully!")
