import copy
from types import MappingProxyType
from typing import Any, Dict, List, Optional, Sequence, Text, Tuple, Union

from openai.types.chat import ChatCompletionMessageParam
from pyassorted.string import Bracket, find_placeholders, multiple_replace
from pydantic import BaseModel

from languru.types.chat.completions import Message


class PromptTemplate:
    def __init__(
        self,
        prompt: Text,
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

    def __call__(self, *args, **kwargs) -> Text:
        return self.format(*args, **kwargs)

    def __str__(self):
        return self.prompt

    def __repr__(self):
        return f"<PromptTemplate: {self.prompt}>"

    @property
    def prompt_vars(self) -> Dict[Text, Any]:
        return dict(self._prompt_vars)

    def prompt_vars_update(
        self,
        data: Optional[Union[Dict[Text, Any], Sequence[Tuple[Text, Any]]]] = None,
        **kwargs,
    ) -> "PromptTemplate":
        prompt_vars = self.prompt_vars
        prompt_vars.update(data or {})
        prompt_vars.update(kwargs)
        self._prompt_vars = MappingProxyType(prompt_vars)
        return self

    def prompt_vars_drop(
        self, keys: Union[Text, Sequence[Text]], *args: Text, **kwargs
    ) -> "PromptTemplate":
        keys = [keys] if isinstance(keys, Text) else keys
        prompt_vars = self.prompt_vars
        for key in keys:
            prompt_vars.pop(key, None)
        self._prompt_vars = MappingProxyType(prompt_vars)
        return self

    def prompt_placeholders(self, *args, **kwargs) -> List[Text]:
        return find_placeholders(
            self.prompt, open_delim=self.open_delim, close_delim=self.close_delim
        )

    def format(
        self, *args, prompt_vars: Optional[Dict[Text, Any]] = None, **kwargs
    ) -> Text:
        _prompt_vars = self.prompt_vars
        _prompt_vars.update(prompt_vars or {})
        _prompt_vars.update(kwargs)
        return multiple_replace(
            _prompt_vars, text=self.prompt, wrapped_by=Bracket.CurlyBrackets
        )

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
        _prompt_vars = self.prompt_vars
        _prompt_vars.update(prompt_vars or {})
        _prompt_vars.update(kwargs)
        _prompt_vars = {k: str(v) for k, v in _prompt_vars.items() if v is not None}
        _messages: List[ChatCompletionMessageParam] = copy.deepcopy(
            [{"role": self.role_system, "content": self.prompt}]
            + self.messages
            + [
                m.model_dump() if isinstance(m, BaseModel) else m
                for m in messages or []
            ],  # type: ignore
        )
        for m in _messages:
            if m_content := m.get("content"):
                if isinstance(m_content, Text):
                    m["content"] = multiple_replace(
                        _prompt_vars,
                        text=m_content,
                        wrapped_by=Bracket.CurlyBrackets,
                    )
        return _messages
