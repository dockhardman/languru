import json
import time
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Text, Type, Union

import duckdb

import languru.exceptions
from languru.config import console
from languru.exceptions import NotFound, NotSupported
from languru.types.openai_page import OpenaiPage
from languru.utils.sql import (
    CREATE_EMBEDDING_INDEX_LINE,
    DISPLAY_SQL_PARAMS,
    DISPLAY_SQL_QUERY,
    openapi_to_create_table_sql,
)

if TYPE_CHECKING:
    import pandas as pd

    from languru.documents.document import Document, Point


class PointQuerySet:
    def __init__(
        self,
        model: Type["Point"],
        *args,
        **kwargs,
    ):
        self.model = model
        self.__args = args
        self.__kwargs = kwargs

    def touch(self, *, conn: "duckdb.DuckDBPyConnection", debug: bool = False) -> bool:
        time_start = time.perf_counter() if debug else None

        # Install VSS extension
        conn.sql("INSTALL vss;")
        conn.sql("LOAD vss;")

        # Create table
        create_table_sql = openapi_to_create_table_sql(
            self.model.model_json_schema(),
            table_name=self.model.TABLE_NAME,
            primary_key="point_id",
            indexes=["document_id", "content_md5"],
        ).strip()
        create_table_sql = (
            create_table_sql
            + "\n"
            + CREATE_EMBEDDING_INDEX_LINE.format(
                table_name=self.model.TABLE_NAME,
                column_name="embedding",
                metric="cosine",
            )
        ).strip()

        if debug:
            console.print(
                f"\nCreating table: '{self.model.TABLE_NAME}' with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=create_table_sql)}\n"
            )
            # CREATE TABLE points (
            #     point_id TEXT,
            #     document_id TEXT NOT NULL,
            #     content_md5 TEXT NOT NULL,
            #     embedding FLOAT[512],
            #     PRIMARY KEY (point_id)
            # );
            # CREATE INDEX idx_points_embedding ON points USING HNSW(embedding) WITH (metric = 'cosine');  # noqa: E501

        conn.sql(create_table_sql)

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(
                f"Created table: '{self.model.TABLE_NAME}' in {time_elapsed:.6f} ms"
            )
        return True

    def retrieve(
        self,
        point_id: Text,
        *,
        conn: "duckdb.DuckDBPyConnection",
        debug: bool = False,
        with_embedding: bool = False,
    ) -> "Point":
        time_start = time.perf_counter() if debug else None

        # Get columns
        columns = list(self.model.model_json_schema()["properties"].keys())
        if not with_embedding:
            columns = [c for c in columns if c != "embedding"]
        columns_expr = ",".join(columns)

        query = f"SELECT {columns_expr} FROM {self.model.TABLE_NAME} WHERE point_id = ?"
        parameters = [point_id]
        if debug:
            console.print(
                f"\nRetrieving point: '{point_id}' with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )

        result = conn.execute(query, parameters).fetchone()

        if result is None:
            raise NotFound(f"Point with ID '{point_id}' not found.")

        data = dict(zip([c for c in columns], result))
        out = self.model.model_validate(data)

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(f"Retrieved point: '{point_id}' in {time_elapsed:.6f} ms")
        return out

    def create(
        self,
        point: Union["Point", Dict],
        *,
        conn: "duckdb.DuckDBPyConnection",
        debug: bool = False,
    ) -> "Point":
        point = self.model.model_validate(point) if isinstance(point, dict) else point
        if point.is_embedded is False:
            raise ValueError("Point is not embedded, please embed it first.")

        time_start = time.perf_counter() if debug else None

        # Get columns
        columns = list(point.model_json_schema()["properties"].keys())
        columns_expr = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])
        parameters = [getattr(point, c) for c in columns]

        query = (
            f"INSERT INTO {self.model.TABLE_NAME} ({columns_expr}) "
            + f"VALUES ({placeholders})"
        )
        if debug:
            console.print(
                f"\nCreating point: '{point.point_id}' with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )

        conn.execute(query, parameters)

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(f"Created point: '{point.point_id}' in {time_elapsed:.6f} ms")
        return point

    def update(self, *args, **kwargs):
        raise NotSupported("Updating points is not supported.")

    def remove(
        self,
        point_id: Text,
        *,
        conn: "duckdb.DuckDBPyConnection",
        debug: bool = False,
    ) -> None:
        time_start = time.perf_counter() if debug else None

        query = f"DELETE FROM {self.model.TABLE_NAME} WHERE point_id = ?"
        parameters = [point_id]
        if debug:
            console.print(
                f"\nDeleting point: '{point_id}' with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )

        conn.execute(query, parameters)

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(f"Deleted point: '{point_id}' in {time_elapsed:.6f} ms")
        return None

    def list(
        self,
        *,
        document_id: Optional[Text] = None,
        content_md5: Optional[Text] = None,
        after: Optional[Text] = None,
        before: Optional[Text] = None,
        limit: int = 20,
        order: Literal["asc", "desc"] = "asc",
        conn: "duckdb.DuckDBPyConnection",
        with_embedding: bool = False,
        debug: bool = False,
    ) -> OpenaiPage["Point"]:
        time_start = time.perf_counter() if debug else None

        columns = list(self.model.model_json_schema()["properties"].keys())
        if not with_embedding:
            columns = [c for c in columns if c != "embedding"]
        columns_expr = ",".join(columns)

        query = f"SELECT {columns_expr} FROM {self.model.TABLE_NAME}\n"
        where_clauses: List[Text] = []
        parameters: List[Text] = []

        if document_id is not None:
            where_clauses.append("document_id = ?")
            parameters.append(document_id)
        if content_md5 is not None:
            where_clauses.append("content_md5 = ?")
            parameters.append(content_md5)

        if after is not None and order == "asc":
            where_clauses.append("point_id > ?")
            parameters.append(after)
        elif before is not None and order == "desc":
            where_clauses.append("point_id < ?")
            parameters.append(before)

        if where_clauses:
            query += "WHERE " + " AND ".join(where_clauses) + "\n"

        query += f"ORDER BY point_id {order.upper()}\n"

        fetch_limit = limit + 1
        query += f"LIMIT {fetch_limit}"

        if debug:
            console.print(
                "\nListing points with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )

        results_df: "pd.DataFrame" = (
            conn.execute(query, parameters).fetch_arrow_table().to_pandas()
        )
        results: List[Dict] = results_df.to_dict(orient="records")

        points = [self.model.model_validate(row) for row in results[:limit]]

        out = OpenaiPage(
            data=points,
            object="list",
            first_id=points[0].point_id if points else None,
            last_id=points[-1].point_id if points else None,
            has_more=len(results) > limit,
        )

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(f"Listed points in {time_elapsed:.6f} ms")
        return out

    def count(
        self,
        *,
        document_id: Optional[Text] = None,
        content_md5: Optional[Text] = None,
        conn: "duckdb.DuckDBPyConnection",
        debug: bool = False,
    ) -> int:
        time_start = time.perf_counter() if debug else None

        query = f"SELECT COUNT(*) FROM {self.model.TABLE_NAME}\n"
        where_clauses: List[Text] = []
        parameters: List[Text] = []

        if document_id is not None:
            where_clauses.append("document_id = ?")
            parameters.append(document_id)
        if content_md5 is not None:
            where_clauses.append("content_md5 = ?")
            parameters.append(content_md5)

        if where_clauses:
            query += "WHERE " + " AND ".join(where_clauses) + "\n"

        if debug:
            console.print(
                "\nCounting points with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )

        result = conn.execute(query, parameters).fetchone()
        count = result[0] if result else 0

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(f"Counted points in {time_elapsed:.6f} ms")
        return count


class DocumentQuerySet:
    def __init__(self, model: Type["Document"], *args, **kwargs):
        self.model = model
        self.__args = args
        self.__kwargs = kwargs

    def touch(
        self,
        *,
        conn: "duckdb.DuckDBPyConnection",
        touch_point: bool = True,
        debug: bool = False,
    ) -> bool:
        time_start = time.perf_counter() if debug else None

        # Install JSON extension
        conn.execute("INSTALL json;")
        conn.execute("LOAD json;")

        # Create table
        create_table_sql = openapi_to_create_table_sql(
            self.model.model_json_schema(),
            table_name=self.model.TABLE_NAME,
            primary_key="document_id",
            unique_fields=[],
            # unique_fields=["name"],  # Index limitations (https://duckdb.org/docs/sql/indexes)  # noqa: E501
            indexes=["content_md5"],
        )
        if debug:
            console.print(
                f"\nCreating table: '{self.model.TABLE_NAME}' with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=create_table_sql)}\n"
            )
            # CREATE TABLE documents (
            #     document_id TEXT,
            #     name VARCHAR(255) NOT NULL UNIQUE,
            #     content VARCHAR(5000) NOT NULL,
            #     content_md5 TEXT NOT NULL,
            #     metadata JSON,
            #     created_at INT,
            #     updated_at INT,
            #     PRIMARY KEY (document_id)
            # );
            # CREATE INDEX idx_documents_content_md5 ON documents (content_md5);

        conn.sql(create_table_sql)

        if touch_point:
            self.model.POINT_TYPE.objects.touch(conn=conn, debug=debug)

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(
                f"Created table: '{self.model.TABLE_NAME}' in {time_elapsed:.6f} ms"
            )
        return True

    def retrieve(
        self,
        document_id: Text,
        *,
        conn: "duckdb.DuckDBPyConnection",
        with_embedding: bool = False,
        debug: bool = False,
    ) -> Optional["Document"]:
        time_start = time.perf_counter() if debug else None

        columns = list(self.model.model_json_schema()["properties"].keys())
        if not with_embedding:
            columns = [c for c in columns if c != "embedding"]
        columns_expr = ",".join(columns)

        query = (
            f"SELECT {columns_expr} FROM {self.model.TABLE_NAME} WHERE document_id = ?"
        )
        parameters = [document_id]
        if debug:
            console.print(
                f"\nRetrieving document: '{document_id}' with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )

        result = conn.execute(query, parameters).fetchone()

        if result is None:
            raise NotFound(f"Document with ID '{document_id}' not found.")

        data = dict(zip(columns, result))
        data["metadata"] = json.loads(data["metadata"])
        out = self.model.model_validate(data)

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(
                f"Retrieved document: '{document_id}' in {time_elapsed:.6f} ms"
            )
        return out

    def create(
        self,
        document: Union["Document", Dict],
        *,
        conn: "duckdb.DuckDBPyConnection",
        debug: bool = False,
    ) -> "Document":
        time_start = time.perf_counter() if debug else None

        document = (
            self.model.model_validate(document)
            if isinstance(document, dict)
            else document
        )
        document.strip()

        columns = list(document.model_json_schema()["properties"].keys())
        columns_expr = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])
        parameters = [getattr(document, c) for c in columns]

        query = (
            f"INSERT INTO {self.model.TABLE_NAME} ({columns_expr}) "
            + f"VALUES ({placeholders})"
        )
        if debug:
            console.print(
                f"\nCreating document: '{document.document_id}' with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )
        conn.execute(
            query,
            parameters,
        )

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(
                f"Created document: '{document.document_id}' in {time_elapsed:.6f} ms"
            )
        return document

    def update(
        self,
        document_id: Text,
        *,
        name: Optional[Text] = None,
        content: Optional[Text] = None,
        metadata: Optional[Dict] = None,
        conn: "duckdb.DuckDBPyConnection",
        debug: bool = False,
    ) -> "Document":
        if not any([name, content, metadata]):
            raise ValueError("At least one of the parameters must be provided.")

        time_start = time.perf_counter() if debug else None

        # Check if the new name already exists
        if name is not None:
            existing_doc = conn.execute(
                "SELECT document_id FROM documents WHERE name = ? AND document_id != ?",
                [name, document_id],
            ).fetchone()
            if existing_doc:
                raise ValueError(
                    f"The name '{name}' is already used by another document."
                )

        document = self.retrieve(document_id, conn=conn)
        if document is None:
            raise languru.exceptions.NotFound(
                f"Document with ID '{document_id}' not found."
            )

        set_query: List[Text] = []
        parameters = []
        if name is not None:
            document.name = name
            set_query.append("name = ?")
            parameters.append(document.name)
        if content is not None:
            document.content = content
            document.strip()
            set_query.append("content = ?")
            parameters.append(document.content)
        if metadata is not None:
            document.metadata.update(metadata)
            set_query.append("metadata = json_merge_patch(metadata, ?::JSON)")
            parameters.append(json.dumps(metadata))
        document.updated_at = int(time.time())
        set_query.append("updated_at = ?")
        parameters.append(document.updated_at)

        set_query_expr = ",\n    ".join(set_query)
        parameters.append(document_id)
        query = f"UPDATE {self.model.TABLE_NAME}\n"
        query += f"SET {set_query_expr}\n"
        query += "WHERE document_id = ?"
        if debug:
            console.print(
                f"\nUpdating document: '{document_id}' with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )

        conn.execute(query, parameters)

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(f"Updated document: '{document_id}' in {time_elapsed:.6f} ms")
        return document

    def remove(
        self,
        document_id: Text,
        *,
        conn: "duckdb.DuckDBPyConnection",
        debug: bool = False,
    ) -> None:
        time_start = time.perf_counter() if debug else None

        query = f"DELETE FROM {self.model.TABLE_NAME} WHERE document_id = ?"
        parameters = [document_id]
        if debug:
            console.print(
                f"\nDeleting document: '{document_id}' with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )

        conn.execute(query, parameters)

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(f"Deleted document: '{document_id}' in {time_elapsed:.6f} ms")
        return None

    def list(
        self,
        *,
        after: Optional[Text] = None,
        before: Optional[Text] = None,
        limit: int = 20,
        order: Literal["asc", "desc"] = "asc",
        conn: "duckdb.DuckDBPyConnection",
        debug: bool = False,
    ) -> OpenaiPage["Document"]:
        time_start = time.perf_counter() if debug else None

        columns = list(self.model.model_json_schema()["properties"].keys())
        columns_expr = ",".join(columns)

        query = f"SELECT {columns_expr} FROM {self.model.TABLE_NAME}\n"
        where_clauses: List[Text] = []
        parameters: List[Text] = []

        if after is not None and order == "asc":
            where_clauses.append("document_id > ?")
            parameters.append(after)
        elif before is not None and order == "desc":
            where_clauses.append("document_id < ?")
            parameters.append(before)

        if where_clauses:
            query += "WHERE " + " AND ".join(where_clauses) + "\n"

        query += f"ORDER BY document_id {order.upper()}\n"

        # Fetch one more than the limit to determine if there are more results
        fetch_limit = limit + 1
        query += f"LIMIT {fetch_limit}"

        if debug:
            console.print(
                "\nListing documents with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )

        results_df: "pd.DataFrame" = (
            conn.execute(query, parameters).fetch_arrow_table().to_pandas()
        )
        results_df["metadata"] = results_df["metadata"].apply(json.loads)
        results: List[Dict] = results_df.to_dict(orient="records")

        documents = [self.model.model_validate(row) for row in results[:limit]]

        out = OpenaiPage(
            data=documents,
            object="list",
            first_id=documents[0].document_id if documents else None,
            last_id=documents[-1].document_id if documents else None,
            has_more=len(results) > limit,
        )

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(f"Listed documents in {time_elapsed:.6f} ms")
        return out

    def count(
        self,
        *,
        document_id: Optional[Text] = None,
        content_md5: Optional[Text] = None,
        conn: "duckdb.DuckDBPyConnection",
        debug: bool = False,
    ) -> int:
        time_start = time.perf_counter() if debug else None

        query = f"SELECT COUNT(*) FROM {self.model.TABLE_NAME}\n"
        where_clauses: List[Text] = []
        parameters: List[Text] = []

        if document_id is not None:
            where_clauses.append("document_id = ?")
            parameters.append(document_id)
        if content_md5 is not None:
            where_clauses.append("content_md5 = ?")
            parameters.append(content_md5)

        if where_clauses:
            query += "WHERE " + " AND ".join(where_clauses) + "\n"

        if debug:
            console.print(
                "\nCounting documents with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )

        result = conn.execute(query, parameters).fetchone()
        count = result[0] if result else 0

        if time_start is not None:
            time_end = time.perf_counter()
            time_elapsed = (time_end - time_start) * 1000
            console.print(f"Counted documents in {time_elapsed:.6f} ms")
        return count


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
