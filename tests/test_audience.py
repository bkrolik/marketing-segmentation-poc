import requests

def test_audience_query():
    payload = {
        "table_name": "resident_core",
        "filters": {
            "age": [25,55],
            "kids_flag": True
        }
    }
    resp = requests.post("http://localhost:8000/audience_dynamic", json=payload)
    assert resp.status_code == 200
    assert resp.json()["audience_size"] >= 1
