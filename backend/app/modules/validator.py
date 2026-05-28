import json
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any, Optional, Type

# ==========================================
# STRUCTURED VALIDATION SCHEMAS
# ==========================================

class ValidationErrorDetail(BaseModel):
    category: str = Field(..., description="Classification category of the compile violation, e.g. syntax, api_db, api_ui, auth")
    field_path: str = Field(..., description="Precise path in the App Specification AST where the error occurred")
    message: str = Field(..., description="Human-readable engineering compile failure report")
    repair_trigger: Dict[str, Any] = Field(
        ..., 
        description="Actionable heuristic trigger dictionary guiding the self-repair pipeline. "
                    "e.g., {'action': 'add_role', 'role_name': 'guest'}"
    )

class ValidationResult(BaseModel):
    is_valid: bool = Field(..., description="Boolean compilation flag")
    errors: List[ValidationErrorDetail] = Field(default_factory=list, description="Array of detected static analysis compile errors")

# ==========================================
# THE VALIDATION ENGINE
# ==========================================

from app.schemas.app_spec import AppSpecification

def validate_json_syntax(raw_json: str, schema_class: Type[BaseModel]) -> ValidationResult:
    """
    Validates JSON syntax and Pydantic field requirements.
    """
    errors = []
    
    # 1. Check raw JSON syntax
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as de:
        errors.append(
            ValidationErrorDetail(
                category="syntax",
                field_path="root",
                message=f"JSON Syntax Error: {de.msg} at line {de.lineno} column {de.colno}",
                repair_trigger={"action": "reformat_json", "reason": str(de)}
            )
        )
        return ValidationResult(is_valid=False, errors=errors)

    # 2. Check required Pydantic fields
    try:
        schema_class(**data)
    except ValidationError as ve:
        for err in ve.errors():
            loc_str = ".".join([str(loc) for loc in err["loc"]])
            errors.append(
                ValidationErrorDetail(
                    category="required_fields",
                    field_path=loc_str,
                    message=f"Schema violation at field '{loc_str}': {err['msg']} (type: {err['type']})",
                    repair_trigger={"action": "default_initialize_field", "field": loc_str}
                )
            )
            
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def validate_spec(spec: AppSpecification) -> List[str]:
    """
    Legacy wrapper maintaining 100% backward compatibility with pipeline.py and test suites.
    Returns compile violations as standard flat string lists.
    """
    result = validate_spec_structured(spec)
    return [f"[{e.category.upper()} ERROR] at {e.field_path}: {e.message}" for e in result.errors]


