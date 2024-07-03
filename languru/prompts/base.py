import copy
import hashlib
import json
from types import MappingProxyType
from typing import Any, Dict, List, Optional, Sequence, Text, Tuple, Union

from openai.types.chat import ChatCompletionMessageParam
from pyassorted.string import Bracket, find_placeholders, multiple_replace
from pydantic import BaseModel

from languru.types.chat.completions import Message


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
