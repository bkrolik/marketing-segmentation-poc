def test_schema_endpoint(client):
    resp = client.post("/schema", json={"schema_name": "residents"})
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) > 0
    assert any("age" in str(r) for r in rows)
