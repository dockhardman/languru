from languru.openai_plugins.clients.pplx import PerplexityOpenAI

test_chat_model_name = "llama-3-sonar-small-32k-chat"


pplx_openai = PerplexityOpenAI()


def test_google_openai_models_retrieve():
    model = pplx_openai.models.retrieve(model=test_chat_model_name)
    assert model.id == test_chat_model_name


def test_google_openai_models_list():
    model_res = pplx_openai.models.list()
    assert len(model_res.data) > 0 and any(
        [m.id == test_chat_model_name for m in model_res.data]
    )
