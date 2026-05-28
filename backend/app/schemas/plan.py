from pydantic import BaseModel, Field
from typing import List, Dict, Any

class DBTablePlan(BaseModel):
    table_name: str = Field(..., description="Target database table name")
    description: str = Field(..., description="What this table stores")
    columns: List[str] = Field(..., description="Key columns planned for this table")
    relations: List[str] = Field(default_factory=list, description="Foreign keys and associations planned")

class APIEndpointPlan(BaseModel):
    path: str = Field(..., description="Endpoint path, e.g. '/api/customers'")
    method: str = Field(..., description="HTTP Method, e.g. 'GET', 'POST'")
    action: str = Field(..., description="CRUD action, e.g. 'list', 'create'")
    auth_required: bool = Field(default=True, description="Whether endpoint requires auth")

class UIPagePlan(BaseModel):
    route: str = Field(..., description="Page path in frontend, e.g. '/dashboard'")
    title: str = Field(..., description="Title of the page")
    components: List[str] = Field(..., description="UI primitives planned, e.g. ['Table', 'MetricCard']")

class AuthPlanSpec(BaseModel):
    roles: List[str] = Field(..., description="Configured roles")
    gated_routes: List[str] = Field(..., description="Routes restricted to specific roles")

class ArchitecturePlan(BaseModel):
    app_name: str = Field(..., description="Application name")
    explanation: str = Field(..., description="High-level engineering design decisions")
    db_tables: List[DBTablePlan] = Field(..., description="Planned DB tables")
    api_endpoints: List[APIEndpointPlan] = Field(..., description="Planned backend endpoints")
    ui_pages: List[UIPagePlan] = Field(..., description="Planned UI page layout structure")
    auth_policy: AuthPlanSpec = Field(..., description="Planned authorization rules")
