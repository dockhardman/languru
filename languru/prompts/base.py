from types import MappingProxyType
from typing import Any, Dict, List, Optional, Sequence, Text, Tuple, Union

from pyassorted.string import Bracket, find_placeholders, multiple_replace


class PromptTemplate:
    def __init__(
        self,
        prompt: Text,
        *,
        prompt_vars: Optional[Dict[Text, Any]] = None,
        **kwargs,
    ):
        self.prompt = prompt
        self._prompt_vars = MappingProxyType(prompt_vars or {})
        self.open_delim = "{"  # Not customizable yet
        self.close_delim = "}"  # Not customizable yet

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

    def format(self, *args, **kwargs) -> Text:
        prompt_vars = self.prompt_vars
        prompt_vars.update(kwargs)
        return multiple_replace(
            prompt_vars, text=self.prompt, wrapped_by=Bracket.CurlyBrackets
        )
