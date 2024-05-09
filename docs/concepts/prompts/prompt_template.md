# PromptTemplate

`PromptTemplate` is a Python class that provides a convenient way to create and manage prompt templates for generating text using language models. It allows you to define a prompt with placeholders for variables, which can be easily substituted with actual values when needed. The class also supports managing a list of messages and formatting them with the prompt variables.

## Introduction

The `PromptTemplate` class is designed to simplify the process of creating and using prompt templates in natural language processing tasks, particularly when working with language models like OpenAI's GPT. It provides a flexible and intuitive interface for defining prompts, managing prompt variables, and formatting messages.

Key features of `PromptTemplate` include:

- Defining prompts with placeholders for variables
- Managing a dictionary of prompt variables
- Formatting prompts with actual values
- Maintaining a list of messages associated with the prompt
- Customizing the delimiter characters for placeholders
- Supporting different roles for messages (system, user, assistant)

## Usage

To use the `PromptTemplate` class, you first need to instantiate it with a prompt string and optional arguments. Here's an example:

```python
from languru.types.chat.completions import PromptTemplate

prompt = "Hello {name}, how are you doing today?"
messages = [{"role": "user", "content": "I'm doing well, thanks for asking!"}]

template = PromptTemplate(prompt, prompt_vars={"name": "John"}, messages=messages)
```

In this example, we create a `PromptTemplate` instance with a prompt that includes a placeholder `{name}`, a dictionary of prompt variables with a default value for `name`, and a list of messages.

You can format the prompt with actual values using the `format()` method:

```python
formatted_prompt = template.format(name="Alice")
print(formatted_prompt)
# Output: Hello Alice, how are you doing today?
```

The `format()` method replaces the placeholders in the prompt with the provided values.

You can also format the messages associated with the prompt using the `format_messages()` method:

```python
formatted_messages = template.format_messages(prompt_vars={"name": "Bob"})
print(formatted_messages)
# Output: [
#   {"role": "system", "content": "Hello Bob, how are you doing today?"},
#   {"role": "user", "content": "I'm doing well, thanks for asking!"}
# ]
```

The `format_messages()` method applies the prompt variables to the messages and returns a list of formatted messages.

## Customization

`PromptTemplate` allows you to customize various aspects of the prompt and messages:

- `prompt_vars_update()`: Update the prompt variables dictionary
- `prompt_vars_drop()`: Remove specific prompt variables from the dictionary
- `prompt_placeholders()`: Get a list of placeholders in the prompt
- `role_system`, `role_user`, `role_assistant`: Customize the role names for messages

You can refer to the class documentation for more details on these methods and attributes.

## Conclusion

The `PromptTemplate` class provides a powerful and flexible way to manage prompt templates and generate formatted prompts and messages. It simplifies the process of working with language models and allows you to focus on the high-level logic of your application. By leveraging the features of `PromptTemplate`, you can easily create and customize prompts, substitute variables, and manage messages associated with the prompts.
