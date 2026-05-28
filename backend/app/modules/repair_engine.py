import os
import json
from typing import List
from app.schemas.app_spec import AppSpecification
from app.schemas.auth import RolePermission

def repair_spec(spec: AppSpecification, errors: List[str]) -> AppSpecification:
    """
    Self-healing compiler repair engine. Corrects mismatched DB, API, UI, and Auth integrations.
    Uses Gemini API if key is present, otherwise executes self-repair heuristics locally.
    """
    if not errors:
        return spec

    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            system_instruction = (
                "You are an expert compiler repair agent. You will receive an AppSpecification JSON "
                "which failed static analysis due to specific errors. Repair the JSON so it is 100% valid "
                "and does not violate any schema validations. "
                "Output ONLY the repaired valid JSON matching the AppSpecification schema."
            )
            
            prompt = (
                f"AppSpecification: {spec.model_dump_json()}\n\n"
                f"Validation Errors:\n" + "\n".join([f"- {e}" for e in errors])
            )
            
            response = model.generate_content(
                f"{system_instruction}\n\n{prompt}",
                generation_config={"temperature": 0, "response_mime_type": "application/json"}
            )
            
            data = json.loads(response.text.strip())
            return AppSpecification(**data)
        except Exception:
            pass

    # High fidelity heuristic self-repair compiler
    repaired = spec.model_copy(deep=True)
    db_tables = {t.name: t for t in repaired.db_schema.tables}
    valid_roles = {r.role_name for r in repaired.auth_schema.roles}

    for error in errors:
        # Scenario A: UI Page points to undefined role
        if "requires undefined role" in error:
            # e.g., "Page 'Sprint Board' requires undefined role 'guest'."
            # Extract page title and role
            parts = error.split("'")
            if len(parts) >= 5:
                page_title = parts[1]
                role_name = parts[3]
                
                # Option 1: Add the role to auth
                repaired.auth_schema.roles.append(
                    RolePermission(
                        role_name=role_name,
                        description=f"Auto-generated role for {page_title} access",
                        allowed_scopes=["*:read"]
                    )
                )
                valid_roles.add(role_name)

        # Scenario B: UI Form/Table references undefined database table
        elif "references undefined database table" in error:
            # e.g., "UI Component 'table_grid' references undefined database table 'cust'."
            # Find a close database table name match or fallback to the first table
            parts = error.split("'")
            if len(parts) >= 5:
                comp_id = parts[1]
                undef_table = parts[3]
                
                # Find closest table name
                closest_table = list(db_tables.keys())[0] if db_tables else "customers"
                for page in repaired.ui_schema.pages:
                    for comp in page.components:
                        if comp.id == comp_id:
                            comp.props["table_name"] = closest_table

        # Scenario C: UI Table/Form references undefined columns
        elif "displays undefined column" in error or "references undefined database field" in error:
            # e.g., "UI Table 'table_grid' displays undefined column 'salary' of table 'customers'."
            parts = error.split("'")
            if len(parts) >= 7:
                comp_id = parts[1]
                undef_col = parts[3]
                table_name = parts[5]
                
                # Fix: Remove column from displaying in the UI component
                for page in repaired.ui_schema.pages:
                    for comp in page.components:
                        if comp.id == comp_id:
                            if "columns" in comp.props:
                                comp.props["columns"] = [c for c in comp.props["columns"] if c != undef_col]
                            if "fields" in comp.props:
                                comp.props["fields"] = [f for f in comp.props["fields"] if (f.get("name") if isinstance(f, dict) else f) != undef_col]

        # Scenario D: Navigation item points to undefined route
        elif "points to undefined route" in error:
            # e.g., "Navigation item 'Billing' points to undefined route '/billing'."
            parts = error.split("'")
            if len(parts) >= 5:
                nav_label = parts[1]
                undef_route = parts[3]
                
                # Correct nav route to home or first valid page
                if repaired.ui_schema.pages:
                    first_route = repaired.ui_schema.pages[0].route
                    for nav in repaired.ui_schema.nav_items:
                        if nav.label == nav_label:
                            nav.route = first_route

    return repaired
