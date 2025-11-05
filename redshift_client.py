import os
import redshift_connector
from dotenv import load_dotenv

if os.getenv("ENV") == "TEST":
    load_dotenv(".env.test")
else:
    load_dotenv()

def get_conn():
    if os.getenv("ENV") == "TEST":
        import psycopg2
        return psycopg2.connect(
            host=os.getenv("REDSHIFT_HOST"),
            port=os.getenv("REDSHIFT_PORT"),
            dbname=os.getenv("REDSHIFT_DATABASE"),
            user=os.getenv("REDSHIFT_USER"),
            password=os.getenv("REDSHIFT_PASSWORD")
        )

    return redshift_connector.connect(
        host=os.getenv("REDSHIFT_HOST"),
        port=int(os.getenv("REDSHIFT_PORT")),
        database=os.getenv("REDSHIFT_DATABASE"),
        user=os.getenv("REDSHIFT_USER"),
        password=os.getenv("REDSHIFT_PASSWORD")
    )

def fetch_schema(schema_name: str):
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

def run_count_query(table_name: str, where_clause: str):
    conn = get_conn()
    cursor = conn.cursor()

    query = f"""
        SELECT COUNT(*) FROM {table_name}
        WHERE {where_clause};
    """

    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result[0]
