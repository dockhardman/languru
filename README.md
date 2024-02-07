# Languru

The general-purpose LLM app stacks deploy AI services quickly and (stupidly) simply.

## Getting Started

Install Languru:

```shell
pip install languru
```

Run agent server:

```shell
languru server run
```

Run llm action server:

```shell
languru llm run
```

## Usage

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
print(res)
```
