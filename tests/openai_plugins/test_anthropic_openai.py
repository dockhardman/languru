from languru.openai_plugins.clients.anthropic import AnthropicOpenAI

test_chat_model_name = "claude-3-haiku-20240307"


claude_openai = AnthropicOpenAI()


def test_claude_openai_models_retrieve():
    model = claude_openai.models.retrieve(model=test_chat_model_name)
    assert model.id == test_chat_model_name


def test_claude_openai_models_list():
    model_res = claude_openai.models.list()
    assert len(model_res.data) > 0 and any(
        [m.id == test_chat_model_name for m in model_res.data]
    )
