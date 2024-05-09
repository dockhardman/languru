# Anthropic Actions

`AnthropicAction` is a class that provides an interface to interact with the Anthropic AI models. It inherits from the `ActionBase` class and implements methods for chat completions and chat streaming using Anthropic's API.

## Introduction

The `AnthropicAction` class allows you to send requests to Anthropic's API for generating chat completions and streaming chat responses. It supports various Anthropic models, including Claude 2.0, Claude 2.1, Claude 3 Haiku, Claude 3 Opus, Claude 3 Sonnet, and Claude Instant 1.2.

To use `AnthropicAction`, you need to provide an API key, which can be passed as a parameter during initialization or set as an environment variable (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `API_KEY`).

## Usage

Here's an example of how to use `AnthropicAction` for chat completions:

```python
from languru.action.anthropic import AnthropicAction

action = AnthropicAction(api_key="your_api_key")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]

chat_response = action.chat(messages, model="claude-2.0")
print(chat_response.choices[0].message.content)
```

And here's an example of how to use `AnthropicAction` for chat streaming:

```python
from languru.action.anthropic import AnthropicAction

action = AnthropicAction(api_key="your_api_key")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Write a short poem about the beauty of nature."}
]

for chunk in action.chat_stream(messages, model="claude-3-sonnet"):
    print(chunk.choices[0].delta.content, end="", flush=True)
```

## Model Deployments

`AnthropicAction` supports the following model deployments:

- `anthropic/claude-2.0` (model name: `claude-2.0`)
- `anthropic/claude-2.1` (model name: `claude-2.1`)
- `anthropic/claude-3-haiku` (model name: `claude-3-haiku-20240307`)
- `anthropic/claude-3-haiku-20240307` (model name: `claude-3-haiku-20240307`)
- `anthropic/claude-3-opus` (model name: `claude-3-opus-20240229`)
- `anthropic/claude-3-opus-20240229` (model name: `claude-3-opus-20240229`)
- `anthropic/claude-3-sonnet` (model name: `claude-3-sonnet-20240229`)
- `anthropic/claude-3-sonnet-20240229` (model name: `claude-3-sonnet-20240229`)
- `anthropic/claude-instant-1.2` (model name: `claude-instant-1.2`)
- `claude-2.0` (model name: `claude-2.0`)
- `claude-2.1` (model name: `claude-2.1`)
- `claude-3-haiku` (model name: `claude-3-haiku-20240307`)
- `claude-3-haiku-20240307` (model name: `claude-3-haiku-20240307`)
- `claude-3-opus` (model name: `claude-3-opus-20240229`)
- `claude-3-opus-20240229` (model name: `claude-3-opus-20240229`)
- `claude-3-sonnet` (model name: `claude-3-sonnet-20240229`)
- `claude-3-sonnet-20240229` (model name: `claude-3-sonnet-20240229`)
- `claude-instant-1.2` (model name: `claude-instant-1.2`)
