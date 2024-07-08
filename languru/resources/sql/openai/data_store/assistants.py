from typing import TYPE_CHECKING, Dict, Iterable, List, Literal, Optional, Text, Type

from openai.types.beta import assistant_create_params
from openai.types.beta.assistant import Assistant
from openai.types.beta.assistant_deleted import AssistantDeleted
from openai.types.beta.assistant_response_format_option_param import (
    AssistantResponseFormatOptionParam,
)
from openai.types.beta.assistant_tool_param import AssistantToolParam

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
        self.orm_assistant = orm_assistant

    def list(
        self,
        *,
        after: Optional[Text] = None,
        before: Optional[Text] = None,
        limit: Optional[int] = None,
        order: Literal["asc", "desc"] = "asc",
    ) -> List["Assistant"]:
        with self._client.sql_session() as session:
            query = session.query(self.orm_assistant)
            query = query.order_by(
                self.orm_assistant.created_at.desc()
                if order == "desc"
                else self.orm_assistant.created_at.asc()
            )
            if after is not None:
                query = query.filter(self.orm_assistant.db_id > after)
            if before is not None:
                query = query.filter(self.orm_assistant.db_id < before)
            if limit is not None:
                query = query.limit(limit)
            assistants = query.all()
            return [asst.to_openai() for asst in assistants]

    def create(self, assistant: "Assistant") -> "Assistant":
        with self._client.sql_session() as session:
            orm_assistant = self.orm_assistant.from_openai(assistant)
            session.add(orm_assistant)
            session.commit()
            session.refresh(orm_assistant)
            return orm_assistant.to_openai()

    def update(
        self,
        assistant_id: Text,
        *,
        model: Optional[Text] = None,
        description: Optional[Text] = None,
        instructions: Optional[Text] = None,
        metadata: Optional[Dict] = None,
        name: Optional[Text] = None,
        response_format: Optional[AssistantResponseFormatOptionParam] = None,
        temperature: Optional[float] = None,
        tool_resources: Optional[assistant_create_params.ToolResources] = None,
        tools: Optional[Iterable[AssistantToolParam]] = None,
        top_p: Optional[float] = None,
    ) -> "Assistant":
        with self._client.sql_session() as session:
            query = session.query(self.orm_assistant).filter(
                self.orm_assistant.id == assistant_id
            )
            assistant = query.one()
            if model is not None:
                assistant.model = model
            if description is not None:
                assistant.description = description
            if instructions is not None:
                assistant.instructions = instructions
            if metadata is not None:
                assistant.metadata = metadata
            if name is not None:
                assistant.name = name
            if response_format is not None:
                assistant.response_format = (
                    response_format
                    if isinstance(response_format, Text)
                    else dict(response_format)
                )
            if temperature is not None:
                assistant.temperature = temperature
            if tool_resources is not None:
                assistant.tool_resources = dict(tool_resources)
            if tools is not None:
                assistant.tools = [dict(t) for t in tools]
            if top_p is not None:
                assistant.top_p = top_p
            session.commit()
            session.refresh(assistant)
            return assistant.to_openai()

    def delete(self) -> "AssistantDeleted":
        pass

    def retrieve(self) -> "Assistant":
        pass
