from pydantic import BaseModel
from typing import Dict, Any


class SchemaRequest(BaseModel):
    """
    Pydantic model for schema metadata requests.

    Attributes:
        schema_name (str): Name of the schema to fetch metadata for.
    """
    schema_name: str


class BusinessRequest(BaseModel):
    """
    Pydantic model for supplying business context to the LLM.

    Attributes:
        business_description (str): Free-text description of the business.
        business_category (str): Category label for the business.
        schema_name (str): Name of dataset schema to reference.
    """
    business_description: str
    business_category: str
    schema_name: str


class SegmentQueryRequest(BaseModel):
    """
    Pydantic model for executing segment queries against a table.

    Attributes:
        table_name (str): Target table to query.
        filters (dict): Mapping of column names to equality or range filters.
    """
    table_name: str
    filters: Dict[str, Any]


class SegmentResult(BaseModel):
    """
    Pydantic model for the LLM output describing a segment.

    Attributes:
        table_name (str): Table name containing the target audience.
        filters (dict): Structured filters to apply to the table (column:value or column:[min, max]).
    """
    table_name: str
    filters: Dict[str, Any]
