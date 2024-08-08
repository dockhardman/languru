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
    Note 3: Keep prompt briefly and concisely.
    """  # noqa: E501
).strip()
request_to_rewrite_as_costar_concise: Final[Text] = (
    request_to_rewrite_as_costar + "\nNote 3: Keep prompt briefly and concisely."
)

documentation_planner: Final[Text] = dedent(
    """
    ## Context

    A software development environment where a specific module named {{module_name}} needs to be analyzed and documented. The module's codebase is available as an attachment or in user query.

    ## Objective

    1. Read and analyze the codebase of the {{module_name}} module.
    2. Provide a detailed explanation of the module's functionality and structure.
    3. Generate creative hypotheses about the module's purpose and potential improvements.
    4. Develop an optimal document structure based on the module's characteristics.
    5. Create a comprehensive plan for documenting the {{module_name}} module.

    ## Style

    Technical and analytical, with a focus on clarity and detail. The writing should be structured and systematic, suitable for software documentation.

    ## Tone

    Professional and objective, with an emphasis on providing insightful analysis and creative thinking.

    ## Audience

    Software developers, technical writers, and other professionals involved in maintaining and documenting the codebase. The audience is assumed to have a strong technical background and familiarity with software development concepts.

    ## Response

    The response should be provided in a structured format, including:

    1. A detailed analysis of the {{module_name}} module's codebase, explaining its functionality, structure, and key components.
    2. A list of creative hypotheses about the module's purpose, potential improvements, or interesting aspects discovered during analysis.
    3. A proposed document structure for the {{module_name}} module, tailored to its specific characteristics and complexity.
    4. A comprehensive plan outlining the steps to document the {{module_name}} module, including sections to be covered, required diagrams or illustrations, and any special considerations based on the module's unique features.

    The response should be written in markdown format, using appropriate headers, lists, and code blocks where necessary to enhance readability and organization.
    """  # noqa: E501
).strip()
