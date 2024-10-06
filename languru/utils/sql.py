from typing import Dict, List, Optional, Text

COLUMN_DECLARATION_LINE = "{field_name} {sql_type} {not_null} {unique}"
DECLARATION_INDENT = "    "
CREATE_INDEX_LINE = (
    "CREATE INDEX idx_{table_name}_{column_name} ON {table_name} ({column_name});"
)

# Mapping for types, adding JSON type
json_to_sql_type_map = {
    "string": "TEXT",  # Default fallback for strings without max_length
    "text": "TEXT",  # We'll override for specific VARCHAR needs
    "integer": "INT",
    "boolean": "BOOLEAN",
    "number": "FLOAT",
    "object": "JSON",  # JSON type for metadata or other object fields
}


# Function to generate SQL CREATE TABLE statement with JSON support
def openapi_to_create_table_sql(
    schema: Dict,
    table_name: Text,
    primary_key: Optional[Text] = None,
    unique_fields: Optional[List[Text]] = None,
) -> Text:
    unique_fields = unique_fields or []
    columns = []
    for field_name, field_info in schema["properties"].items():
        field_type = field_info.get("type")

        # Special handling for VARCHAR if maxLength is specified
        max_length = field_info.get("maxLength")
        if max_length and field_type == "string":
            sql_type = f"VARCHAR({max_length})"
        elif field_type == "object":  # Handle JSON fields
            sql_type = "JSON"
        else:
            sql_type = json_to_sql_type_map.get(field_type, "TEXT")

        not_null = "NOT NULL" if field_name in schema.get("required", []) else ""
        unique = "UNIQUE" if field_name in unique_fields else ""
        columns.append(
            COLUMN_DECLARATION_LINE.format(
                field_name=field_name,
                sql_type=sql_type,
                not_null=not_null,
                unique=unique,
            ).strip()
        )

    # Add primary key
    if primary_key:
        columns.append(f"PRIMARY KEY ({primary_key})")

    columns_sql = f",\n{DECLARATION_INDENT}".join(columns)
    create_table_sql = (
        f"CREATE TABLE {table_name} (\n{DECLARATION_INDENT}{columns_sql}\n);"
    )
    return create_table_sql
