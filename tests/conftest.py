# import os
import time
import pytest
import psycopg2
from unittest.mock import patch, AsyncMock
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from main import app


load_dotenv(".env.test")

DB_CONN = dict(
    host="localhost",
    port=5439,
    dbname="analytics",
    user="test",
    password="test"
)


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


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

    cur.execute("CREATE SCHEMA IF NOT EXISTS residents;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS residents.resident_core (
            pseudonymous_id VARCHAR,
            age INT,
            income_band INT,
            kids_flag BOOLEAN,
            distance_miles FLOAT
        );
    """)

    cur.execute("DELETE FROM residents.resident_core;")
    conn.commit()

    # seed predictable data
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
    with patch("openai_client.llm", new_callable=AsyncMock) as mocker:
        mocker.return_value = '{"table_name": "resident_core", "filters": {"age": [25,55], "kids_flag": true}}'
        yield mocker