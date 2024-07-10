from typing import TYPE_CHECKING, Type

from languru.types.sql._openai import Message as OrmMessage

if TYPE_CHECKING:
    from languru.resources.sql.openai.backend._client import OpenaiBackend


class Messages:
    def __init__(
        self,
        client: "OpenaiBackend",
        *,
        orm_model: Type["OrmMessage"] = OrmMessage,
        **kwargs,
    ):
        self._client = client
        self.orm_model = orm_model

    def create(self):
        pass

    def list(self):
        pass

    def retrieve(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass
