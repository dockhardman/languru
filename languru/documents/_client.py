from typing import TYPE_CHECKING, Type

import duckdb

from languru.config import console
from languru.utils.sql import CREATE_EMBEDDING_INDEX_LINE, openapi_to_create_table_sql

if TYPE_CHECKING:
    from languru.documents.document import Document, Point


class PointQuerySet:
    def __init__(self, model: Type["Point"], *args, **kwargs):
        self.model = model
        self.__args = args
        self.__kwargs = kwargs

    def touch(self, *, conn: "duckdb.DuckDBPyConnection", debug: bool = False) -> bool:
        create_table_sql = openapi_to_create_table_sql(
            self.model.model_json_schema(),
            table_name=self.model.TABLE_NAME,
            primary_key="point_id",
            indexes=["content_md5"],
        ).strip()
        create_table_sql = (
            create_table_sql
            + "\n"
            + CREATE_EMBEDDING_INDEX_LINE.format(
                table_name=self.model.TABLE_NAME, column_name="embedding"
            )
        ).strip()

        if debug:
            console.print(
                f"Creating table: '{self.model.TABLE_NAME}' with SQL:\n"
                + f"{create_table_sql}\n"
                + "=== End of SQL ===\n"
            )
        conn.sql(create_table_sql)
        return True


class DocumentQuerySet:
    def __init__(self, model: Type["Document"], *args, **kwargs):
        self.model = model
        self.__args = args
        self.__kwargs = kwargs

    def touch(self, *, conn: "duckdb.DuckDBPyConnection", debug: bool = False) -> bool:
        create_table_sql = openapi_to_create_table_sql(
            self.model.model_json_schema(),
            table_name=self.model.TABLE_NAME,
            primary_key="document_id",
            unique_fields=["name"],
            indexes=["content_md5"],
        )
        if debug:
            console.print(
                f"Creating table: '{self.model.TABLE_NAME}' with SQL:\n"
                + f"{create_table_sql}\n"
                + "=== End of SQL ===\n"
            )
        conn.sql(create_table_sql)

        self.model.POINT_TYPE.objects.touch(conn=conn, debug=debug)
        return True


class PointQuerySetDescriptor:
    def __get__(self, instance: None, owner: Type["Point"]) -> "PointQuerySet":
        if instance is not None:
            raise AttributeError(
                "PointQuerySetDescriptor cannot be accessed via an instance."
            )
        return PointQuerySet(owner)


class DocumentQuerySetDescriptor:
    def __get__(self, instance: None, owner: Type["Document"]) -> "DocumentQuerySet":
        if instance is not None:
            raise AttributeError(
                "DocumentQuerySetDescriptor cannot be accessed via an instance."
            )
        return DocumentQuerySet(owner)
