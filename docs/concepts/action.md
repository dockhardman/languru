---
weight: 100
---

# Action

The `Action` module is designed to provide a simple way to interact with the models or external services.
It is a base class that provides a common interface for all the actions.
The `Action` instance could be loaded in LLM server which will be fully compatible with OpenAI APIs.

## Implemented Actions

- OpenaiAction
- GoogleGenaiAction
- GroqAction, GroqOpenaiAction
- PerplexityAction
- TransformersAction
