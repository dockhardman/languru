from rich import print

from languru.action.base import ModelDeploy
from languru.action.hf import TransformersAction


class SentenceTransformersParaphraseMultilingualMiniLML12V2Action(TransformersAction):
    # Model configuration
    MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    model_deploys = (
        ModelDeploy(MODEL_NAME, MODEL_NAME),
        ModelDeploy("MiniLM-L12-v2", MODEL_NAME),
    )


if __name__ == "__main__":

    action = SentenceTransformersParaphraseMultilingualMiniLML12V2Action()
    print(f"Health: {action.health()}")

    # Embedding
    res = action.embeddings("Hello, world!", model=action.model_name)
    print(res.model_dump(exclude={"data": {-1: {"embedding"}}}))
    # Batch embedding
    res = action.embeddings(["Hello", "world!"], model=action.model_name)
    print(res.model_dump(exclude={"data": {-1: {"embedding"}}}))
