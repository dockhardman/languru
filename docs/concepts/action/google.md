# Google Actions

GoogleGenaiAction is a class that provides an interface to interact with Google's Generative AI models. It allows you to perform various natural language processing tasks such as chat completion, text completion, and embeddings generation using Google's powerful AI models.

## Introduction

The GoogleGenaiAction class is a subclass of ActionBase and is designed to work with Google's Generative AI API. It provides a convenient way to access and utilize Google's AI models for different NLP tasks. The class handles the configuration and authentication with the Google GenAI API using an API key.

## Usage

To use the GoogleGenaiAction class, you need to follow these steps:

1. Import the necessary modules:

```python
import google.generativeai as genai
from languru.action.base import ActionBase, ModelDeploy
from languru.config import logger
```

2. Create an instance of the GoogleGenaiAction class:

```python
action = GoogleGenaiAction(api_key="YOUR_API_KEY")
```

Make sure to provide a valid Google GenAI API key when creating the instance. You can either pass it directly or set it as an environment variable named `GOOGLE_API_KEY` or `GOOGLE_GENAI_API_KEY`.

3. Use the available methods to perform different tasks:

   - `chat(messages, model)`: Generates a chat completion based on the provided messages and model.
   - `text_completion(prompt, model)`: Generates a text completion based on the given prompt and model.
   - `embeddings(input, model)`: Generates embeddings for the provided input using the specified model.

Here's an example of how to use the `chat` method:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]
model = "models/chat-bison-001"

chat_completion = action.chat(messages, model=model)
print(chat_completion)
```

## Available Models

The GoogleGenaiAction class provides a list of available model deploys that can be used for different tasks. These model deploys are defined in the `model_deploys` attribute of the class. Some of the available models include:

- `models/chat-bison-001`: A model for chat-based tasks.
- `models/text-bison-001`: A model for text generation tasks.
- `models/embedding-gecko-001`: A model for generating embeddings.
- `models/gemini-1.0-pro`: A high-quality model for various NLP tasks.

You can specify the desired model when calling the respective methods (`chat`, `text_completion`, `embeddings`).
