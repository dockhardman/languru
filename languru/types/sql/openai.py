from typing import Dict, Text

import sqlalchemy as sa
from openai.types.beta.assistant import Assistant as OpenaiAssistant
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
    metadata: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    model: Mapped[Text] = mapped_column(sa.String)
    name: Mapped[Text] = mapped_column(sa.String, nullable=True)
    object: Mapped[Text] = mapped_column(sa.String, nullable=True)
    tools: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    response_format: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    temperature: Mapped[float] = mapped_column(sa.Float, nullable=True)
    tool_resources: Mapped[Dict] = mapped_column(sa.JSON, nullable=True)
    top_p: Mapped[float] = mapped_column(sa.Float, nullable=True)

    def to_openai(self):
        return OpenaiAssistant.model_validate(
            {
                "id": self.id,
                "created_at": self.created_at,
                "description": self.description,
                "instructions": self.instructions,
                "metadata": self.metadata,
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


__all__ = ["Assistant"]
