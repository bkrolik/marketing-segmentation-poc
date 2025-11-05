def test_audience_query(client):
    payload = {
        "table_name": "resident_core",
        "filters": {
            "age": [25, 55],
            "kids_flag": True
        }
    }
    resp = client.post("/audience_dynamic", json=payload)
    assert resp.status_code == 200
    assert resp.json()["audience_size"] >= 1
