from contextlib import contextmanager
from typing import Text, Type

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from yarl import URL

from languru.resources.sql.openai.backend.assistants import Assistants
from languru.types.sql._openai import Assistant as OrmAssistant
from languru.types.sql._openai import Base as SQL_Base


class OpenaiBackend:
    assistants: Assistants

    def __init__(
        self,
        url: Text | URL,
        *,
        sql_base: Type[DeclarativeBase] = SQL_Base,
        orm_assistant: Type[OrmAssistant] = OrmAssistant,
        **kwargs,
    ):
        self.url: Text = str(url)
        connect_kwargs = {}
        if self.url.startswith("sqlite"):
            connect_kwargs["check_same_thread"] = False

        self._engine = sa.create_engine(self.url, connect_args=connect_kwargs)
        self._session_factory = sessionmaker(bind=self._engine)
        self._sql_base = sql_base

        self.assistants = Assistants(client=self, orm_model=orm_assistant, **kwargs)

    @property
    def sql_engine(self) -> sa.Engine:
        return self._engine

    @contextmanager
    def sql_session(self):
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def touch(self):
        self._sql_base.metadata.create_all(self.sql_engine)
