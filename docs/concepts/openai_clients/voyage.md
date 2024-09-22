# Voyage OpenAI

## Introduction

The `languru.openai_plugins.clients.voyage` module is designed to interact with the Voyage AI platform, providing functionalities for model management and embedding creation. This documentation aims to provide a clear and concise overview of the module's functionality and usage.

## Module Overview

The `languru.openai_plugins.clients.voyage` module consists of several classes:

- **VoyageModels**: Handles model retrieval and validation.
- **VoyageEmbeddings**: Creates embeddings for input text or texts.
- **VoyageOpenAI**: Manages API interactions and client initialization.

### VoyageModels

The `VoyageModels` class provides methods for retrieving and listing supported models.

#### Retrieve Model

```python
def retrieve(self, model: str, *, extra_headers: Headers | None = None, extra_query: Query | None = None, extra_body: Body | None = None, timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN, **kwargs,) -> "Model":
    """
    Retrieve a specific model by its ID.

    Args:
        model (str): The ID of the model to retrieve.
        extra_headers (Headers | None, optional): Additional headers for the request. Defaults to None.
        extra_query (Query | None, optional): Additional query parameters for the request. Defaults to None.
        extra_body (Body | None, optional): Additional body data for the request. Defaults to None.
        timeout (float | httpx.Timeout | None | NotGiven, optional): Timeout for the request. Defaults to NOT_GIVEN.

    Returns:
        Model: The retrieved model.
    """
```

#### List Models

```python
def list(self, *, extra_headers: Headers | None = None, extra_query: Query | None = None, extra_body: Body | None = None, timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN, **kwargs,) -> "SyncPage[Model]":
    """
    List all supported models.

    Args:
        extra_headers (Headers | None, optional): Additional headers for the request. Defaults to None.
        extra_query (Query | None, optional): Additional query parameters for the request. Defaults to None.
        extra_body (Body | None, optional): Additional body data for the request. Defaults to None.
        timeout (float | httpx.Timeout | None | NotGiven, optional): Timeout for the request. Defaults to NOT_GIVEN.

    Returns:
        SyncPage[Model]: A page of supported models.
    """
```

### VoyageEmbeddings

The `VoyageEmbeddings` class provides a method for creating embeddings.

#### Create Embedding

```python
def create(self, *, input: Union[str, List[str], Iterable[int], Iterable[Iterable[int]]], model: Text, dimensions: int | NotGiven = NOT_GIVEN, encoding_format: Literal["float", "base64"] | NotGiven = NOT_GIVEN, user: str | NotGiven = NOT_GIVEN, extra_headers: Headers | None = None, extra_query: Query | None = None, extra_body: Body | None = None, timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,) -> CreateEmbeddingResponse:
    """
    Create an embedding for the input text or texts.

    Args:
        input (Union[str, List[str], Iterable[int], Iterable[Iterable[int]]]): The input text or texts to create embeddings for.
        model (Text): The model to use for creating embeddings.
        dimensions (int | NotGiven, optional): The number of dimensions for the embeddings. Defaults to NOT_GIVEN.
        encoding_format (Literal["float", "base64"] | NotGiven, optional): The encoding format for the embeddings. Defaults to NOT_GIVEN.
        user (str | NotGiven, optional): The user to create embeddings for. Defaults to NOT_GIVEN.
        extra_headers (Headers | None, optional): Additional headers for the request. Defaults to None.
        extra_query (Query | None, optional): Additional query parameters for the request. Defaults to None.
        extra_body (Body | None, optional): Additional body data for the request. Defaults to None.
        timeout (float | httpx.Timeout | None | NotGiven, optional): Timeout for the request. Defaults to NOT_GIVEN.

    Returns:
        CreateEmbeddingResponse: The created embedding response.
    """
```

### VoyageOpenAI

The `VoyageOpenAI` class manages API interactions and client initialization.

#### Initialize Client

```python
def __init__(self, *, api_key: Optional[Text] = None, **kwargs):
    """
    Initialize the VoyageOpenAI client.

    Args:
        api_key (Optional[Text], optional): The API key to use for authentication. Defaults to None.
    """
```

## Usage Examples

### Retrieving a Model

```python
voyage_models = VoyageModels()
model = voyage_models.retrieve("model-id")
print(model)
```

### Creating an Embedding

```python
voyage_embeddings = VoyageEmbeddings()
embedding = voyage_embeddings.create(input="Hello, World!", model="model-id")
print(embedding)
```

### Initializing the Client

```python
voyage_openai = VoyageOpenAI(api_key="your-api-key")
print(voyage_openai)
```

## Conclusion

The `languru.openai_plugins.clients.voyage` module provides essential functionalities for interacting with the Voyage AI platform. By following this documentation, developers can easily integrate the module into their projects and utilize its features for model management and embedding creation.
