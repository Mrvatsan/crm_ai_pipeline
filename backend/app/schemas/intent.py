from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

class AppType(str, Enum):
    CRM = "CRM"
    DASHBOARD = "Dashboard"
    PROJECT_BOARD = "Project Management Board"
    ANALYTICS = "SaaS Analytics Hub"
    COMMERCE = "E-Commerce System"
    CUSTOM = "Custom Software Solution"

class EntityIntent(BaseModel):
    name: str = Field(..., description="Entity name, e.g., 'Customer', 'Task'")
    description: str = Field(..., description="Functional purpose of storing this entity")
    attributes: List[str] = Field(..., description="Fields extracted from prompt, e.g., ['first_name', 'deal_value']")
    actions: List[str] = Field(default_factory=lambda: ["create", "read", "update", "delete"], description="CRUD operations allowed")

class DashboardWidgetIntent(BaseModel):
    title: str = Field(..., description="Display title of the chart/metric card")
    metric_type: str = Field(..., description="Aggregation type, e.g., 'sum', 'count', 'avg'")
    target_column: str = Field(..., description="Target database column to calculate")
    visual_format: str = Field(..., description="Widget style, e.g., 'bar_chart', 'metric_card', 'line_chart'")

class IntentSpec(BaseModel):
    app_name: str = Field(..., description="Name of the application to compile")
    app_type: AppType = Field(default=AppType.CRM, description="Detected classification class")
    description: str = Field(..., description="Clean high-level architectural purpose overview")
    entities: List[EntityIntent] = Field(..., description="Dynamic CRUD model specifications")
    roles: List[str] = Field(default_factory=lambda: ["admin", "user"], description="Registered roles for RBAC")
    dashboards: List[DashboardWidgetIntent] = Field(default_factory=list, description="Planned metrics and widgets")
    has_auth: bool = Field(default=True, description="Detects whether user authentication is requested")
    has_payments: bool = Field(default=False, description="Detects premium plan paywall or gates")

    @validator("entities")
    def validate_entities_non_empty(cls, v):
        if not v:
            raise ValueError("IntentSpec must define at least one CRUD entity schema.")
        return v

    @validator("roles")
    def validate_roles_non_empty(cls, v):
        if not v:
            raise ValueError("IntentSpec must define at least one user role.")
        return v
