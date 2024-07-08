import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AssistantOrm(Base):
    __tablename__ = "assistants"

    db_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id = sa.Column(sa.String, index=True)
    created_at = sa.Column(sa.Integer, index=True)
    description = sa.Column(sa.String, nullable=True)
    instructions = sa.Column(sa.String, nullable=True)
    metadata = sa.Column(sa.JSON, nullable=True)
    model = sa.Column(sa.String)
    name = sa.Column(sa.String, nullable=True)
    object = sa.Column(sa.String, nullable=True)
    tools = sa.Column(sa.JSON, nullable=True)
    response_format = sa.Column(sa.JSON, nullable=True)
    temperature = sa.Column(sa.Float, nullable=True)
    tool_resources = sa.Column(sa.JSON, nullable=True)
    top_p = sa.Column(sa.Float, nullable=True)


__all__ = ["AssistantOrm"]
