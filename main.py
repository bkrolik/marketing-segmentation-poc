from fastapi import FastAPI, HTTPException
from models import SchemaRequest, BusinessRequest, SegmentQueryRequest, SegmentResult
from redshift_client import fetch_schema, run_count_query
from openai_client import llm
import json

app = FastAPI()

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/schema")
def schema(payload: SchemaRequest):
    return fetch_schema(payload.schema_name)

@app.post("/segment_dynamic")
async def segment_dynamic(payload: BusinessRequest):
    metadata = fetch_schema(payload.schema_name)

    prompt = f"""
        User business category: {payload.business_category}
        Business description: {payload.business_description}

        Available dataset fields:
        {metadata}

        Output JSON with:
        - table_name
        - filters (dict of column:value or column:[min,max])
        You must respond with only valid JSON. Do not add commentary. Do not add explanation.
    """

    result = await llm(prompt)
    data = json.loads(result)
    parsed = SegmentResult(**data)  # throws if structure is wrong
    return parsed


@app.post("/audience_dynamic")
async def audience(payload: SegmentQueryRequest):
    metadata = fetch_schema("residents")
    allowed_columns = set(
        col["column_name"]
        for table in metadata
        for col in table["columns"]
    )

    conditions = []
    for col, val in payload.filters.items():
        if col not in allowed_columns:
            raise HTTPException(400, f"Invalid filter column: {col}")
        if isinstance(val, list) and len(val) == 2:
            low, high = val
            if low > high:
                raise HTTPException(400, f"Invalid range filter on {col}")
            conditions.append(f"{col} BETWEEN {low} AND {high}")
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