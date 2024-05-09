---
weight: 100
---

# Overview

The `Action` module is designed to provide a simple way to interact with the models or external services.
It is a base class that provides a common interface for all the actions.
The `Action` instance could be loaded in LLM server which will be fully compatible with OpenAI APIs.

## Introduction

The `Action` module in Languru is designed to provide a simple and unified interface for interacting with different language models or external services. It serves as a base class that defines common methods and abstracts away the underlying implementation details. The `Action` instance can be loaded into the LLM server, making it fully compatible with OpenAI APIs.

## Module Structure

The `Action` module consists of several key components:

1. `ActionBase`: The base class that inherits from `ActionText`, `ActionAudio`, and `ActionImage`. It provides a common interface for all actions.
2. `ActionText`: An abstract base class that defines methods related to text-based actions, such as chat, text completion, embeddings, and moderations.
3. `ActionAudio`: An abstract base class that defines methods related to audio-based actions, such as speech generation, transcription, and translation.
4. `ActionImage`: An abstract base class that defines methods related to image-based actions, such as image generation, editing, and variation.

## Usage

To use the `Action` module, you can create a subclass that inherits from `ActionBase` and implements the required methods for your specific use case. Here's an example:

```python
class MyAction(ActionBase):
    def name(self) -> Text:
        return "MyAction"

    def health(self) -> bool:
        return True

    def chat(self, messages: List["ChatCompletionMessageParam"], *args, model: Text, **kwargs) -> "ChatCompletion":
        # Implement chat functionality here
        pass

    def text_completion(self, prompt: Text, *args, model: Text, **kwargs) -> "Completion":
        # Implement text completion functionality here
        pass

    # Implement other required methods
```

In the above example, `MyAction` inherits from `ActionBase` and implements the `name()`, `health()`, `chat()`, and `text_completion()` methods. You can add additional methods and functionality as needed.

## Model Deployment

The `Action` module allows you to define model deployments using the `ModelDeploy` named tuple. Each model deployment consists of a `model_deploy_name` and a `model_name`. You can specify the model deployments when creating an instance of your custom `Action` class:

```python
model_deploys = [
    ModelDeploy("gpt-3", "text-davinci-002"),
    ModelDeploy("gpt-3.5", "text-davinci-003"),
]

my_action = MyAction(model_deploys=model_deploys)
```

The `get_model_name()` method allows you to retrieve the `model_name` based on the `model_deploy_name`.

## Interaction Methods

The `Action` module provides several methods for interacting with the loaded models:

- `chat()`: Performs a chat completion based on the provided messages and model.
- `chat_stream()`: Generates a stream of chat completion chunks based on the provided messages and model.
- `text_completion()`: Generates a text completion based on the provided prompt and model.
- `text_completion_stream()`: Generates a stream of text completion chunks based on the provided prompt and model.
- `embeddings()`: Creates embeddings for the given input text using the specified model.
- `moderations()`: Performs content moderation on the given input text using the specified model.
- `audio_speech()`: Generates speech audio from the given input text using the specified model and voice.
- `audio_transcriptions()`: Transcribes the given audio file using the specified model.
- `audio_translations()`: Translates the given audio file using the specified model.
- `images_generations()`: Generates images based on the given prompt using the specified model.
- `images_edits()`: Edits an image based on the provided parameters using the specified model.
- `images_variations()`: Generates variations of an image using the specified model.

These methods provide a high-level interface for interacting with the loaded models and performing various tasks related to text, audio, and image processing.

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
