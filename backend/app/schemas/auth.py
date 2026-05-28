from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class RolePermission(BaseModel):
    role_name: str = Field(..., description="Role key, e.g., 'admin', 'manager', 'user'")
    description: str = Field(..., description="Description of role privileges")
    allowed_scopes: List[str] = Field(
        ...,
        description="Allowed actions/resources, e.g., ['customers:read', 'customers:create', 'analytics:view']"
    )

class PremiumGatingConfig(BaseModel):
    is_gating_enabled: bool = Field(default=False, description="Enable payment premium wall")
    premium_features: List[str] = Field(
        default_factory=list,
        description="Features requiring upgrade, e.g., ['analytics', 'billing']"
    )
    upgrade_message: str = Field(
        default="Upgrade to Premium to access this feature.",
        description="Message shown to free users attempting access"
    )

class AuthSchemaSpec(BaseModel):
    roles: List[RolePermission] = Field(..., description="Role permissions registry")
    premium_gating: PremiumGatingConfig = Field(..., description="Premium monetization gate parameters")
