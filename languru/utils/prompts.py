from typing import Optional, Set, Text

from jinja2 import Environment as Jinja2Environment
from jinja2 import meta as jinja2_meta


def find_placeholders(
    prompt: Text, env: Optional["Jinja2Environment"] = None
) -> Set[Text]:
    """Find undeclared variables (placeholders) in a Jinja2 template.

    This function analyzes a given Jinja2 template string and identifies
    any variables that are referenced but not declared within the template.
    It utilizes the Jinja2 environment to parse the template and extract
    the undeclared variables.

    Parameters
    ----------
    prompt : Text
        The Jinja2 template string to be analyzed. This string may contain
        placeholders that are expected to be filled with actual values.

    env : Optional[Jinja2Environment], optional
        An optional Jinja2 environment instance. If not provided, a new
        Jinja2 environment will be created. This environment is used to
        parse the template and find undeclared variables.

    Returns
    -------
    Set[Text]
        A set of variable names (placeholders) that are referenced in the
        template but not declared. This can be useful for debugging
        templates or ensuring that all necessary variables are provided
        before rendering.

    Examples
    --------
    >>> template = "Hello, {{ name }}! Welcome to {{ place }}."
    >>> find_placeholders(template)
    {'name', 'place'}
    """  # noqa: E501

    jinja_env = env or Jinja2Environment()
    parsed_content = jinja_env.parse(prompt)
    variables = jinja2_meta.find_undeclared_variables(parsed_content)
    return variables
