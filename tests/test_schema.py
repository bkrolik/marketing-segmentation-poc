import requests

def test_schema_endpoint():
    resp = requests.post("http://localhost:8000/schema", json={"schema_name": "residents"})
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) > 0
    assert any("age" in str(r) for r in rows)
