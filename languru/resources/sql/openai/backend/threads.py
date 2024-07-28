from typing import TYPE_CHECKING, Dict, Iterable, List, Literal, Optional, Text, Type

import sqlalchemy.exc
from openai.types.beta import thread_create_params
from openai.types.beta.thread import Thread
from openai.types.beta.thread_deleted import ThreadDeleted

from languru.exceptions import NotFound
from languru.resources.sql.openai.backend.messages import Messages as MessagesBackend
from languru.resources.sql.openai.backend.runs import Runs as RunsBackend
from languru.types.sql._openai import Message as OrmMessage
from languru.types.sql._openai import Thread as OrmThread
from languru.utils.openai_utils import rand_message_id

if TYPE_CHECKING:
    from languru.resources.sql.openai.backend._client import OpenaiBackend


class Threads:
    messages: MessagesBackend
    runs: RunsBackend

    def __init__(
        self,
        client: "OpenaiBackend",
        *,
        orm_model: Type["OrmThread"] = OrmThread,
        **kwargs,
    ):
        self._client = client
        self.orm_model = orm_model

        self.messages = MessagesBackend(client=self._client)
        self.runs = RunsBackend(client=self._client)

    def list(
        self,
        *,
        after: Optional[Text] = None,
        before: Optional[Text] = None,
        limit: Optional[int] = None,
        order: Optional[Literal["asc", "desc"]] = None,
    ) -> List["Thread"]:
        with self._client.sql_session() as session:
            query = session.query(self.orm_model)

            # Apply sorting
            if order == "desc":
                query = query.order_by(self.orm_model.created_at.desc())
            else:
                query = query.order_by(self.orm_model.created_at.asc())

            # Apply pagination using after
            if after is not None:
                try:
                    after_instance = (
                        session.query(self.orm_model)
                        .filter(self.orm_model.id == after)
                        .one()
                    )
                    if order == "asc":
                        query = query.filter(
                            self.orm_model.created_at > after_instance.created_at
                        )
                    else:
                        query = query.filter(
                            self.orm_model.created_at < after_instance.created_at
                        )
                except sqlalchemy.exc.NoResultFound:
                    raise NotFound(f"Thread {after} not found")

            # Apply pagination using before
            if before is not None:
                try:
                    before_instance = (
                        session.query(self.orm_model)
                        .filter(self.orm_model.id == before)
                        .one()
                    )
                    if order == "asc":
                        query = query.filter(
                            self.orm_model.created_at < before_instance.created_at
                        )
                    else:
                        query = query.filter(
                            self.orm_model.created_at > before_instance.created_at
                        )
                except sqlalchemy.exc.NoResultFound:
                    raise NotFound(f"Thread {before} not found")

            # Apply limit
            if limit is not None:
                query = query.limit(limit)

            return [thread.to_openai() for thread in query.all()]

    def create(
        self,
        thread: "Thread",
        messages: Optional[Iterable["thread_create_params.Message"]] = None,
    ) -> "Thread":
        with self._client.sql_session() as session:
            orm_thread = OrmThread.from_openai(thread)
            session.add(orm_thread)
            for message in messages or []:
                orm_message = OrmMessage.from_openai_create_params(
                    rand_message_id(), message=message
                )
                session.add(orm_message)
            session.commit()

            session.refresh(orm_thread)
            return orm_thread.to_openai()

    def retrieve(self, thread_id: Text) -> "Thread":
        with self._client.sql_session() as session:
            thread = (
                session.query(self.orm_model)
                .filter(self.orm_model.id == thread_id)
                .first()
            )
            if thread is None:
                raise NotFound(f"Thread {thread_id} not found")
            return thread.to_openai()

    def update(
        self,
        thread_id: Text,
        *,
        metadata: Optional[Dict] = None,
        tool_resources: Optional[thread_create_params.ToolResources] = None,
    ) -> "Thread":
        with self._client.sql_session() as session:
            thread = (
                session.query(self.orm_model)
                .filter(self.orm_model.id == thread_id)
                .first()
            )
            if thread is None:
                raise NotFound(f"Thread {thread_id} not found")
            thread.update(
                metadata=metadata,
                tool_resources=tool_resources,
            )
            session.commit()
            session.refresh(thread)
            return thread.to_openai()

    def delete(self, thread_id: Text, *, not_exist_ok: bool = False) -> "ThreadDeleted":
        with self._client.sql_session() as session:
            thread = (
                session.query(self.orm_model)
                .filter(self.orm_model.id == thread_id)
                .first()
            )
            if thread is None:
                if not_exist_ok:
                    return ThreadDeleted.model_validate(
                        {
                            "id": thread_id,
                            "deleted": False,
                            "object": "thread.deleted",
                        }
                    )
                raise NotFound(f"Thread {thread_id} not found")

            session.delete(thread)
            session.commit()
            return ThreadDeleted.model_validate(
                {"id": thread_id, "deleted": True, "object": "thread.deleted"}
            )
