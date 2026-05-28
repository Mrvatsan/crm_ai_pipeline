from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ComponentType(str, Enum):
    TABLE = "Table"
    FORM = "Form"
    CHART = "Chart"
    METRIC_CARD = "MetricCard"
    PREMIUM_GATE = "PremiumGate"
    HEADER = "Header"

class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    AREA = "area"

class FormFieldType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    SELECT = "select"
    DATE = "date"
    TEXTAREA = "textarea"

class FormField(BaseModel):
    name: str = Field(..., description="Field key matching database/API column")
    label: str = Field(..., description="Human readable label")
    type: FormFieldType = Field(..., description="HTML Input type")
    placeholder: Optional[str] = Field(default=None)
    required: bool = Field(default=True)
    options: Optional[List[str]] = Field(default=None, description="Select option list (if type=select)")

class UIComponent(BaseModel):
    id: str = Field(..., description="Unique component ID")
    type: ComponentType = Field(..., description="Type of component block")
    title: str = Field(..., description="Display title for the component")
    target_api_path: Optional[str] = Field(default=None, description="Backend endpoint URL for data operations")
    grid_span: int = Field(default=12, description="Width in columns on a 12-column grid")
    props: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible key-value properties for custom options. "
                    "e.g. for Table: {'columns': ['id', 'name'], 'actions': ['edit', 'delete']}. "
                    "e.g. for Chart: {'chart_type': 'bar', 'x_axis': 'month', 'y_axis': 'sales'}. "
                    "e.g. for MetricCard: {'value_key': 'revenue', 'icon': 'dollar'}"
    )

class UIPage(BaseModel):
    route: str = Field(..., description="URL path in frontend, e.g. '/dashboard'")
    title: str = Field(..., description="Title of the page")
    icon: Optional[str] = Field(default=None, description="Lucide icon name, e.g. 'home', 'users'")
    required_role: Optional[str] = Field(default=None, description="If set, only users with this role can view")
    is_premium_gated: bool = Field(default=False, description="Is page locked for premium plans?")
    components: List[UIComponent] = Field(default_factory=list, description="Array of components in rendering order")

class NavItem(BaseModel):
    label: str = Field(..., description="Sidebar nav label")
    route: str = Field(..., description="Destination route path")
    icon: str = Field(..., description="Icon name")
    required_role: Optional[str] = Field(default=None)

class UISchemaSpec(BaseModel):
    nav_items: List[NavItem] = Field(..., description="Sidebar navigation items")
    pages: List[UIPage] = Field(..., description="List of all app pages")
