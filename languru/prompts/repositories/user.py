from textwrap import dedent
from typing import Final, Text

question_of_costar: Final[Text] = dedent(
    """
    The CO-STAR prompt framework is :

    **Context (C) :** Providing background information helps the LLM understand the specific scenario.

    **Objective (O):** Clearly defining the task directs the LLM’s focus.

    **Style (S):** Specifying the desired writing style aligns the LLM response.

    **Tone (T):** Setting the tone ensures the response resonates with the required sentiment.

    **Audience (A):** Identifying the intended audience tailors the LLM’s response to be targeted to an audience.

    **Response (R):** Providing the response format, like text or json, ensures the LLM outputs, and help build pipelines.

    Please explain it with gradually increasing complexity.
    """  # noqa: E501
).strip()

request_to_rewrite_as_costar = dedent(
    """
    ```
    {PROMPT_DESCRIPTION}
    ```

    Please rewrite the prompt above as CO-STAR framework step by step:

    1. Analyze the prompt and provide a detailed explanation.
    2. Come up with some hypotheses creatively.
    3. Finally, provide a response in the markdown code block format as shown below:

        ```markdown
        ## Context

        {CONTEXT}

        ## Objective

        {OBJECTIVE}

        ## Style

        {STYLE}

        ## Tone

        {TONE}

        ## Audience

        {AUDIENCE}

        ## Response

        {RESPONSE}
        ```

    Note 1: Please ensure that the response is in the correct markdown format in a code snippet.
    Note 2: The chat example is not required for this prompt.
    """  # noqa: E501
).strip()
