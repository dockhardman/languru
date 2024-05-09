---
weight: 100
---

# Overview

The `Action` module is designed to provide a simple way to interact with the models or external services.
It is a base class that provides a common interface for all the actions.
The `Action` instance could be loaded in LLM server which will be fully compatible with OpenAI APIs.

## Implemented Actions

### OpenAI and AzureOpenAI Actions

- OpenaiAction
- AzureOpenaiAction

### Anthropic Claude Actions

- AnthropicAction

### Google Actions

- GoogleGenaiAction

### Groq Actions

- GroqAction
- GroqOpenaiAction

### Hugging Face Actions

- TransformersAction

### Perplexity Actions

- PerplexityAction
