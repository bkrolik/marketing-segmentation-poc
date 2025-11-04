from pydantic import BaseModel
from typing import Dict, Any

class SchemaRequest(BaseModel):
    schema_name: str

class BusinessRequest(BaseModel):
    business_description: str
    business_category: str
    schema_name: str

class SegmentQueryRequest(BaseModel):
    table_name: str
    filters: Dict[str, Any]
    