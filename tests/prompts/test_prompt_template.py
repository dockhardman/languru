from pprint import pformat

from languru.openai_plugins.clients.pplx import PerplexityOpenAI
from languru.prompts import PromptTemplate

client = PerplexityOpenAI()
model = "llama-3.1-sonar-small-128k-chat"


def test_prompt_template_from_description():
    prompt_template = PromptTemplate.from_description(
        prompt_description=(
            "You are a subtle humorous politician "
            + "who is concerned about energy issues."
        ),
        client=client,
        model=model,
        example_user_queries=[
            "Respond simply and concisely. "
            + "What is your opinion on nuclear energy?",
        ],
        verbose=True,
    )
    assert prompt_template.prompt


def test_prompt_template_operations():
    type_ = "joke"
    name = "Alex"
    prompt_template = PromptTemplate(
        prompt="You are a short {type} funny talker.",
        messages=[
            {"role": "user", "content": "What's your name?"},
            {"role": "assistant", "content": "My name is {name}, a jokester."},
        ],
        prompt_vars={"type": type_},
    )

    # Test prompt variables
    assert "type" in prompt_template.prompt_vars
    assert "name" not in prompt_template.prompt_vars
    prompt_template.prompt_vars_update({"name": name, "gg": "gg"})
    assert "name" in prompt_template.prompt_vars
    assert "gg" in prompt_template.prompt_vars
    prompt_template.prompt_vars_drop(["gg"])
    assert "gg" not in prompt_template.prompt_vars

    # Test prompt placeholders
    assert "type" in prompt_template.prompt_placeholders()
    assert "name" in prompt_template.prompt_placeholders()
    assert "gg" not in prompt_template.prompt_placeholders()

    # Test md5
    _md5 = prompt_template.md5
    _md5_formatted = prompt_template.md5_formatted
    prompt_template.prompt_vars_update({"name": "Bob"})
    assert _md5 == prompt_template.md5
    assert _md5_formatted != prompt_template.md5_formatted
    prompt_template.prompt_vars_update({"name": name})
    assert _md5 == prompt_template.md5
    assert _md5_formatted == prompt_template.md5_formatted

    # Test format messages
    _prompt_messages = prompt_template.prompt_messages()
    _format_messages = prompt_template.format_messages()
    assert pformat(_prompt_messages) != pformat(_format_messages)
