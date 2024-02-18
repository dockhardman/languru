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

### Chat with customized transformers llm

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

Query services.

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
