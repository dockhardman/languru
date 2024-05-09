# OpenAI Actions

OpenaiAction and AzureOpenaiAction are classes in the languru library that provide a convenient way to interact with OpenAI's and Azure OpenAI's API for various natural language processing tasks such as text completion, chat, embeddings, moderations, and more. These classes inherit from the ActionBase class and implement specific methods for each API functionality.

## Introduction

The OpenaiAction and AzureOpenaiAction classes are part of the languru.action module. They encapsulate the functionality provided by the OpenAI API and Azure OpenAI API, respectively. These classes make it easy to integrate OpenAI's powerful language models into your Python applications.

The OpenaiAction class uses the openai library to communicate with the OpenAI API, while the AzureOpenaiAction class uses the openai library with Azure-specific configurations to interact with the Azure OpenAI API.

Both classes define a set of model_deploys, which are named tuples that map user-friendly model names to the actual model names used by the respective APIs. This allows users to refer to models using more intuitive names.

## Usage

To use the OpenaiAction or AzureOpenaiAction class, you first need to instantiate an object of the desired class. You can provide an API key and other configuration options during initialization.

Here's an example of creating an OpenaiAction object:

```python
from languru.action.openai import OpenaiAction

openai_action = OpenaiAction(api_key="your_api_key")
```

For AzureOpenaiAction, you can provide additional parameters such as api_version and azure_endpoint:

```python
from languru.action.openai import AzureOpenaiAction

azure_openai_action = AzureOpenaiAction(
    api_key="your_api_key",
    api_version="2024-02-01",
    azure_endpoint="your_azure_endpoint"
)
```

Once you have an instance of the desired class, you can use its various methods to perform different tasks. Here are a few examples:

### Chat

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]
response = openai_action.chat(messages, model="gpt-3.5-turbo")
```

### Text Completion

```python
prompt = "Once upon a time"
completion = openai_action.text_completion(prompt, model="davinci-002", max_tokens=50)
```

### Embeddings

```python
text = "This is a sample text for embedding."
embeddings = openai_action.embeddings(text, model="text-embedding-ada-002")
```

The OpenaiAction and AzureOpenaiAction classes provide many more methods for different API functionalities, such as moderations, audio transcription, image generation, and more. You can refer to the class definitions and documentation for a complete list of available methods and their parameters.
