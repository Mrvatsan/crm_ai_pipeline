import sys
import os
import pytest

# Add parent directories to sys.path so we can import app modules directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.pipeline import compile_application
from app.modules.validator import validate_spec
from app.modules.repair_engine import repair_spec
from app.schemas.auth import RolePermission
import app.database.dynamic_db as db

def test_full_pipeline_compilation():
    """
    Validates that a typical CRM request successfully compiles,
    validates with zero errors, and correctly sets up dynamic tables.
    """
    prompt = "Create a premium SaaS customer relationship portal with sales deal analytics"
    spec, errors = compile_application(prompt)
    
    assert errors == [], f"Expected 0 compilation errors, got: {errors}"
    assert spec.app_name == "Apex CRM Portal"
    assert len(spec.db_schema.tables) > 0
    assert len(spec.api_schema.endpoints) > 0
    assert len(spec.ui_schema.pages) > 0

    # Verify dynamic DB records were successfully populated
    customers = db.list_records("customers")
    assert len(customers) > 0
    assert customers[0]["full_name"] == "Tony Stark"
    assert customers[0]["deal_value"] == 750000.0

def test_static_analysis_validator_detects_errors():
    """
    Injects structural mismatches into a valid specification and verifies
    that the validator flags them correctly.
    """
    prompt = "Create a basic dashboard"
    spec, _ = compile_application(prompt)
    
    # 1. Inject an invalid column display on the UI Table
    # The 'customers' table has no 'salary' column
    table_comp = None
    for page in spec.ui_schema.pages:
        for comp in page.components:
            if comp.type == "Table":
                table_comp = comp
                break
        if table_comp:
            break
            
    assert table_comp is not None
    table_comp.props["table_name"] = "customers"
    table_comp.props["columns"].append("salary") # Mismatch!
    
    # 2. Inject an invalid role requirement on a UI Page
    spec.ui_schema.pages[0].required_role = "executive_manager" # Mismatch!
    
    errors = validate_spec(spec)
    
    # Check that both violations are flagged by compile validation
    has_column_error = any("displays undefined column 'salary'" in e for e in errors)
    has_role_error = any("requires undefined role 'executive_manager'" in e for e in errors)
    
    assert has_column_error, "Validator failed to flag mismatching UI column"
    assert has_role_error, "Validator failed to flag undefined page access role"

def test_repair_engine_self_healing():
    """
    Tests that feeding validation errors into the repair engine
    heals the specifications and returns a 100% valid spec.
    """
    prompt = "Create a dynamic board"
    spec, _ = compile_application(prompt)
    
    # Inject bad column
    table_comp = None
    for page in spec.ui_schema.pages:
        for comp in page.components:
            if comp.type == "Table":
                table_comp = comp
                break
        if table_comp:
            break
            
    assert table_comp is not None
    table_comp.props["table_name"] = "customers"
    table_comp.props["columns"].append("secret_revenue_stream")
    
    # Inject bad page role
    spec.ui_schema.pages[0].required_role = "anonymous_super_user"
    
    # Run static validation
    errors = validate_spec(spec)
    assert len(errors) >= 2
    
    # Run repair engine
    repaired_spec = repair_spec(spec, errors)
    
    # Validate repaired spec
    repaired_errors = validate_spec(repaired_spec)
    assert repaired_errors == [], f"Repair engine failed to heal specification. Errors: {repaired_errors}"
    
    # Verify that the bad column was removed by the heuristic repair
    repaired_table_comp = None
    for page in repaired_spec.ui_schema.pages:
        for comp in page.components:
            if comp.type == "Table":
                repaired_table_comp = comp
                break
        if repaired_table_comp:
            break
    assert "secret_revenue_stream" not in repaired_table_comp.props["columns"]
    
    # Verify the role was dynamically registered to allow clean compilation
    registered_roles = {r.role_name for r in repaired_spec.auth_schema.roles}
    assert "anonymous_super_user" in registered_roles
