from pydantic import BaseModel, Field
from app.schemas.db import DBSchemaSpec
from app.schemas.api import APISchemaSpec
from app.schemas.ui import UISchemaSpec
from app.schemas.auth import AuthSchemaSpec

class AppSpecification(BaseModel):
    app_name: str = Field(..., description="Name of the generated application")
    db_schema: DBSchemaSpec = Field(..., description="Complete database definition and seed data")
    api_schema: APISchemaSpec = Field(..., description="API endpoints contracts and query mapping")
    ui_schema: UISchemaSpec = Field(..., description="Frontend navigation, pages, and components layouts")
    auth_schema: AuthSchemaSpec = Field(..., description="RBAC and premium monetization parameters")
