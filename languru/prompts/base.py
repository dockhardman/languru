import copy
import hashlib
import json
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
from languru.utils.common import display_messages, ensure_openai_chat_completion_content
from languru.utils.prompt import ensure_chat_completion_message_params

if TYPE_CHECKING:
    from openai import OpenAI
    from openai.types.chat import ChatCompletion


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
        temperature: float = 0.3,
        verbose: bool = False,
        **kwargs,
    ):
        # Build prompt
        messages_to_gen_prompt = [
            {
                "role": "user",
                "content": question_of_costar,
            },
            {
                "role": "assistant",
                "content": explanation_co_star,
            },
            {
                "role": "user",
                "content": multiple_replace(
                    {"PROMPT_DESCRIPTION": prompt_description},
                    request_to_rewrite_as_costar,
                    wrapped_by=Bracket.CurlyBrackets,
                ),
            },
        ]
        if verbose:
            display_messages(
                messages=messages_to_gen_prompt,
                table_title=f"{client.__class__.__name__} Chat Messages Input",
            )
        # Generate response
        chat_res: "ChatCompletion" = client.chat.completions.create(
            messages=ensure_chat_completion_message_params(messages_to_gen_prompt),
            model=model,
            temperature=temperature,
            stream=False,
        )  # type: ignore
        chat_answer = ensure_openai_chat_completion_content(chat_res)
        if verbose:
            display_messages(
                messages=[{"role": "assistant", "content": chat_answer}],
                table_title=f"{client.__class__.__name__}({model}) Chat Response",
            )
        # Parse response
        code_blocks = extract_code_blocks(chat_answer, language="markdown")
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
            _ex_messages: List["Message"] = [
                Message.model_validate({"role": "user", "content": _ex_query})
            ]
            messages_input = [
                {"role": "system", "content": prompt_costar},
                {"role": "user", "content": _ex_query},
            ]
            if verbose:
                display_messages(
                    messages=messages_input,
                    table_title=f"{client.__class__.__name__} Chat Messages Input",
                )
            chat_res: "ChatCompletion" = client.chat.completions.create(
                messages=ensure_chat_completion_message_params(messages_input),
                model=model,
                temperature=temperature,
                stream=False,
            )  # type: ignore
            chat_answer = ensure_openai_chat_completion_content(chat_res)
            if verbose:
                display_messages(
                    messages=[{"role": "assistant", "content": chat_answer}],
                    table_title=f"{client.__class__.__name__}({model}) Chat Response",
                )
            _ex_messages.append(
                Message.model_validate({"role": "assistant", "content": chat_answer})
            )
            examples_messages.append(_ex_messages)

        # Add examples into the costar prompt
        prompt_costar = prompt_costar.strip()
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

        _messages = self.prompt_messages()
        _messages_md5 = hashlib.md5(
            json.dumps(_messages, sort_keys=True, default=str).encode()
        ).hexdigest()
        return f'<{self.__class__.__name__} md5="{_messages_md5}">'

    def __repr__(self):
        return self.__str__()

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
        _messages += self.messages
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
