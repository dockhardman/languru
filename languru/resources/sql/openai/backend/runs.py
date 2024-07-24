from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Text, Type

import sqlalchemy.exc
from openai.types.beta.threads.run import Run

from languru.exceptions import NotFound
from languru.types.sql._openai import Run as OrmRun

if TYPE_CHECKING:
    from languru.resources.sql.openai.backend._client import OpenaiBackend


class Runs:
    def __init__(
        self,
        client: "OpenaiBackend",
        *,
        orm_model: Type["OrmRun"] = OrmRun,
        **kwargs,
    ):
        self._client = client
        self.orm_model = orm_model

    def create(self, run: "Run") -> "Run":
        with self._client.sql_session() as session:
            orm_run = self.orm_model.from_openai(run)
            session.add(orm_run)
            session.commit()
            session.refresh(orm_run)
            return orm_run.to_openai()

    def list(
        self,
        thread_id: Text,
        *,
        after: Optional[Text] = None,
        before: Optional[Text] = None,
        limit: Optional[int] = None,
        order: Optional[Literal["asc", "desc"]] = None,
        assistant_id: Optional[Text] = None,
    ) -> List["Run"]:
        with self._client.sql_session() as session:
            query = session.query(self.orm_model).filter(
                self.orm_model.thread_id == thread_id
            )

            # Apply sorting
            if order == "asc":
                query = query.order_by(self.orm_model.created_at.asc())
            else:
                query = query.order_by(self.orm_model.created_at.desc())

            # Apply filters
            if assistant_id is not None:
                query = query.filter(self.orm_model.assistant_id == assistant_id)

            # Apply pagination
            if after is not None:
                try:
                    after_run = (
                        session.query(self.orm_model)
                        .filter(self.orm_model.id == after)
                        .one_or_none()
                    )
                    if after_run:
                        if order == "asc":
                            query = query.filter(
                                self.orm_model.created_at > after_run.created_at
                            )
                        else:
                            query = query.filter(
                                self.orm_model.created_at < after_run.created_at
                            )
                except sqlalchemy.exc.NoResultFound:
                    raise NotFound(f"Run with ID {after} not found.")

            if before is not None:
                try:
                    before_run = (
                        session.query(self.orm_model)
                        .filter(self.orm_model.id == before)
                        .one_or_none()
                    )
                    if before_run:
                        if order == "asc":
                            query = query.filter(
                                self.orm_model.created_at < before_run.created_at
                            )
                        else:
                            query = query.filter(
                                self.orm_model.created_at > before_run.created_at
                            )
                except sqlalchemy.exc.NoResultFound:
                    raise NotFound(f"Run with ID {before} not found.")

            if limit is not None:
                query = query.limit(limit)

            return [run.to_openai() for run in query.all()]

    def retrieve(self, run_id: Text, *, thread_id: Text) -> "Run":
        with self._client.sql_session() as session:
            run = (
                session.query(self.orm_model)
                .filter(
                    self.orm_model.id == run_id, self.orm_model.thread_id == thread_id
                )
                .first()
            )
            if run is None:
                raise NotFound(f"Run {run_id} not found")
            return run.to_openai()

    def update(
        self, run_id: Text, *, thread_id: Text, metadata: Optional[Dict] = None
    ) -> "Run":
        with self._client.sql_session() as session:
            run = (
                session.query(self.orm_model)
                .filter(
                    self.orm_model.id == run_id, self.orm_model.thread_id == thread_id
                )
                .first()
            )
            if run is None:
                raise NotFound(f"Run {run_id} not found")
            run.run_metadata = metadata or {}
            session.commit()
            session.refresh(run)
            return run.to_openai()

    def delete(self):
        pass
