import json
import openai_client
from typing import Any, List
from fastapi import FastAPI, HTTPException
from redshift_client import FilterSpec, fetch_schema, run_count_query
from models import SchemaRequest, BusinessRequest, SegmentQueryRequest, SegmentResult


app = FastAPI()


@app.get("/health")
async def health():
    """
    Return a simple health check response.

    Returns:
        dict: A health payload with `{"ok": True}` when the service is healthy.
    """
    return {"ok": True}


@app.post("/schema")
def schema(payload: SchemaRequest):
    """
    Fetch table schema metadata for a schema name.

    Args:
        payload (SchemaRequest): Request containing `schema_name`.

    Returns:
        list[tuple]: Rows of (table_name, column_name, data_type) from information_schema.
    """
    return fetch_schema(payload.schema_name)


@app.post("/segment_dynamic")
async def segment_dynamic(payload: BusinessRequest):
    """
    Call the LLM to extract a structured target audience from a business description.

    The LLM must return only valid JSON that matches `SegmentResult`.

    Args:
        payload (BusinessRequest): Business description, category, and schema name.

    Returns:
        SegmentResult: Parsed result with `table_name` and `filters`.

    Raises:
        json.JSONDecodeError: If the LLM response is not valid JSON.
        ValidationError: If JSON does not match `SegmentResult` schema.
    """
    metadata = fetch_schema(payload.schema_name)

    prompt = f"""
        You are a marketing assistant. Extract a structured target audience
        from this business description. You must respond with only valid JSON. 
        Do not add commentary. Do not add explanation.
        User business category: {payload.business_category}
        Business description: {payload.business_description}

        Available dataset fields:
        {metadata}

        Output JSON with:
        - table_name
        - filters (dict of column:value or column:[min,max])
    """

    result = await openai_client.llm(prompt)
    data = json.loads(result)
    parsed = SegmentResult(**data)  # throws if structure is wrong
    return parsed


@app.post("/audience_dynamic")
async def audience(payload: SegmentQueryRequest):
    """
    Compute audience size using provided filters and a target table.

    Validates filter column names against the `residents` schema, converts
    range filters to `between` clauses, and executes a count query.

    Args:
        payload (SegmentQueryRequest): `{table_name, filters}`.

    Returns:
        dict: `{"audience_size": <int>}`

    Raises:
        HTTPException: For invalid filter columns or invalid range filters.
    """
    metadata = fetch_schema("residents")
    allowed_columns = {column_name for _, column_name, _ in metadata}

    filters: List[FilterSpec] = []
    params: List[Any] = []

    for col, val in payload.filters.items():
        if col not in allowed_columns:
            raise HTTPException(400, f"Invalid filter column: {col}")

        if isinstance(val, (list, tuple)) and len(val) == 2:
            low, high = val
            if low > high:
                raise HTTPException(400, f"Invalid range filter on {col}")
            filters.append((col, "between"))
            params.extend([low, high])
        else:
            filters.append((col, "eq"))
            params.append(val)

    size = run_count_query(payload.table_name, filters, params)

    return {"audience_size": size}


def run():
    """
    Start the FastAPI app with Uvicorn in reload mode.

    Intended for local development; imports `uvicorn` at runtime to avoid
    adding it as a hard dependency for library usage.
    """
    import uvicorn
    uvicorn.run("main:app", reload=True)
