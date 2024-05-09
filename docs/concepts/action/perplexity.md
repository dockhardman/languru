# Perplexity Actions

PerplexityAction is a custom action class that extends the OpenaiAction class to provide support for interacting with the Perplexity AI API. It allows you to leverage various language models and perform tasks such as text completion, chat completion, and more.

## Introduction

The PerplexityAction class is designed to simplify the integration of the Perplexity AI API into your Python projects. It provides a convenient way to initialize the action with the necessary API key and base URL, and offers a set of predefined model deploys that you can use for different language tasks.

The class inherits from the OpenaiAction class, which means it inherits all the functionality and methods available in the base class. Additionally, it overrides certain methods to customize the behavior specific to the Perplexity AI API.

## Usage

To use the PerplexityAction class, follow these steps:

1. Import the necessary modules:

    ```python
    from languru.action.perplexity import PerplexityAction
    ```

2. Initialize the PerplexityAction instance:

    ```python
    action = PerplexityAction(api_key="your_api_key", base_url="https://api.perplexity.ai")
    ```

    Make sure to provide a valid API key for the Perplexity AI API. You can either pass it directly to the constructor or set it as an environment variable named `PERPLEXITY_API_KEY`, `PPLX_API_KEY`, or `OPENAI_API_KEY`.

3. Use the available methods to interact with the Perplexity AI API. For example, to perform a chat completion:

    ```python
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    model = "pplx-70b-chat"
    response = action.chat(messages, model=model)
    ```

    The `chat` method sends a chat completion request to the Perplexity AI API using the specified model and messages. It returns the response from the API.

4. Explore other methods available in the PerplexityAction class, such as `text_completion`, `chat_stream`, `text_completion_stream`, and more, to perform various language tasks.

## Model Deploys

The PerplexityAction class provides a set of predefined model deploys that you can use for different language tasks. These model deploys are defined in the `model_deploys` attribute of the class.

Some of the available model deploys include:

- "codellama-34b-instruct"
- "codellama-70b-instruct"
- "llama-2-70b-chat"
- "mistral-7b-instruct"
- "mixtral-8x7b-instruct"
- "pplx-70b-chat"
- "pplx-70b-online"
- "pplx-7b-chat"
- "pplx-7b-online"
- ...

You can specify the desired model deploy when calling the methods of the PerplexityAction class.

## Customization

If you need to customize the behavior of the PerplexityAction class, you can subclass it and override the relevant methods. For example, you can override the `__init__` method to provide additional initialization logic or modify the `model_deploys` attribute to include your own custom model deploys.

```python
class CustomPerplexityAction(PerplexityAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add your custom initialization logic here

    model_deploys = (
        ModelDeploy("custom-model-1", "custom-model-1"),
        ModelDeploy("custom-model-2", "custom-model-2"),
        # Add your custom model deploys here
    )
```
