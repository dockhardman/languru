from typing import TYPE_CHECKING, Dict, Iterable, List, Literal, Optional, Text, Type

import sqlalchemy.exc
from openai.types.beta import assistant_create_params
from openai.types.beta.assistant import Assistant
from openai.types.beta.assistant_deleted import AssistantDeleted
from openai.types.beta.assistant_response_format_option_param import (
    AssistantResponseFormatOptionParam,
)
from openai.types.beta.assistant_tool_param import AssistantToolParam

from languru.exceptions import NotFound
from languru.resources.sql.openai.backend.threads import Threads as ThreadsBackend
from languru.types.sql._openai import Assistant as OrmAssistant

if TYPE_CHECKING:
    from languru.resources.sql.openai.backend._client import OpenaiBackend


class Assistants:
    threads: ThreadsBackend

    def __init__(
        self,
        client: "OpenaiBackend",
        *,
        orm_model: Type["OrmAssistant"] = OrmAssistant,
        **kwargs,
    ):
        self._client = client
        self.orm_model = orm_model

        self.threads = ThreadsBackend(client=self._client)

    def list(
        self,
        *,
        after: Optional[Text] = None,
        before: Optional[Text] = None,
        limit: Optional[int] = None,
        order: Literal["asc", "desc"] = "asc",
    ) -> List["Assistant"]:
        with self._client.sql_session() as session:
            query = session.query(self.orm_model)
            query = query.order_by(
                self.orm_model.created_at.desc()
                if order == "desc"
                else self.orm_model.created_at.asc()
            )
            if after is not None:
                query = query.filter(self.orm_model.db_id > after)
            if before is not None:
                query = query.filter(self.orm_model.db_id < before)
            if limit is not None:
                query = query.limit(limit)
            assistants = query.all()
            return [asst.to_openai() for asst in assistants]

    def create(self, assistant: "Assistant") -> "Assistant":
        with self._client.sql_session() as session:
            orm_assistant = self.orm_model.from_openai(assistant)
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
        try:
            with self._client.sql_session() as session:
                query = session.query(self.orm_model).filter(
                    self.orm_model.id == assistant_id
                )
                assistant = query.one()
                assistant.update(
                    model=model,
                    description=description,
                    instructions=instructions,
                    metadata=metadata,
                    name=name,
                    response_format=response_format,
                    temperature=temperature,
                    tool_resources=tool_resources,
                    tools=tools,
                    top_p=top_p,
                )
                session.commit()
                session.refresh(assistant)
                return assistant.to_openai()
        except sqlalchemy.exc.NoResultFound:
            raise NotFound(f"Assistant with ID {assistant_id} not found.")

    def delete(
        self, assistant_id: Text, *, not_exist_ok: bool = False
    ) -> "AssistantDeleted":
        try:
            with self._client.sql_session() as session:
                query = session.query(self.orm_model).filter(
                    self.orm_model.id == assistant_id
                )
                assistant = query.one()
                session.delete(assistant)
                session.commit()
                return AssistantDeleted.model_validate(
                    {"id": assistant_id, "deleted": True, "object": "assistant.deleted"}
                )
        except sqlalchemy.exc.NoResultFound:
            if not_exist_ok:
                return AssistantDeleted.model_validate(
                    {
                        "id": assistant_id,
                        "deleted": False,
                        "object": "assistant.deleted",
                    }
                )
            else:
                raise NotFound(f"Assistant with ID {assistant_id} not found.")

    def retrieve(self, assistant_id: Text) -> "Assistant":
        try:
            with self._client.sql_session() as session:
                query = session.query(self.orm_model).filter(
                    self.orm_model.id == assistant_id
                )
                assistant = query.one()
                return assistant.to_openai()
        except sqlalchemy.exc.NoResultFound:
            raise NotFound(f"Assistant with ID {assistant_id} not found.")
