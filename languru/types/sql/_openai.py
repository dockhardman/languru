from typing import Dict, Iterable, List, Optional, Text, Union

import sqlalchemy as sa
from openai.types.beta.assistant import Assistant as OpenaiAssistant
from openai.types.beta.assistant import ToolResources
from openai.types.beta.assistant_response_format_option import (
    AssistantResponseFormatOption,
)
from openai.types.beta.assistant_tool import AssistantTool
from openai.types.beta.thread import Thread as OpenaiThread
from openai.types.beta.threads.message import Message as OpenaiMessage
from openai.types.beta.threads.run import Run as OpenaiRun
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
        response_format: Optional[AssistantResponseFormatOption] = None,
        temperature: Optional[float] = None,
        tool_resources: Optional[ToolResources] = None,
        tools: Optional[Iterable[AssistantTool]] = None,
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

    db_id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    id: Mapped[Text] = mapped_column(sa.String, index=True)
    created_at: Mapped[int] = mapped_column(sa.Integer, index=True)
    thread_metadata: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    object: Mapped[Text] = mapped_column(sa.String)
    tool_resources: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)

    @classmethod
    def from_openai(cls, thread: "OpenaiThread") -> "Thread":
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
        tool_resources: Optional[ToolResources] = None,
        **kwargs,
    ):
        if metadata is not None:
            self.thread_metadata = metadata
        if tool_resources is not None:
            self.tool_resources = model_dump(tool_resources)


class Message(Base):
    __tablename__ = "messages"

    db_id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    id: Mapped[Text] = mapped_column(sa.String, index=True)
    assistant_id: Mapped[Text] = mapped_column(sa.String, nullable=True)
    attachments: Mapped[List[Dict]] = mapped_column(sa.JSON, nullable=True)
    completed_at: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    content: Mapped[List[Dict]] = mapped_column(sa.JSON)
    created_at: Mapped[int] = mapped_column(sa.Integer, index=True)
    incomplete_at: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    incomplete_details: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    message_metadata: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    object: Mapped[Text] = mapped_column(sa.String)  # "thread.message"
    role: Mapped[Text] = mapped_column(sa.String)
    run_id: Mapped[Text] = mapped_column(sa.String, nullable=True)
    status: Mapped[Text] = mapped_column(sa.String, nullable=True)
    thread_id: Mapped[Text] = mapped_column(sa.String, index=True)

    @classmethod
    def from_openai(cls, message: "OpenaiMessage") -> "Message":
        return cls(
            id=message.id,
            assistant_id=message.assistant_id,
            attachments=model_dump(message.attachments),
            completed_at=message.completed_at,
            content=model_dump(message.content),
            created_at=message.created_at,
            incomplete_at=message.incomplete_at,
            incomplete_details=model_dump(message.incomplete_details),
            message_metadata=model_dump(message.metadata),
            object=message.object,
            role=message.role,
            run_id=message.run_id,
            status=message.status,
            thread_id=message.thread_id,
        )

    @classmethod
    def from_openai_create_params(cls, message: OpenaiMessage) -> "Message":
        return cls(
            id=message.id,
            content=model_dump(message.content),
            role=message.role,
            created_at=message.created_at,
            object=message.object,
            attachments=model_dump(message.attachments or []),
            message_metadata=model_dump(message.metadata or {}),
        )

    def to_openai(self) -> "OpenaiMessage":
        return OpenaiMessage.model_validate(
            {
                "id": self.id,
                "assistant_id": self.assistant_id,
                "attachments": model_dump(self.attachments),
                "completed_at": self.completed_at,
                "content": model_dump(self.content),
                "created_at": self.created_at,
                "incomplete_at": self.incomplete_at,
                "incomplete_details": model_dump(self.incomplete_details),
                "metadata": model_dump(self.message_metadata),
                "object": self.object,
                "role": self.role,
                "run_id": self.run_id,
                "status": self.status,
                "thread_id": self.thread_id,
            }
        )


