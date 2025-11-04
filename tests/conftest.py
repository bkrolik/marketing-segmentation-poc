import os
import time
import pytest
import psycopg2
from unittest.mock import patch

DB_CONN = dict(
    host="localhost",
    port=5439,
    dbname="analytics",
    user="test",
    password="test"
)

def wait_for_db():
    for _ in range(10):
        try:
            psycopg2.connect(**DB_CONN).close()
            return
        except:
            time.sleep(1)
    raise RuntimeError("Database not ready")

@pytest.fixture(scope="session", autouse=True)
def db_ready():
    wait_for_db()

@pytest.fixture(autouse=True)
def reset_db():
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    cur.execute("DELETE FROM residents.resident_core;")
    conn.commit()

    # seed a few predictable rows
    cur.execute("""
        INSERT INTO residents.resident_core VALUES
        ('p1', 34, 60000, true, 2.1),
        ('p2', 41, 120000, false, 5.0),
        ('p3', 29, 80000, true, 1.5),
        ('p4', 52, 90000, false, 3.0);
    """)
    conn.commit()
    conn.close()

@pytest.fixture
def mock_openai_llm():
    with patch("openai_client.llm") as mocker:
        mocker.return_value = '{"table_name":"resident_core","filters":{"age":[25,55],"kids_flag":true}}'
        yield mocker
