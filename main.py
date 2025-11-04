from fastapi import FastAPI
from models import SchemaRequest, BusinessRequest, SegmentQueryRequest
from redshift_client import fetch_schema, run_count_query
from openai_client import llm
import json

app = FastAPI()

@app.post("/schema")
def schema(payload: SchemaRequest):
    return fetch_schema(payload.schema_name)

@app.post("/segment_dynamic")
def segment_dynamic(payload: BusinessRequest):
    metadata = fetch_schema(payload.schema_name)

    prompt = f"""
        User business category: {payload.business_category}
        Business description: {payload.business_description}

        Available dataset fields:
        {metadata}

        Output JSON with:
        - table_name
        - filters (dict of column:value or column:[min,max])
        Only output JSON.
    """

    return json.loads(llm(prompt))

@app.post("/audience_dynamic")
def audience(payload: SegmentQueryRequest):

    conditions = []
    for col, val in payload.filters.items():
        if isinstance(val, list) and len(val) == 2:
            conditions.append(f"{col} BETWEEN {val[0]} AND {val[1]}")
        elif isinstance(val, bool):
            conditions.append(f"{col} = {val}")
        else:
            conditions.append(f"{col} = '{val}'")

    where_clause = " AND ".join(conditions)
    size = run_count_query(payload.table_name, where_clause)

    return {"audience_size": size}

def run():
    import uvicorn
    uvicorn.run("main:app", reload=True)