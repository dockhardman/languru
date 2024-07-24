from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Text, Type

import sqlalchemy.exc
from openai.types.beta.assistant_tool_choice_option import AssistantToolChoiceOption
from openai.types.beta.threads.run import Run
from openai.types.beta.threads.run_status import RunStatus

from languru.exceptions import NotFound
from languru.types.sql._openai import Run as OrmRun
from languru.utils.common import model_dump

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
        self,
        run_id: Text,
        *,
        thread_id: Text,
        metadata: Optional[Dict] = None,
        cancelled_at: Optional[int] = None,
        completed_at: Optional[int] = None,
        expires_at: Optional[int] = None,
        failed_at: Optional[int] = None,
        incomplete_details: Optional[Dict] = None,
        required_action: Optional[Dict] = None,
        status: Optional[RunStatus] = None,
        tool_choice: Optional[AssistantToolChoiceOption] = None,
        tools: Optional[List[Dict]] = None,
        truncation_strategy: Optional[Dict] = None,
        usage: Optional[Dict] = None,
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
            if cancelled_at is not None:
                run.cancelled_at = cancelled_at
            if completed_at is not None:
                run.completed_at = completed_at
            if expires_at is not None:
                run.expires_at = expires_at
            if failed_at is not None:
                run.failed_at = failed_at
            if incomplete_details is not None:
                run.incomplete_details = model_dump(incomplete_details)
            if required_action is not None:
                run.required_action = model_dump(required_action)
            if status is not None:
                run.status = status
            if tool_choice is not None:
                run.tool_choice
            if tools is not None:
                run.tools = model_dump(tools)
            if truncation_strategy is not None:
                run.truncation_strategy = model_dump(truncation_strategy)
            if usage is not None:
                run.usage = model_dump(usage)

            session.commit()
            session.refresh(run)
            return run.to_openai()

    def delete(
        self, run_id: Text, *, thread_id: Text, not_exist_ok: bool = False
    ) -> Dict:
        with self._client.sql_session() as session:
            run = (
                session.query(self.orm_model)
                .filter(
                    self.orm_model.id == run_id, self.orm_model.thread_id == thread_id
                )
                .first()
            )
            if run is None:
                if not_exist_ok:
                    return {
                        "id": run_id,
                        "deleted": False,
                        "object": "thread.run.deleted",
                    }

                raise NotFound(f"Run {run_id} not found")

            session.delete(run)
            session.commit()
            return {
                "id": run_id,
                "deleted": True,
                "object": "thread.run.deleted",
            }
