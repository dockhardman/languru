from typing import TYPE_CHECKING, List, Literal, Optional, Text, Type

from openai.types.beta.assistant import Assistant
from openai.types.beta.assistant_deleted import AssistantDeleted
from sqlalchemy.orm import Session

from languru.types.sql.openai import Assistant as OrmAssistant

if TYPE_CHECKING:
    from languru.resources.sql.openai.data_store.client import DataStoreClient


class AssistantClient:
    def __init__(
        self,
        client: "DataStoreClient",
        *,
        orm_assistant: Type["OrmAssistant"],
        **kwargs,
    ):
        self._client = client
        self._orm_assistant = orm_assistant

    def list(
        self,
        *,
        after: Optional[Text] = None,
        before: Optional[Text] = None,
        limit: Optional[int] = None,
        order: Literal["asc", "desc"] = "asc",
    ) -> List["Assistant"]:
        with Session(self._client.sql_engine) as session:
            query = session.query(OrmAssistant)
            query = query.order_by(
                OrmAssistant.created_at.desc()
                if order == "desc"
                else OrmAssistant.created_at.asc()
            )
            if after is not None:
                query = query.filter(OrmAssistant.db_id > after)
            if before is not None:
                query = query.filter(OrmAssistant.db_id < before)
            if limit is not None:
                query = query.limit(limit)
            assistants = query.all()
            return [asst.to_openai() for asst in assistants]

    def create(self) -> "Assistant":
        pass

    def update(self) -> "Assistant":
        pass

    def delete(self) -> "AssistantDeleted":
        pass

    def retrieve(self) -> "Assistant":
        pass
