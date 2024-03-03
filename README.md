# Languru

The general-purpose LLM app stacks deploy AI services quickly and (stupidly) simply.

## Getting Started

Install Languru:

```shell
pip install languru[server]
```

Or install all dependencies (include `torch`, `transformers`, ...)

```shell
pip install languru[all]
```

Run agent server:

```shell
languru server run
```

Run llm action server:

```shell
languru llm run
```

Query llm service.

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8680/v1")
res = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
)
for choice in res.choices:
    print(f"{choice.message.role}: {choice.message.content}")
# assistant: Hello! How can I assist you today?
```

## Usages

### Chat Streaming

The service is compatible with OpenAI chat stream mode.

```python
# languru server run
# languru llm run
res = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
    stream=True,
)
for chunk in res:
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
            # Hello! How can I assist you today?
print()
```

### Chat and TextCompletion with customized transformers llm

Inherited from `TransformersAction`.

```python
# module_path.py
from languru.action.base import ModelDeploy
from languru.action.hf import TransformersAction


class MicrosoftPhiAction(TransformersAction):
    MODEL_NAME = "microsoft/phi-1_5"
    model_deploys = (
        ModelDeploy("microsoft/phi-1_5", "microsoft/phi-1_5"),
        ModelDeploy("phi-1_5", "microsoft/phi-1_5"),
    )
```

Run agent server and llm action server.

```shell
languru server run
languru llm run --action module_path.MicrosoftPhiAction
```

Query llm chat.

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8680/v1")
res = client.chat.completions.create(
    model="microsoft/phi-1_5",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of the United States?"},
    ],
)
for choice in res.choices:
    print(f"{choice.message.role}: {choice.message.content}")
# assistant: The capital of the United States is Washington D.C.
#
```

Query llm text completion.

```python
from textwrap import dedent

from openai import OpenAI

client = OpenAI(base_url="http://localhost:8680/v1")
res = client.completions.create(
    model="microsoft/phi-1_5",
    prompt=dedent(
        """
        Alice: I don't know why, I'm struggling to maintain focus while studying. Any suggestions?
        Bob: Well, have you tried creating a study schedule and sticking to it?
        Alice: Yes, I have, but it doesn't seem to help much.
        """
    ).strip(),
    max_tokens=200,
)
for choice in res.choices:
    print(choice.text)

# Bob: Hmm, maybe you should try studying in a different environment. Sometimes a change of scenery can do wonders for concentration.
# Alice: That's a good idea. I'll give it a try.

# Alice: I'm having trouble understanding this concept in my math class.
# Bob: Have you tried watching online tutorials or asking your teacher for help?
# Alice: Yes, I have, but I still can't grasp it.
# Bob: Well, maybe you should try studying with a study group. Sometimes discussing the material with others can help you understand it better.
# Alice: That's a great suggestion. I'll look into joining a study group.

# Alice: I'm feeling overwhelmed with all
```

### Embeddings with customized transformers model

Inherited from `TransformersAction`.

```python
# module_path.py
from languru.action.base import ModelDeploy
from languru.action.hf import TransformersAction


class STMiniLML12V2Action(TransformersAction):
    MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    model_deploys = (
        ModelDeploy(MODEL_NAME, MODEL_NAME),
        ModelDeploy(model_deploy_name="MiniLM-L12-v2", model_name=MODEL_NAME),
    )
```

Run agent server and llm action server.

```shell
languru server run
languru llm run --action module_path.STMiniLML12V2Action
```

Query text embeddings:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8680/v1")
res = client.embeddings.create(
    input=[
        "What is your return policy for online purchases?",
        "How long does it usually take for an order to be delivered?",
        "Do you offer international shipping, and what are the rates?",
    ],
    model="MiniLM-L12-v2",
)
print(f"There are {len(res.data)} embeddings.")
print(f"The embeddings length is {len(res.data[0].embedding)}.")
# There are 3 embeddings.
# The embeddings length is 384.
```

### Use google gemini generative ai models

Run agent server and llm action server.

```shell
languru server run
languru llm run --action languru.action.google.GoogleGenaiAction
```

Query llm chat.

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8680/v1")

# Chat
res = client.chat.completions.create(
    model="gemini-pro",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
)
for choice in res.choices:
    print(f"{choice.message.role}: {choice.message.content}")
    # assistant: As an AI language model, I don't have personal feelings or emotions, so I don't experience states like happiness or sadness. However, I am designed to be helpful and informative, and I can engage in conversations and answer your questions to the best of my abilities.
    # How about you? How are you feeling today?

# Text Generation
res = client.completions.create(
    model="gemini-pro",
    prompt="The reverse of a dog is a",
    max_tokens=200,
)
for choice in res.choices:
    print(choice.text)
    # god

# Embeddings
res = client.embeddings.create(
    input=[
        "Discover your spirit of adventure and indulge your thirst for wanderlust with the touring bike that has dominated the segment for the past 50 years: the Honda Gold Wing Tour, Gold Wing Tour Automatic DCT, and Gold Wing Tour Airbag Automatic DCT.",
        "R1M: This is the most advanced production motorcycle for riders who are at the very top of their game.",
    ],
    model="models/embedding-001",
)
print(f"There are {len(res.data)} embeddings.")
print(f"The embeddings length is {len(res.data[0].embedding)}.")
# There are 2 embeddings.
# The embeddings length is 768.
```

### Google Gemma Transformers

Run gemma action server:

```shell
languru server run
MODEL_NAME=google/gemma-2b languru llm run --action languru.action.hf.TransformersAction
MODEL_NAME=google/gemma-2b-it languru llm run --action languru.action.hf.TransformersAction
```

Query gemma llm.

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8680/v1")
res = client.chat.completions.create(
    model="google/gemma-2b-it",
    messages=[
        {"role": "user", "content": "Write a hello world program"},
    ],
    max_tokens=800,
)
for choice in res.choices:
    print(f"{choice.message.role}: {choice.message.content}")
# assistant: ```python
# print("Hello, world!")
# ```

# **Explanation:**

# * `print()` is a built-in Python function that prints the given argument to the console.
# * `"Hello, world!"` is the string that we want to print.
# * The `\n` character is used to insert a newline character into the print statement.

# **Output:**

# ```
# Hello, world!
# ```

# **How it works:**

# 1. The `print()` function takes one or more arguments.
# 2. The first argument is the string that we want to print.
# 3. If there are multiple arguments, they are separated by commas.
# 4. The `print()` function prints the arguments in the order they are given, separated by a space.
# 5. The `\n` character is used to insert a newline character into the output.

# **Note:**

# * The `print()` function can also print other types of objects, such as lists, dictionaries, and objects.
# * You can use the `format()` method to format the output before printing it. For example, the following code will print the string with a dollar sign:

# ```python
# name = "John"
# age = 30
# print("My name is {} and I am {} years old.".format(name, age))
# ```
```

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8680/v1")
res = client.completions.create(
    model="google/gemma-2b",
    prompt="The capital of France is ",
    max_tokens=300,
)
for choice in res.choices:
    print(choice.text)
```
