from typing import TYPE_CHECKING, Type

from openai.types.beta.threads.message import Message

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

    def create(self, message: "Message") -> "Message":
        with self._client.sql_session() as session:
            orm_message = self.orm_model.from_openai(message)
            session.add(orm_message)
            session.commit()
            session.refresh(orm_message)
            return orm_message.to_openai()

    def list(self):
        pass

    def retrieve(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass
