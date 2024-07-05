from languru.openai_plugins.clients.pplx import PerplexityOpenAI
from languru.prompts import PromptTemplate

client = PerplexityOpenAI()
model = "llama-3-sonar-small-32k-chat"


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
