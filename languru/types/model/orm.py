import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

tb_name = "models"

Base = declarative_base()


class ModelOrm(Base):
    __tablename__ = tb_name

    db_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id = sa.Column(sa.String, index=True)
    created = sa.Column(sa.Integer, index=True)
    object = sa.Column(sa.String, default="model")
    owned_by = sa.Column(sa.String, index=True)


__all__ = ["ModelOrm"]