def validate_spec_structured(spec: AppSpecification) -> ValidationResult:
    """
    Performs deep multi-layer structural and security static analysis audits on the compiled App Specification IR.
    """
    errors: List[ValidationErrorDetail] = []
    
    # Extract DB table register
    db_tables = {table.name: table for table in spec.db_schema.tables}
    valid_roles = {role.role_name for role in spec.auth_schema.roles}

    # 1. Cross-Layer: API to Database mapping
    for i, endpoint in enumerate(spec.api_schema.endpoints):
        path_prefix = f"api_schema.endpoints[{i}]"
        
        # Verify endpoint targets a valid registered DB table
        if endpoint.target_table not in db_tables:
            errors.append(
                ValidationErrorDetail(
                    category="api_db",
                    field_path=f"{path_prefix}.target_table",
                    message=f"API endpoint '{endpoint.path}' references undefined database table '{endpoint.target_table}'",
                    repair_trigger={"action": "remap_table", "component": "endpoint", "path": endpoint.path, "target_table": endpoint.target_table}
                )
            )
        else:
            table = db_tables[endpoint.target_table]
            valid_columns = {col.name for col in table.columns}
            
            # Verify request fields exist in DB table columns
            for rf in endpoint.request_fields:
                if rf != "id" and rf not in valid_columns:
                    errors.append(
                        ValidationErrorDetail(
                            category="api_db",
                            field_path=f"{path_prefix}.request_fields",
                            message=f"API request field '{rf}' does not exist on table '{endpoint.target_table}'",
                            repair_trigger={"action": "add_column", "table_name": endpoint.target_table, "column_name": rf, "column_type": "text"}
                        )
                    )

            # Verify response fields exist in DB table columns
            for rf in endpoint.response_fields:
                if rf not in ["id", "success", "message", "value"] and rf not in valid_columns:
                    errors.append(
                        ValidationErrorDetail(
                            category="api_db",
                            field_path=f"{path_prefix}.response_fields",
                            message=f"API response field '{rf}' does not exist on table '{endpoint.target_table}'",
                            repair_trigger={"action": "add_column", "table_name": endpoint.target_table, "column_name": rf, "column_type": "text"}
                        )
                    )

    # 2. Cross-Layer: UI to API navigation maps
    valid_routes = {page.route: page for page in spec.ui_schema.pages}
    for i, nav in enumerate(spec.ui_schema.nav_items):
        if nav.route not in valid_routes:
            errors.append(
                ValidationErrorDetail(
                    category="ui_routing",
                    field_path=f"ui_schema.nav_items[{i}].route",
                    message=f"Sidebar navigation label '{nav.label}' references undefined route path '{nav.route}'",
                    repair_trigger={"action": "remap_nav_route", "label": nav.label, "route": nav.route}
                )
            )

    # 3. Cross-Layer: UI components integration
    for p_idx, page in enumerate(spec.ui_schema.pages):
        page_path = f"ui_schema.pages[{p_idx}]"
        
        # Auth: Verify page required role is registered in security policy
        if page.required_role and page.required_role not in valid_roles:
            errors.append(
                ValidationErrorDetail(
                    category="auth",
                    field_path=f"{page_path}.required_role",
                    message=f"UI Page '{page.title}' requires undefined role '{page.required_role}'",
                    repair_trigger={"action": "add_role", "role_name": page.required_role}
                )
            )

        for c_idx, comp in enumerate(page.components):
            comp_path = f"{page_path}.components[{c_idx}]"
            
            # Check Table and Form integrations
            if comp.type == "Table" or comp.type == "Form":
                if not comp.target_api_path:
                    errors.append(
                        ValidationErrorDetail(
                            category="api_ui",
                            field_path=f"{comp_path}.target_api_path",
                            message=f"UI interactive element '{comp.id}' is missing a required API target path",
                            repair_trigger={"action": "set_api_path", "component_id": comp.id, "component_type": comp.type.value}
                        )
                    )
                
                table_name = comp.props.get("table_name")
                if table_name:
                    if table_name not in db_tables:
                        errors.append(
                            ValidationErrorDetail(
                                category="api_ui",
                                field_path=f"{comp_path}.props.table_name",
                                message=f"UI Component '{comp.id}' binds to non-existent database table '{table_name}'",
                                repair_trigger={"action": "remap_table", "component": "ui", "component_id": comp.id, "target_table": table_name}
                            )
                        )
                    else:
                        table = db_tables[table_name]
                        valid_columns = {col.name for col in table.columns}
                        
                        # Validate columns displayed by UI Table widget
                        columns = comp.props.get("columns", [])
                        for col in columns:
                            if col != "id" and col not in valid_columns:
                                errors.append(
                                    ValidationErrorDetail(
                                        category="api_ui",
                                        field_path=f"{comp_path}.props.columns",
                                        message=f"UI Table grid '{comp.id}' displays undefined column '{col}' of table '{table_name}'",
                                        repair_trigger={"action": "remove_ui_field", "component_id": comp.id, "field_name": col, "type": "column"}
                                    )
                                )

                        # Validate input fields in UI Form widget
                        fields = comp.props.get("fields", [])
                        for f in fields:
                            field_name = f.get("name") if isinstance(f, dict) else f
                            if field_name not in valid_columns:
                                errors.append(
                                    ValidationErrorDetail(
                                        category="api_ui",
                                        field_path=f"{comp_path}.props.fields",
                                        message=f"UI Form '{comp.id}' contains input field '{field_name}' not found in DB table '{table_name}'",
                                        repair_trigger={"action": "remove_ui_field", "component_id": comp.id, "field_name": field_name, "type": "field"}
                                    )
                                )

    # 4. Cross-Layer: Auth Roles mapping to dynamic APIs
    for i, endpoint in enumerate(spec.api_schema.endpoints):
        for r in endpoint.allowed_roles:
            if r not in valid_roles:
                errors.append(
                    ValidationErrorDetail(
                        category="auth",
                        field_path=f"api_schema.endpoints[{i}].allowed_roles",
                        message=f"API endpoint path '{endpoint.path}' allows unregistered role scope '{r}'",
                        repair_trigger={"action": "add_role", "role_name": r}
                    )
                )

    return ValidationResult(is_valid=len(errors) == 0, errors=errors)
