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
from languru.types.sql._openai import Assistant as OrmAssistant

if TYPE_CHECKING:
    from languru.resources.sql.openai.backend._client import OpenaiBackend


class Assistants:
    def __init__(
        self,
        client: "OpenaiBackend",
        *,
        orm_model: Type["OrmAssistant"] = OrmAssistant,
        **kwargs,
    ):
        self._client = client
        self.orm_model = orm_model

    def list(
        self,
        *,
        after: Optional[int] = None,
        before: Optional[int] = None,
        limit: Optional[int] = None,
        order: Optional[Literal["asc", "desc"]] = None,
    ) -> List["Assistant"]:
        with self._client.sql_session() as session:
            query = session.query(self.orm_model)

            # Apply sorting
            if order == "desc":
                query = query.order_by(self.orm_model.created_at.desc())
            else:
                query = query.order_by(self.orm_model.created_at.asc())

            # Apply pagination using after
            if after is not None:
                try:
                    after_instance = (
                        session.query(self.orm_model)
                        .filter(self.orm_model.db_id == after)
                        .one()
                    )
                    if order == "asc":
                        query = query.filter(
                            self.orm_model.created_at > after_instance.created_at
                        )
                    else:
                        query = query.filter(
                            self.orm_model.created_at < after_instance.created_at
                        )
                except sqlalchemy.exc.NoResultFound:
                    raise NotFound(f"Assistant with ID {after} not found.")

            # Apply pagination using before
            if before is not None:
                try:
                    before_instance = (
                        session.query(self.orm_model)
                        .filter(self.orm_model.db_id == before)
                        .one()
                    )
                    if order == "asc":
                        query = query.filter(
                            self.orm_model.created_at < before_instance.created_at
                        )
                    else:
                        query = query.filter(
                            self.orm_model.created_at > before_instance.created_at
                        )
                except sqlalchemy.exc.NoResultFound:
                    raise NotFound(f"Assistant with ID {before} not found.")

            # Apply limit
            if limit is not None:
                query = query.limit(limit)

            # Execute query and return results
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
        with self._client.sql_session() as session:
            query = session.query(self.orm_model).filter(
                self.orm_model.id == assistant_id
            )
            assistant = query.first()
            if assistant is None:
                if not_exist_ok:
                    return AssistantDeleted.model_validate(
                        {
                            "id": assistant_id,
                            "deleted": False,
                            "object": "assistant.deleted",
                        }
                    )
                raise NotFound(f"Assistant with ID {assistant_id} not found.")

            session.delete(assistant)
            session.commit()
            return AssistantDeleted.model_validate(
                {"id": assistant_id, "deleted": True, "object": "assistant.deleted"}
            )

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
