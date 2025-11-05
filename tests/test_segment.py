def test_segment_dynamic(client, mock_openai_llm):
    payload = {
        "business_description": "Family dentist focusing on kids.",
        "business_category": "dentist",
        "schema_name": "residents"
    }
    resp = client.post("/segment_dynamic", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "table_name" in body
    assert "filters" in body