class Run(Base):
    __tablename__ = "runs"

    db_id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    id: Mapped[Text] = mapped_column(sa.String, index=True)
    assistant_id: Mapped[Text] = mapped_column(sa.String, index=True)
    cancelled_at: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    completed_at: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    created_at: Mapped[int] = mapped_column(sa.Integer, index=True)
    expires_at: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    failed_at: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    incomplete_details: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    instructions: Mapped[Text] = mapped_column(sa.String)
    last_error: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    max_completion_tokens: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    max_prompt_tokens: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    run_metadata: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    model: Mapped[Text] = mapped_column(sa.String)
    object: Mapped[Text] = mapped_column(sa.String)
    parallel_tool_calls: Mapped[bool] = mapped_column(sa.Boolean)
    required_action: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    response_format: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    started_at: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    status: Mapped[Text] = mapped_column(sa.String)
    thread_id: Mapped[Text] = mapped_column(sa.String, index=True)
    tool_choice: Mapped[Text] = mapped_column(sa.JSON, nullable=True)
    tools: Mapped[List[Dict]] = mapped_column(sa.JSON)
    truncation_strategy: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    usage: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    temperature: Mapped[float] = mapped_column(sa.Float, nullable=True)
    top_p: Mapped[float] = mapped_column(sa.Float, nullable=True)

    @classmethod
    def from_openai(cls, message: "OpenaiRun") -> "Run":
        return cls(
            id=message.id,
            assistant_id=message.assistant_id,
            cancelled_at=message.cancelled_at,
            completed_at=message.completed_at,
            created_at=message.created_at,
            expires_at=message.expires_at,
            failed_at=message.failed_at,
            incomplete_details=model_dump(message.incomplete_details),
            instructions=message.instructions,
            last_error=model_dump(message.last_error),
            max_completion_tokens=message.max_completion_tokens,
            max_prompt_tokens=message.max_prompt_tokens,
            run_metadata=model_dump(message.metadata),
            model=message.model,
            object=message.object,
            parallel_tool_calls=message.parallel_tool_calls,
            required_action=model_dump(message.required_action),
            response_format=model_dump(message.response_format),
            started_at=message.started_at,
            status=message.status,
            thread_id=message.thread_id,
            tool_choice=(
                message.tool_choice
                if isinstance(message.tool_choice, Text)
                else model_dump(message.tool_choice)
            ),
            tools=model_dump(message.tools),
            truncation_strategy=model_dump(message.truncation_strategy),
            usage=model_dump(message.usage),
            temperature=message.temperature,
            top_p=message.top_p,
        )

    def to_openai(self) -> "OpenaiRun":
        return OpenaiRun.model_validate(
            {
                "id": self.id,
                "assistant_id": self.assistant_id,
                "cancelled_at": self.cancelled_at,
                "completed_at": self.completed_at,
                "created_at": self.created_at,
                "expires_at": self.expires_at,
                "failed_at": self.failed_at,
                "incomplete_details": model_dump(self.incomplete_details),
                "instructions": self.instructions,
                "last_error": model_dump(self.last_error),
                "max_completion_tokens": self.max_completion_tokens,
                "max_prompt_tokens": self.max_prompt_tokens,
                "metadata": model_dump(self.run_metadata),
                "model": self.model,
                "object": self.object,
                "parallel_tool_calls": self.parallel_tool_calls,
                "required_action": model_dump(self.required_action),
                "response_format": model_dump(self.response_format),
                "started_at": self.started_at,
                "status": self.status,
                "thread_id": self.thread_id,
                "tool_choice": (
                    self.tool_choice
                    if isinstance(self.tool_choice, Text)
                    else model_dump(self.tool_choice)
                ),
                "tools": model_dump(self.tools),
                "truncation_strategy": model_dump(self.truncation_strategy),
                "usage": model_dump(self.usage),
                "temperature": self.temperature,
                "top_p": self.top_p,
            }
        )


__all__ = ["Assistant", "Thread", "Message", "Run"]
