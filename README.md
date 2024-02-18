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
print(res.model_dump_json(indent=2))
```

```json
{
  "id": "chatcmpl-8tXSkCGosQVsPe1TBV13Tub7lV623",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "Hello! How can I assist you today?",
        "role": "assistant",
        "function_call": null,
        "tool_calls": null
      }
    }
  ],
  "created": 1708247362,
  "model": "gpt-3.5-turbo-0125",
  "object": "chat.completion",
  "system_fingerprint": "fp_69829325d0",
  "usage": {
    "completion_tokens": 9,
    "prompt_tokens": 19,
    "total_tokens": 28
  }
}
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
print(res.model_dump_json(indent=2))
```

```json
{
  "id": "18f7ab9f-7e1f-4ecb-90b6-585b27d7fc19",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "The capital of the United States is Washington D.C.\n",
        "role": "assistant",
        "function_call": null,
        "tool_calls": null
      }
    }
  ],
  "created": 1708245462,
  "model": "microsoft/phi-1_5",
  "object": "chat.completion",
  "system_fingerprint": null,
  "usage": {
    "completion_tokens": 16,
    "prompt_tokens": 29,
    "total_tokens": 45
  }
}
```
