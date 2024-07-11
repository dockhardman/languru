from typing import TYPE_CHECKING, List, Literal, Optional, Text, Type

import sqlalchemy.exc
from openai.types.beta.threads.message import Message

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

    def retrieve(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass
