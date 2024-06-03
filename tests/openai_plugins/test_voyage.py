from typing import List, Text

import pytest

from languru.openai_plugins.clients.voyage import VoyageOpenAI

test_emb_model_name = "voyage-2"


vo_openai = VoyageOpenAI()


def test_voyage_openai_models_retrieve():
    model = vo_openai.models.retrieve(model=test_emb_model_name)
    assert model.id == test_emb_model_name


def test_voyage_openai_models_list():
    model = vo_openai.models.list()
    assert len(model.data) > 0


@pytest.mark.parametrize(
    "texts",
    [
        "Super Cub appeal has never gone out of fashion.",
        [
            (
                "In the city. Be where you want to be, when you want to be. "
                + "And enjoy every second."
            ),
            (
                "Looking for a new feel? Inject an extra, hugely enjoyable edge "
                + "into riding with lightweight form driven by responsive power."
            ),
        ],
    ],
)
def test_voyage_openai_embeddings_create(texts: Text | List[Text]):
    emb_res = vo_openai.embeddings.create(
        input=texts,
        model=test_emb_model_name,
    )
    assert emb_res.data
    assert len(emb_res.data) == len(texts) if isinstance(texts, List) else 1
    assert emb_res.data[0].embedding
