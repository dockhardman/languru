# Welcome to Languru

The general-purpose LLM app stacks deploy AI services quickly and (stupidly) simply.

[![image](https://img.shields.io/pypi/v/languru.svg)](https://pypi.python.org/pypi/languru)
[![image](https://img.shields.io/pypi/l/languru.svg)](https://pypi.python.org/pypi/languru)
[![image](https://img.shields.io/pypi/pyversions/languru.svg)](https://pypi.python.org/pypi/languru)
[![PytestCI](https://github.com/dockhardman/languru/actions/workflows/python-pytest.yml/badge.svg)](https://github.com/dockhardman/languru/actions/workflows/python-pytest.yml)
[![codecov](https://codecov.io/gh/dockhardman/languru/graph/badge.svg?token=OFX6C8Z31C)](https://codecov.io/gh/dockhardman/languru)

Source Code: [Languru on Github](https://github.com/dockhardman/languru)

## Getting Started

Install Languru:

```shell
pip install languru[server]
pip install languru[all]  # Or install all dependencies (include `torch`, `transformers`, ...)
```

Run llm action server:

```shell
OPENAI_API_KEY=$OPENAI_API_KEY languru llm run  # Remember set OPENAI_API_KEY before you run.
```

Query LLM service, which is fully compatible with OpenAI APIs.

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8682/v1")
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

## Concepts

- [Action](concepts/action.md)
- [LLM Server](concepts/llm_server.md)
- [Agent Server](concepts/agent_server.md)
- [Docker](concepts/docker.md)
