from typing import TYPE_CHECKING, Type

import duckdb

if TYPE_CHECKING:
    from languru.documents.document import Document, Point


class PointQuerySet:
    def __init__(self, model: Type["Point"], *args, **kwargs):
        self.model = model
        self.__args = args
        self.__kwargs = kwargs

    def touch(self) -> bool:
        pass


class DocumentQuerySet:
    def __init__(self, model: Type["Document"], *args, **kwargs):
        self.model = model
        self.__args = args
        self.__kwargs = kwargs

    def touch(self) -> bool:
        pass
