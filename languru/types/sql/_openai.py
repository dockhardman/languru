from typing import Dict, Iterable, List, Optional, Text, Union

import sqlalchemy as sa
from openai.types.beta import assistant_create_params
from openai.types.beta.assistant import Assistant as OpenaiAssistant
from openai.types.beta.assistant_response_format_option_param import (
    AssistantResponseFormatOptionParam,
)
from openai.types.beta.assistant_tool_param import AssistantToolParam
from openai.types.beta.thread import Thread as OpenaiThread
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from languru.utils.common import model_dump


class Base(DeclarativeBase):
    pass


class Assistant(Base):
    __tablename__ = "assistants"

    db_id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    id: Mapped[Text] = mapped_column(sa.String, index=True)
    created_at: Mapped[int] = mapped_column(sa.Integer, index=True)
    description: Mapped[Text] = mapped_column(sa.String, nullable=True)
    instructions: Mapped[Text] = mapped_column(sa.String, nullable=True)
    assistant_metadata: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    model: Mapped[Text] = mapped_column(sa.String)
    name: Mapped[Text] = mapped_column(sa.String, nullable=True)
    object: Mapped[Text] = mapped_column(sa.String, nullable=True)
    tools: Mapped[List[Dict]] = mapped_column(sa.JSON, nullable=True)
    response_format: Mapped[Union[Text, Dict]] = mapped_column(sa.JSON, nullable=True)
    temperature: Mapped[float] = mapped_column(sa.Float, nullable=True)
    tool_resources: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    top_p: Mapped[float] = mapped_column(sa.Float, nullable=True)

    @classmethod
    def from_openai(cls, assistant: OpenaiAssistant) -> "Assistant":
        return cls(
            id=assistant.id,
            created_at=assistant.created_at,
            description=assistant.description,
            instructions=assistant.instructions,
            assistant_metadata=model_dump(assistant.metadata),
            model=assistant.model,
            name=assistant.name,
            object=assistant.object,
            tools=model_dump(assistant.tools),
            response_format=model_dump(assistant.response_format),
            temperature=assistant.temperature,
            tool_resources=model_dump(assistant.tool_resources),
            top_p=assistant.top_p,
        )

    def to_openai(self):
        return OpenaiAssistant.model_validate(
            {
                "id": self.id,
                "created_at": self.created_at,
                "description": self.description,
                "instructions": self.instructions,
                "metadata": self.assistant_metadata,
                "model": self.model,
                "name": self.name,
                "object": self.object,
                "tools": self.tools,
                "response_format": self.response_format,
                "temperature": self.temperature,
                "tool_resources": self.tool_resources,
                "top_p": self.top_p,
            }
        )

    def update(
        self,
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
        **kwargs,
    ):
        if model is not None:
            self.model = model
        if description is not None:
            self.description = description
        if instructions is not None:
            self.instructions = instructions
        if metadata is not None:
            self.assistant_metadata = metadata
        if name is not None:
            self.name = name
        if response_format is not None:
            self.response_format = (
                response_format
                if isinstance(response_format, Text)
                else model_dump(response_format)
            )
        if temperature is not None:
            self.temperature = temperature
        if tool_resources is not None:
            self.tool_resources = model_dump(tool_resources)
        if tools is not None:
            self.tools = [model_dump(t) for t in tools]
        if top_p is not None:
            self.top_p = top_p


class Thread(Base):
    __tablename__ = "threads"

    id: Mapped[Text] = mapped_column(sa.String, primary_key=True)
    created_at: Mapped[int] = mapped_column(sa.Integer)
    thread_metadata: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    object: Mapped[Text] = mapped_column(sa.String)
    tool_resources: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)

    @classmethod
    def from_openai(cls, thread: OpenaiThread) -> "Thread":
        return cls(
            id=thread.id,
            created_at=thread.created_at,
            thread_metadata=model_dump(thread.metadata),
            object=thread.object,
            tool_resources=model_dump(thread.tool_resources),
        )

    def to_openai(self):
        return OpenaiThread.model_validate(
            {
                "id": self.id,
                "created_at": self.created_at,
                "metadata": self.thread_metadata,
                "object": self.object,
                "tool_resources": self.tool_resources,
            }
        )

    def update(
        self,
        *,
        metadata: Optional[Dict] = None,
        tool_resources: Optional[assistant_create_params.ToolResources] = None,
        **kwargs,
    ):
        if metadata is not None:
            self.thread_metadata = metadata
        if tool_resources is not None:
            self.tool_resources = model_dump(tool_resources)


__all__ = ["Assistant", "Thread"]
