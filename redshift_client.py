"""
Utilities for connecting to Redshift and running simple queries.

Provides `get_conn`, `fetch_schema`, and `run_count_query` helpers.
"""

import os
import redshift_connector
from typing import Any, Iterable, List, Tuple
from dotenv import load_dotenv
from psycopg2 import sql


if os.getenv("ENV") == "TEST":
    load_dotenv(".env.test")
else:
    load_dotenv()


def get_conn():
    """
    Return a DB connection to Redshift or a test Postgres instance.

    Uses `ENV=TEST` to decide whether to return a local `psycopg2` connection
    or a `redshift_connector` connection.

    Returns:
        Connection: DB connection object from `psycopg2` or `redshift_connector`.
    """

    if os.getenv("ENV") == "TEST":
        import psycopg2
        return psycopg2.connect(
            host=os.getenv("REDSHIFT_HOST"),
            port=int(os.getenv("REDSHIFT_PORT", "5439")),
            dbname=os.getenv("REDSHIFT_DATABASE"),
            user=os.getenv("REDSHIFT_USER"),
            password=os.getenv("REDSHIFT_PASSWORD")
        )

    return redshift_connector.connect(
        host=os.getenv("REDSHIFT_HOST"),
        port=int(os.getenv("REDSHIFT_PORT", "5439")),
        database=os.getenv("REDSHIFT_DATABASE"),
        user=os.getenv("REDSHIFT_USER"),
        password=os.getenv("REDSHIFT_PASSWORD")
    )


def fetch_schema(schema_name: str):
    """
    Fetch column metadata for all tables in a schema.

    Args:
        schema_name (str): Name of the schema to query.

    Returns:
        list[tuple]: Rows containing (table_name, column_name, data_type).
    """

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = '{schema_name}';
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


FilterSpec = Tuple[str, str]


def run_count_query(table_name: str, filters: Iterable[FilterSpec], params: List[Any]) -> int:
    """
    Run a parameterized COUNT(*) query with optional filters.

    Args:
        table_name (str): Table to count rows from (uses `DEFAULT_SCHEMA` env var).
        filters (Iterable[FilterSpec]): Sequence of (column, clause_type) tuples.
        params (list[Any]): Parameters for the query in the same order as filters.

    Returns:
        int: Row count result.
    """

    conn = get_conn()
    cursor = conn.cursor()
    schema = os.getenv("DEFAULT_SCHEMA", "public")

    base_query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
        sql.Identifier(schema),
        sql.Identifier(table_name),
    )

    filter_list = list(filters)

    if filter_list:
        clauses = []
        for column, clause_type in filter_list:
            identifier = sql.Identifier(column)
            if clause_type == "between":
                clauses.append(sql.SQL("{} BETWEEN %s AND %s").format(identifier))
            else:
                clauses.append(sql.SQL("{} = %s").format(identifier))

        where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(clauses)
        query = base_query + where_clause
    else:
        query = base_query

    cursor.execute(query, params)
    (count,) = cursor.fetchone()
    conn.close()
    return count
