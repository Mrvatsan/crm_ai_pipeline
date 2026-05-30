import sys
import os

# Add parent directory to sys.path so we can import app modules directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.pipeline import compile_application

def test_verify_real_dynamic_generation():
    """
    Verifies that different user prompts produce visibly and structurally different
    application names, database schemas, tables, pages, and dynamic seed data.
    """
    print("\n[DYNAMIC COMPILATION VERIFICATION]")
    
    # 1. Compile CRM Spec
    print("-> Compiling CRM spec...")
    crm_spec, crm_errors = compile_application("Build CRM")
    assert not crm_errors, f"CRM compiled with errors: {crm_errors}"
    
    # 2. Compile Hospital Spec
    print("-> Compiling Hospital Management System spec...")
    hms_spec, hms_errors = compile_application("Build Hospital Management System")
    assert not hms_errors, f"Hospital system compiled with errors: {hms_errors}"
    
    # 3. Compile Inventory Spec
    print("-> Compiling Inventory Management spec...")
    inv_spec, inv_errors = compile_application("Build Inventory Management")
    assert not inv_errors, f"Inventory system compiled with errors: {inv_errors}"

    # ==========================================
    # VERIFY STRUCTURAL DIFFERENTIATION (Issue 9)
    # ==========================================
    
    # Verify Application Names are distinct
    print(f"CRM App Name: '{crm_spec.app_name}'")
    print(f"Hospital App Name: '{hms_spec.app_name}'")
    print(f"Inventory App Name: '{inv_spec.app_name}'")
    
    assert crm_spec.app_name != hms_spec.app_name, "App names for CRM and HMS are identical!"
    assert hms_spec.app_name != inv_spec.app_name, "App names for HMS and Inventory are identical!"
    assert crm_spec.app_name != inv_spec.app_name, "App names for CRM and Inventory are identical!"

    # Verify Database Tables are distinct
    crm_tables = {t.name for t in crm_spec.db_schema.tables}
    hms_tables = {t.name for t in hms_spec.db_schema.tables}
    inv_tables = {t.name for t in inv_spec.db_schema.tables}

    print(f"CRM Tables: {crm_tables}")
    print(f"Hospital Tables: {hms_tables}")
    print(f"Inventory Tables: {inv_tables}")

    # Ensure table schemas differ significantly
    assert crm_tables != hms_tables, "FAIL: Generated database tables for CRM and Hospital System are identical!"
    assert hms_tables != inv_tables, "FAIL: Generated database tables for Hospital and Inventory System are identical!"
    assert crm_tables != inv_tables, "FAIL: Generated database tables for CRM and Inventory System are identical!"

    # Domain specific assertions to guarantee user intent mapping
    assert any("customer" in t or "lead" in t or "contact" in t for t in crm_tables), "CRM tables do not match CRM domain keywords!"
    assert any("patient" in t or "doctor" in t or "appointment" in t for t in hms_tables), "Hospital tables do not match HMS domain keywords!"
    assert any("product" in t or "warehouse" in t or "supplier" in t for t in inv_tables), "Inventory tables do not match Inventory domain keywords!"

    # Verify UI Pages and routes are distinct
    crm_routes = {p.route for p in crm_spec.ui_schema.pages}
    hms_routes = {p.route for p in hms_spec.ui_schema.pages}
    inv_routes = {p.route for p in inv_spec.ui_schema.pages}

    print(f"CRM Routes: {crm_routes}")
    print(f"Hospital Routes: {hms_routes}")
    print(f"Inventory Routes: {inv_routes}")

    # Ensure page route layouts differ
    assert crm_routes != hms_routes, "FAIL: Generated UI pages for CRM and Hospital System are identical!"
    assert hms_routes != inv_routes, "FAIL: Generated UI pages for Hospital and Inventory System are identical!"
    assert crm_routes != inv_routes, "FAIL: Generated UI pages for CRM and Inventory System are identical!"

    print("\n[SUCCESS] Dynamic generation verification passed. Schemas are beautifully distinct and intention-driven!")

if __name__ == "__main__":
    try:
        test_verify_real_dynamic_generation()
        sys.exit(0)
    except AssertionError as ae:
        print(f"\n[FAILURE] {str(ae)}")
        sys.exit(1)
