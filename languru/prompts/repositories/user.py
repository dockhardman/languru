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

request_to_rewrite_as_costar: Final[Text] = dedent(
    """
    I want to create a co-star prompt, the original prompt is as follows:

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
    Note 3: Keep all mentioned instructions in the co-star prompt as much as possible.
    """  # noqa: E501
).strip()

request_to_rewrite_as_costar_concise: Final[Text] = dedent(
    """
    I want to create a co-star prompt, the original prompt is as follows:

    ```
    {{ PROMPT_DESCRIPTION }}
    ```

    Please rewrite the prompt above as CO-STAR framework step by step:

    1. Analyze the prompt and provide a detailed explanation.
    2. Come up with some hypotheses creatively.
    3. Finally, provide a response in a xml code block format as shown below:

    ```xml
    <context description={THE_MOST_CONCISE_AND_PRECISE_CONTEXT_DESCRIPTION}>
    {CONTEXT}
    </context>

    <objective description={THE_MOST_CONCISE_AND_PRECISE_OBJECTIVE_DESCRIPTION}>
    {OBJECTIVE}
    </objective>

    <style description={THE_MOST_CONCISE_AND_PRECISE_STYLE_DESCRIPTION}>
    {STYLE}
    </style>

    <tone description={THE_MOST_CONCISE_AND_PRECISE_TONE_DESCRIPTION}>
    {TONE}
    </tone>

    <audience description={THE_MOST_CONCISE_AND_PRECISE_AUDIENCE_DESCRIPTION}>
    {AUDIENCE}
    </audience>

    <response description={THE_MOST_CONCISE_AND_PRECISE_RESPONSE_DESCRIPTION}>
    {RESPONSE}
    </response>
    ```

    Note 1: Please ensure that the response is in the correct markdown format in a code snippet.
    Note 2: The chat example is not required for this prompt.
    Note 3: Keep all mentioned instructions in the co-star prompt as much as possible.
    Note 4: Keep prompt briefly and concisely.
    """  # noqa: E501
).strip()

request_to_distill_into_a_sentence: Final[Text] = dedent(
    """
    Could you distill the document above into a sentence which be the most concise and precise response description?
    """  # noqa: E501
).strip()
