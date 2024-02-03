import time
from typing import Text

import sqlalchemy as sa
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from yarl import URL

from languru.types.model.orm import Model, ModelOrm


class ModelDiscorvery:
    def register(self, model: Model) -> Model:
        raise NotImplementedError

    def retrieve(self, id: Text) -> Model:
        raise NotImplementedError


class SqlModelDiscorvery(ModelDiscorvery):
    def __init__(self, url: Text | URL):
        self.url = URL(url)
        self._engine = sa.create_engine(str(self.url))

    @property
    def sql_engine(self):
        return self._engine

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
                    session.query(ModelOrm).filter(ModelOrm.id == model.id).one()
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
