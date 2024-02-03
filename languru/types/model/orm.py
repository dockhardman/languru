import sqlalchemy as sa
from openai.types import Model
from sqlalchemy.orm import declarative_base

tb_name = "models"

Base = declarative_base()


class ModelOrm(Base):
    __tablename__ = tb_name

    id = sa.Column(sa.String, primary_key=True)
    created = sa.Column(sa.Integer)
    object = sa.Column(sa.String, default="model")
    owned_by = sa.Column(sa.String)


__all__ = ["Model", "ModelOrm"]
