import copy
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Text,
    Tuple,
    Union,
)

from openai.types.chat import ChatCompletionMessageParam
from pyassorted.string import (
    Bracket,
    extract_code_blocks,
    find_placeholders,
    multiple_replace,
)
from pydantic import BaseModel

from languru.prompts.repositories.assistant import explanation_co_star
from languru.prompts.repositories.user import (
    question_of_costar,
    request_to_rewrite_as_costar,
)
from languru.types.chat.completions import Message
from languru.utils.chat import chat_completion_once
from languru.utils.common import display_messages
from languru.utils.openai_utils import messages_to_md5

if TYPE_CHECKING:
    from openai import OpenAI


class PromptTemplate:
    def __init__(
        self,
        prompt: Optional[Text] = None,
        *,
        prompt_vars: Optional[Dict[Text, Any]] = None,
        messages: Optional[
            Union[
                Sequence["Message"],
                Sequence[Dict[Text, Any]],
                Sequence[ChatCompletionMessageParam],
            ]
        ] = None,
        role_system: Text = "system",
        role_user: Text = "user",
        role_assistant: Text = "assistant",
        **kwargs,
    ):
        self.prompt = prompt
        self._prompt_vars = MappingProxyType(prompt_vars or {})
        self.open_delim = "{"  # Not customizable yet
        self.close_delim = "}"  # Not customizable yet
        self.role_system = role_system
        self.role_user = role_user
        self.role_assistant = role_assistant
        self.messages: List[ChatCompletionMessageParam] = [  # type: ignore
            m.model_dump() if isinstance(m, Message) else m for m in messages or []
        ]

    @classmethod
    def from_description(
        cls,
        prompt_description: Text,
        client: "OpenAI",
        *,
        model: Text,
        example_user_queries: Optional[Sequence[Text]] = None,
        temperature: float = 0.7,
        verbose: bool = False,
        **kwargs,
    ):
        """
        Create an instance of the class from a prompt description using OpenAI's API.

        This method generates a prompt based on the given description, creates example
        messages if provided, and constructs the final prompt with examples.

        Parameters
        ----------
        prompt_description : Text
            A description of the desired prompt.
        client : OpenAI
            An instance of the OpenAI client for making API calls.
        model : Text
            The name of the OpenAI model to use for generating responses.
        example_user_queries : Optional[Sequence[Text]], optional
            A sequence of example user queries to generate responses for, by default None.
        temperature : float, optional
            The sampling temperature to use when generating responses, by default 0.3.
        verbose : bool, optional
            If True, display detailed information about API calls and responses, by default False.
        **kwargs : dict
            Additional keyword arguments to be passed to the class constructor.

        Returns
        -------
        cls
            An instance of the class initialized with the generated prompt and any additional
            parameters provided in kwargs.

        Raises
        ------
        ValueError
            If no markdown code block can be extracted from the API response.

        Notes
        -----
        This method uses the OpenAI API to generate a prompt based on the given description,
        and then uses that prompt to generate example responses if example queries are provided.
        The final prompt includes these examples and is used to initialize a new instance of the class.
        """  # noqa: E501

        # Build prompt by chat
        chat_answer = chat_completion_once(
            messages=[
                {"role": "user", "content": question_of_costar},
                {"role": "assistant", "content": explanation_co_star},
                {"role": "user", "content": request_to_rewrite_as_costar},
            ],
            client=client,
            model=model,
            prompt_vars={"PROMPT_DESCRIPTION": prompt_description},
            verbose=verbose,
            temperature=temperature,
            wrapped_by=Bracket.CurlyBrackets,
        )
        # Parse response
        code_blocks = extract_code_blocks(
            chat_answer, language="markdown", eob_missing_ok=True
        )
        code_blocks = [b.strip() for b in code_blocks if b.strip()]
        if len(code_blocks) == 0:
            raise ValueError(
                "Failed to extract a markdown code block from the response: "
                + f"{chat_answer}"
            )
        prompt_costar = code_blocks[-1].strip()

        # Generate example messages
        examples_messages: List[List["Message"]] = []
        for _ex_query in example_user_queries or []:
            _ex_query = _ex_query.strip()
            _ex_chat_answer = chat_completion_once(
                messages=[
                    {"role": "system", "content": prompt_costar},
                    {"role": "user", "content": _ex_query},
                ],
                client=client,
                model=model,
                verbose=verbose,
                temperature=temperature,
                wrapped_by=Bracket.CurlyBrackets,
            )
            examples_messages.append(
                [
                    Message.model_validate({"role": "user", "content": _ex_query}),
                    Message.model_validate(
                        {"role": "assistant", "content": _ex_chat_answer}
                    ),
                ]
            )

        # Add examples into the costar prompt
        if examples_messages:
            prompt_costar += "\n\n## Examples"
            prompt_costar = prompt_costar.strip()
            for idx, example_messages in enumerate(examples_messages):
                prompt_costar += f"\n\n### Example {idx + 1}\n\n"
                prompt_costar += display_messages(example_messages, is_print=False)
                prompt_costar = prompt_costar.strip()

        # Final prompt
        return cls(
            prompt=prompt_costar,
            prompt_vars=kwargs.get("prompt_vars"),
            messages=kwargs.get("messages"),
        )

    def __call__(
        self,
        messages: Optional[
            Union[
                Sequence["Message"],
                Sequence[Dict[Text, Any]],
                Sequence[ChatCompletionMessageParam],
            ]
        ] = None,
        *args,
        prompt_vars: Optional[Dict[Text, Any]] = None,
        **kwargs,
    ) -> List[ChatCompletionMessageParam]:
        """Format messages with prompt vars."""

        return self.format_messages(
            messages=messages, *args, prompt_vars=prompt_vars, **kwargs
        )

    def __str__(self):
        """Return a string representation of the object."""

        return f'<{self.__class__.__name__} md5="{self.md5_formatted}">'

    def __repr__(self):
        return self.__str__()

    @property
    def md5(self) -> Text:
        """Return the MD5 hash of the prompt messages."""

        _messages = self.prompt_messages()
        return messages_to_md5(_messages)

    @property
    def md5_formatted(self) -> Text:
        """Return the formatted MD5 hash of the prompt messages."""

        _messages = self.format_messages()
        return messages_to_md5(_messages)

    @property
    def prompt_vars(self) -> Dict[Text, Any]:
        """Return a copy of the prompt vars."""

        return dict(self._prompt_vars)

    def prompt_vars_update(
        self,
        data: Optional[Union[Dict[Text, Any], Sequence[Tuple[Text, Any]]]] = None,
        **kwargs,
    ) -> "PromptTemplate":
        """Update prompt vars."""

        prompt_vars = self.prompt_vars
        prompt_vars.update(data or {})
        prompt_vars.update(kwargs)
        self._prompt_vars = MappingProxyType(prompt_vars)
        return self

    def prompt_vars_drop(
        self, keys: Union[Text, Sequence[Text]], *args: Text, **kwargs
    ) -> "PromptTemplate":
        """Drop prompt vars."""

        keys = [keys] if isinstance(keys, Text) else keys
        prompt_vars = self.prompt_vars
        for key in keys:
            prompt_vars.pop(key, None)
        self._prompt_vars = MappingProxyType(prompt_vars)
        return self

    def prompt_placeholders(self, *args, **kwargs) -> List[Text]:
        """Return a list of placeholders in the prompt and messages."""

        out = find_placeholders(
            self.prompt or "", open_delim=self.open_delim, close_delim=self.close_delim
        )
        for m in self.messages:
            if "content" in m and isinstance(m["content"], Text):
                out += find_placeholders(
                    m["content"],
                    open_delim=self.open_delim,
                    close_delim=self.close_delim,
                )
        return out

    def prompt_messages(
        self,
        messages: Optional[
            Union[
                Sequence["Message"],
                Sequence[Dict[Text, Any]],
                Sequence[ChatCompletionMessageParam],
            ]
        ] = None,
        *args,
        **kwargs,
    ) -> List[ChatCompletionMessageParam]:
        """Return a list of raw messages with the prompt."""

        _messages: List[ChatCompletionMessageParam] = []
        if self.prompt:
            _messages.append(
                {"role": self.role_system, "content": self.prompt}  # type: ignore
            )
        _messages += copy.deepcopy(self.messages)
        if messages:
            _messages += [
                m.model_dump() if isinstance(m, BaseModel) else copy.deepcopy(m)
                for m in messages  # type: ignore
            ]
        return _messages

    def format_messages(
        self,
        messages: Optional[
            Union[
                Sequence["Message"],
                Sequence[Dict[Text, Any]],
                Sequence[ChatCompletionMessageParam],
            ]
        ] = None,
        *args,
        prompt_vars: Optional[Dict[Text, Any]] = None,
        **kwargs,
    ) -> List[ChatCompletionMessageParam]:
        """Format messages with prompt vars.

        Parameters
        ----------
        messages : Optional[Union[Sequence["Message"], Sequence[Dict[Text, Any], Sequence[ChatCompletionMessageParam]]]
            A list of messages to format.
        *args
            Additional arguments to pass to the prompt vars.
        prompt_vars : Optional[Dict[Text, Any]]
            A dictionary of prompt variables to use.
        **kwargs
            Additional keyword arguments to pass to the prompt vars.

        Returns
        -------
        List[ChatCompletionMessageParam]
            A list of formatted messages.
        """  # noqa

        # Update prompt vars
        _prompt_vars = self.prompt_vars
        _prompt_vars.update(prompt_vars or {})
        _prompt_vars.update(kwargs)
        _prompt_vars = {k: str(v) for k, v in _prompt_vars.items() if v is not None}

        # Collect messages
        _messages = self.prompt_messages(messages=messages, *args, **kwargs)

        # Format messages
        for m in _messages:
            if m_content := m.get("content"):
                if isinstance(m_content, Text):
                    m["content"] = multiple_replace(
                        _prompt_vars,
                        text=m_content,
                        wrapped_by=Bracket.CurlyBrackets,
                    )
        return _messages
