# Hugging Face Actions

TransformersAction is a class in the Languru library that provides an interface for performing various natural language processing tasks using Hugging Face's Transformers models. It allows users to easily load pre-trained models and perform tasks such as text completion, chat completion, and embedding generation.

## Introduction

The TransformersAction class is designed to simplify the process of working with Transformers models. It handles the loading of pre-trained models and tokenizers based on the provided configuration. The class supports different model deployment options, quantization configurations, and generation settings.

The main features of TransformersAction include:

- Loading pre-trained models and tokenizers from Hugging Face's model hub
- Performing text completion tasks with customizable parameters
- Generating chat completions based on a sequence of messages
- Computing embeddings for given input text or pre-tokenized input
- Supporting model quantization for reduced memory usage
- Customizable stop words and generation settings

## Usage

To use TransformersAction, you need to create an instance of the class and provide the necessary configuration. Here's an example of how to instantiate the class:

```python
from languru.action.transformers import TransformersAction

action = TransformersAction(model_name="gpt2", device="cpu")
```

In this example, we create an instance of TransformersAction with the "gpt2" model and specify the device as "cpu". You can customize the model name, device, and other parameters based on your requirements.

Once you have an instance of TransformersAction, you can use its methods to perform various tasks. Here are some examples:

### Text Completion

```python
prompt = "Once upon a time"
completion = action.text_completion(prompt=prompt, model="gpt2", max_tokens=50)
print(completion.choices[0].text)
```

This code snippet demonstrates how to generate a text completion using the `text_completion` method. You provide the prompt, specify the model name, and set the maximum number of tokens to generate. The generated completion is accessible through the `choices` attribute of the returned `Completion` object.

### Chat Completion

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]
chat_completion = action.chat(messages=messages, model="gpt2")
print(chat_completion.choices[0].message.content)
```

To generate a chat completion, you can use the `chat` method. You provide a list of messages, where each message is a dictionary containing the role and content. The generated chat completion is returned as a `ChatCompletion` object, and you can access the assistant's response through the `choices` attribute.

### Embeddings

```python
input_text = "This is a sample sentence."
embeddings = action.embeddings(input=input_text, model="gpt2")
print(embeddings.data[0].embedding)
```

The `embeddings` method allows you to generate embeddings for a given input text or pre-tokenized input. You provide the input and specify the model name. The generated embeddings are returned as a `CreateEmbeddingResponse` object, and you can access the embeddings through the `data` attribute.

## Model Configuration

TransformersAction provides various configuration options to customize the behavior of the loaded models. Here are some of the key configuration attributes:

- `MODEL_NAME`: The name of the pre-trained model to load. You can set this attribute directly or use the `HF_MODEL_NAME` or `MODEL_NAME` environment variables.
- `model_deploys`: A sequence of `ModelDeploy` named tuples that define the mapping between model deployment names and their corresponding model names.
- `use_quantization`: A boolean flag indicating whether to use quantization for the loaded model.
- `load_in_8bit`: A boolean flag specifying whether to load the model in 8-bit precision.
- `load_in_4bit`: A boolean flag specifying whether to load the model in 4-bit precision.
- `use_flash_attention`: A boolean flag indicating whether to use flash attention for improved performance.
- `stop_words`: A sequence of words that, when encountered, will stop the text generation process.
- `is_causal_lm`: A boolean flag indicating whether the loaded model is a causal language model.

You can customize these configuration attributes when creating an instance of TransformersAction or by modifying the class attributes directly.

## Model Quantization

TransformersAction supports model quantization, which allows you to reduce the memory usage of the loaded models. Quantization is useful when working with large models or when running on resource-constrained devices.

To enable quantization, you can set the `use_quantization` attribute to `True` or pass it as a parameter when creating an instance of TransformersAction. Additionally, you can configure various quantization settings using the following attributes:

- `load_in_8bit`: Set to `True` to load the model in 8-bit precision.
- `load_in_4bit`: Set to `True` to load the model in 4-bit precision.
- `llm_int8_threshold`: The threshold for activating 8-bit quantization.
- `llm_int8_skip_modules`: A sequence of module names to skip during 8-bit quantization.
- `llm_int8_enable_fp32_cpu_offload`: Set to `True` to enable FP32 CPU offloading for 8-bit quantization.
- `llm_int8_has_fp16_weight`: Set to `True` if the model has FP16 weights for 8-bit quantization.
- `bnb_4bit_compute_dtype`: The compute dtype for 4-bit quantization.
- `bnb_4bit_quant_type`: The quantization type for 4-bit quantization.
- `bnb_4bit_use_double_quant`: Set to `True` to use double quantization for 4-bit quantization.

By configuring these quantization settings, you can optimize the memory usage of the loaded models based on your specific requirements.
