from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class APIOperation(str, Enum):
    LIST = "list"
    RETRIEVE = "retrieve"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ANALYTICS = "analytics" # Aggregations/metrics

class QueryParamSpec(BaseModel):
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type, e.g. 'str', 'int'")
    description: str = Field(..., description="Purpose of query parameter")
    required: bool = Field(default=False)

class APIEndpoint(BaseModel):
    path: str = Field(..., description="Route path, e.g. '/api/customers' or '/api/customers/{id}'")
    method: str = Field(..., description="HTTP Method, e.g. 'GET', 'POST', 'PUT', 'DELETE'")
    operation: APIOperation = Field(..., description="Type of operation")
    target_table: str = Field(..., description="Underlying database table for queries")
    auth_required: bool = Field(default=True, description="Authentication required?")
    allowed_roles: List[str] = Field(default_factory=list, description="Roles permitted, empty means all authenticated")
    is_premium_gated: bool = Field(default=False, description="Is this endpoint locked behind a premium plan?")
    query_params: List[QueryParamSpec] = Field(default_factory=list, description="Allowed query string parameters")
    request_fields: List[str] = Field(default_factory=list, description="Fields allowed in request body (for CREATE/UPDATE)")
    response_fields: List[str] = Field(default_factory=list, description="Fields returned in response body")

class APISchemaSpec(BaseModel):
    endpoints: List[APIEndpoint] = Field(..., description="List of all API endpoints exposed by the generated backend")
