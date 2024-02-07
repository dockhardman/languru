import time
from typing import Text

import sqlalchemy as sa
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from yarl import URL

from languru.config import logger
from languru.types.model import Model
from languru.types.model.orm import Base as SQL_Base
from languru.types.model.orm import ModelOrm


class ModelDiscovery:

    @classmethod
    def from_url(cls, url: Text | URL):
        url_str: Text = str(url).strip()
        if (
            url_str.startswith("sqlite")
            or url_str.startswith("postgresql")
            or url_str.startswith("postgres")
            or url_str.startswith("mysql")
        ):
            return SqlModelDiscovery(url)
        else:
            logger.error(f"Unsupported discovery url: {url_str}")
            raise ValueError(f"Unsupported discovery url: {url_str}")

    def touch(self) -> bool:
        raise NotImplementedError

    def register(self, model: Model) -> Model:
        raise NotImplementedError

    def retrieve(self, id: Text) -> Model:
        raise NotImplementedError


class SqlModelDiscovery(ModelDiscovery):
    def __init__(self, url: Text | URL):
        self.url: Text = str(url)
        connect_kwargs = {}
        if self.url.startswith("sqlite"):
            connect_kwargs["check_same_thread"] = False
        self._engine = sa.create_engine(self.url, connect_args=connect_kwargs)

    @property
    def sql_engine(self):
        return self._engine

    def touch(self) -> bool:
        return SQL_Base.metadata.create_all(self.sql_engine)

    def register(self, model: Model, created: int | None = None) -> Model:
        if not isinstance(model, Model):
            raise TypeError(f"Expected Model, got {type(model)}")
        if not model.id:
            raise ValueError("Model id is required")

        created = int(time.time()) if created is None else created
        with Session(self.sql_engine) as session:
            # update or create
            try:
                model_orm = (
                    session.query(ModelOrm)
                    .filter(
                        ModelOrm.id == model.id, ModelOrm.owned_by == model.owned_by
                    )
                    .one()
                )
                model_orm.created = created
            except NoResultFound:
                # create one
                model_orm = ModelOrm(
                    id=model.id,
                    created=created,
                    object=model.object,
                    owned_by=model.owned_by,
                )
                session.add(model_orm)
            session.commit()
            session.refresh(model_orm)

            return Model.model_validate(model_orm)

    def retrieve(self, id: Text) -> Model | None:
        with Session(self.sql_engine) as session:
            model_orm = session.query(ModelOrm).filter(ModelOrm.id == id).one_or_none()
            if model_orm is None:
                return None
            return Model.model_validate(model_orm)
