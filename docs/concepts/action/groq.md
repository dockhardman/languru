# Groq Actions

The `GroqAction` class is a subclass of `OpenaiAction` that provides a convenient way to interact with Groq's language models using the Groq API. It allows you to perform various natural language processing tasks such as text completion, chat completion, and more.

## Introduction

The `GroqAction` class is designed to simplify the process of working with Groq's language models. It inherits from the `OpenaiAction` class and extends its functionality to support Groq-specific models and configurations. By using this class, you can easily integrate Groq's powerful language models into your Python applications.

## Usage

To use the `GroqAction` class, you need to follow these steps:

1. Import the necessary modules:

    ```python
    from languru.action.groq import GroqAction
    ```

2. Create an instance of the `GroqAction` class by providing the required parameters:

    ```python
    action = GroqAction(api_key="YOUR_GROQ_API_KEY")
    ```

    Replace `"YOUR_GROQ_API_KEY"` with your actual Groq API key. Alternatively, you can set the `GROQ_API_KEY` environment variable, and the class will automatically use it.

3. Use the available methods of the `GroqAction` instance to perform various tasks. For example, to generate text completions:

    ```python
    prompt = "Once upon a time"
    completion = action.text_completion(prompt, model="llama2-70b")
    print(completion.choices[0].text)
    ```

    This will generate a text completion using the "llama2-70b" model based on the provided prompt.
