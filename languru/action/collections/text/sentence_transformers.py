from typing import Text

from languru.action.base import ModelDeploy
from languru.action.hf import TransformersAction


class ParaphraseMultilingualMiniLML12Action(TransformersAction):
    MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    model_deploys = (
        ModelDeploy(MODEL_NAME, MODEL_NAME),
        ModelDeploy("MiniLM-L12-v2", MODEL_NAME),
    )
    is_causal_lm: bool = False

    def name(self) -> Text:
        return "paraphrase_multilingual_minilm_l12_action"


class ParaphraseMultilingualMpnetAction(TransformersAction):
    MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

    is_causal_lm: bool = False

    def name(self) -> Text:
        return "paraphrase_multilingual_mpnet_action"


class SentenceTransformersLaBSE(TransformersAction):
    MODEL_NAME = "sentence-transformers/LaBSE"

    is_causal_lm: bool = False

    def name(self) -> Text:
        return "sentence_transformers_labse"


if __name__ == "__main__":
    from rich import print

    action_class = ParaphraseMultilingualMiniLML12Action

    print(f"Loading {action_class.MODEL_NAME} ...")
    action = action_class()
    print(f'Loaded Model "{action_class.MODEL_NAME}" Health: {action.health()}')
    print()

    # Embedding
    res = action.embeddings("Hello, world!", model=action.model_name)
    assert len(res.data[0].embedding) == 384
