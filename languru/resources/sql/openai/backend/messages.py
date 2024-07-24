from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Text, Type

import sqlalchemy.exc
from openai.types.beta.threads.message import Message
from openai.types.beta.threads.message_deleted import MessageDeleted

from languru.exceptions import NotFound
from languru.types.sql._openai import Message as OrmMessage

if TYPE_CHECKING:
    from languru.resources.sql.openai.backend._client import OpenaiBackend


class Messages:
    def __init__(
        self,
        client: "OpenaiBackend",
        *,
        orm_model: Type["OrmMessage"] = OrmMessage,
        **kwargs,
    ):
        self._client = client
        self.orm_model = orm_model

    def create(self, message: "Message") -> "Message":
        with self._client.sql_session() as session:
            orm_message = self.orm_model.from_openai(message)
            session.add(orm_message)
            session.commit()
            session.refresh(orm_message)
            return orm_message.to_openai()

    def list(
        self,
        thread_id: str,
        *,
        after: Optional[Text] = None,
        before: Optional[Text] = None,
        limit: Optional[int] = None,
        order: Optional[Literal["asc", "desc"]] = None,
        run_id: Optional[Text] = None,
    ) -> List["Message"]:
        with self._client.sql_session() as session:
            query = session.query(OrmMessage).filter(OrmMessage.thread_id == thread_id)

            # Apply sorting
            if order == "asc":
                query = query.order_by(OrmMessage.created_at.asc())
            else:
                query = query.order_by(OrmMessage.created_at.desc())

            # Apply filters
            if run_id is not None:
                query = query.filter(OrmMessage.run_id == run_id)

            # Apply pagination
            if after is not None:
                try:
                    after_message = (
                        session.query(OrmMessage)
                        .filter(OrmMessage.id == after)
                        .one_or_none()
                    )
                    if after_message:
                        if order == "asc":
                            query = query.filter(
                                OrmMessage.created_at > after_message.created_at
                            )
                        else:
                            query = query.filter(
                                OrmMessage.created_at < after_message.created_at
                            )
                except sqlalchemy.exc.NoResultFound:
                    raise NotFound(f"Message with ID {after} not found.")

            if before is not None:
                try:
                    before_message = (
                        session.query(OrmMessage)
                        .filter(OrmMessage.id == before)
                        .one_or_none()
                    )
                    if before_message:
                        if order == "asc":
                            query = query.filter(
                                OrmMessage.created_at < before_message.created_at
                            )
                        else:
                            query = query.filter(
                                OrmMessage.created_at > before_message.created_at
                            )
                except sqlalchemy.exc.NoResultFound:
                    raise NotFound(f"Message with ID {before} not found.")

            # Apply limit
            query = query.limit(limit)

            # Execute query and return results
            return [m.to_openai() for m in query.all()]

    def retrieve(self, message_id: Text, *, thread_id: Text) -> "Message":
        with self._client.sql_session() as session:
            message = (
                session.query(OrmMessage)
                .filter(OrmMessage.id == message_id, OrmMessage.thread_id == thread_id)
                .first()
            )
            if message is None:
                raise NotFound(f"Message {message_id} not found")
            return message.to_openai()

    def update(
        self, message_id: Text, *, thread_id: Text, metadata: Optional[Dict] = None
    ) -> "Message":
        with self._client.sql_session() as session:
            message = (
                session.query(OrmMessage)
                .filter(OrmMessage.id == message_id, OrmMessage.thread_id == thread_id)
                .first()
            )
            if message is None:
                raise NotFound(f"Message {message_id} not found")
            message.message_metadata = metadata or {}
            session.commit()
            session.refresh(message)
            return message.to_openai()

    def delete(
        self, message_id: Text, *, thread_id: Text, not_exist_ok: bool = False
    ) -> "MessageDeleted":
        with self._client.sql_session() as session:
            try:
                message = (
                    session.query(OrmMessage)
                    .filter(
                        OrmMessage.id == message_id, OrmMessage.thread_id == thread_id
                    )
                    .one()
                )
                session.delete(message)
                session.commit()
                return MessageDeleted.model_validate(
                    dict(id=message_id, deleted=True, object="thread.message.deleted")
                )
            except sqlalchemy.exc.NoResultFound:
                if not_exist_ok:
                    return MessageDeleted.model_validate(
                        dict(
                            id=message_id,
                            deleted=False,
                            object="thread.message.deleted",
                        )
                    )
                raise NotFound(f"Message {message_id} not found")
