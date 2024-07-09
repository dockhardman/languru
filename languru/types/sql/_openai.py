from typing import Dict, Iterable, List, Optional, Text, Union

import sqlalchemy as sa
from openai.types.beta import assistant_create_params
from openai.types.beta.assistant import Assistant as OpenaiAssistant
from openai.types.beta.assistant_response_format_option_param import (
    AssistantResponseFormatOptionParam,
)
from openai.types.beta.assistant_tool_param import AssistantToolParam
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
            assistant_metadata=assistant.metadata,
            model=assistant.model,
            name=assistant.name,
            object=assistant.object,
            tools=assistant.tools,
            response_format=assistant.response_format,
            temperature=assistant.temperature,
            tool_resources=assistant.tool_resources,
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
                else dict(response_format)
            )
        if temperature is not None:
            self.temperature = temperature
        if tool_resources is not None:
            self.tool_resources = dict(tool_resources)
        if tools is not None:
            self.tools = [dict(t) for t in tools]
        if top_p is not None:
            self.top_p = top_p


__all__ = ["Assistant"]
