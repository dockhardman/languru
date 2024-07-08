from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from languru.resources.sql.openai.data_store.client import DataStoreClient
    from languru.types.sql.openai_orm import Assistant as OrmAssistant


class AssistantClient:
    def __init__(
        self,
        client: "DataStoreClient",
        *,
        orm_assistant: Type["OrmAssistant"],
        **kwargs
    ):
        self._client = client
        self._orm_assistant = orm_assistant
