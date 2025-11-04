import requests

def test_segment_dynamic(mock_openai_llm):
    payload = {
        "business_description": "Family dentist focusing on kids.",
        "business_category": "dentist",
        "schema_name": "residents"
    }
    resp = requests.post("http://localhost:8000/segment_dynamic", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "table_name" in body
    assert "filters" in body
