from typing import TYPE_CHECKING, Iterable, Optional, Text, Type

from openai.types.beta import thread_create_params

from languru.resources.sql.openai.backend.messages import Messages as MessagesBackend
from languru.resources.sql.openai.backend.runs import Runs as RunsBackend
from languru.types.sql._openai import Thread as OrmThread

if TYPE_CHECKING:
    from languru.resources.sql.openai.backend._client import OpenaiBackend


class Threads:
    messages: MessagesBackend
    runs: RunsBackend

    def __init__(
        self,
        client: "OpenaiBackend",
        *,
        orm_model: Type["OrmThread"] = OrmThread,
        **kwargs,
    ):
        self._client = client
        self.orm_model = orm_model

        self.messages = MessagesBackend(client=self._client)
        self.runs = RunsBackend(client=self._client)

    def create(
        self,
        thread: "OrmThread",
        messages: Optional[Iterable["thread_create_params.Message"]] = None,
    ) -> "OrmThread":
        with self._client.sql_session() as session:
            pass

    def retrieve(self, thread_id: Text) -> "OrmThread":
        with self._client.sql_session() as session:
            pass

    def update(self, thread_id: Text):
        pass

    def delete(self, thread_id: Text):
        with self._client.sql_session() as session:
            pass
