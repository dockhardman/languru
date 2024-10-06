from typing import TYPE_CHECKING, Type

import duckdb

from languru.config import console
from languru.utils.sql import openapi_to_create_table_sql

if TYPE_CHECKING:
    from languru.documents.document import Document, Point


class PointQuerySet:
    def __init__(self, model: Type["Point"], *args, **kwargs):
        self.model = model
        self.__args = args
        self.__kwargs = kwargs

    def touch(self, *, conn: "duckdb.DuckDBPyConnection", debug: bool = False) -> bool:
        create_table_sql = openapi_to_create_table_sql(
            Point.model_json_schema(),
            table_name=Point.TABLE_NAME,
            primary_key="point_id",
            indexes=["content_md5"],
        )
        if debug:
            console.print(
                f"Creating table: {Point.TABLE_NAME} with SQL:\n{create_table_sql}"
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
            Document.model_json_schema(),
            table_name=Document.TABLE_NAME,
            primary_key="document_id",
            unique_fields=["name"],
            indexes=["content_md5"],
        )
        if debug:
            console.print(
                f"Creating table: {Document.TABLE_NAME} with SQL:\n{create_table_sql}"
            )
        conn.sql(create_table_sql)

        self.model.POINT_TYPE.objects.touch(conn=conn)
        return True
