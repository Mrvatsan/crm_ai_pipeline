import os
import json
from app.schemas.plan import ArchitecturePlan
from app.schemas.ui import UISchemaSpec, UIPage, UIComponent, NavItem, ComponentType, ChartType

def generate_ui(plan: ArchitecturePlan) -> UISchemaSpec:
    """
    Constructs concrete frontend UI layouts matching specific component tree hierarchies.
    Uses Gemini API if key is present, otherwise maps default templates.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            system_instruction = (
                "You are an expert Frontend Architect. Convert an ArchitecturePlan JSON into a UISchemaSpec JSON "
                "with detailed navigation items and pages matching this schema:\n"
                "{\n"
                "  \"nav_items\": [{ \"label\": \"string\", \"route\": \"string\", \"icon\": \"string\", \"required_role\": null }],\n"
                "  \"pages\": [\n"
                "    {\n"
                "      \"route\": \"string\",\n"
                "      \"title\": \"string\",\n"
                "      \"icon\": \"string\",\n"
                "      \"required_role\": null,\n"
                "      \"is_premium_gated\": false,\n"
                "      \"components\": [\n"
                "        { \"id\": \"string\", \"type\": \"Table/Form/Chart/MetricCard/PremiumGate/Header\", \"title\": \"string\", \"target_api_path\": \"string\", \"grid_span\": 12, \"props\": {} }\n"
                "      ]\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "Output ONLY JSON. Use grid_span=6 for side-by-side elements."
            )
            
            response = model.generate_content(
                f"{system_instruction}\n\nArchitecture Plan JSON: {plan.model_dump_json()}",
                generation_config={"temperature": 0, "response_mime_type": "application/json"}
            )
            
            data = json.loads(response.text.strip())
            return UISchemaSpec(**data)
        except Exception:
            pass

    # High fidelity local dynamic UI layout builder
    nav_items = []
    pages = []
    
    # Map Navigation items based on planned pages
    for page_plan in plan.ui_pages:
        icon_name = "home"
        if "members" in page_plan.route or "customers" in page_plan.route:
            icon_name = "users"
        elif "tasks" in page_plan.route or "interactions" in page_plan.route:
            icon_name = "clipboard-list"
        elif "billing" in page_plan.route or "subscription" in page_plan.route:
            icon_name = "credit-card"
        
        nav_items.append(
            NavItem(
                label=page_plan.title,
                route=page_plan.route,
                icon=icon_name,
                required_role=None
            )
        )

    # Build dynamic components per page
    for page_plan in plan.ui_pages:
        components = []
        
        # 1. Header always rendered first
        components.append(
            UIComponent(
                id=f"{page_plan.title.lower().replace(' ', '_')}_header",
                type=ComponentType.HEADER,
                title=page_plan.title,
                grid_span=12,
                props={"subtitle": f"Manage your {page_plan.title.lower()}"}
            )
        )

        for comp_type in page_plan.components:
            if comp_type == "Header":
                continue
                
            elif comp_type == "MetricCard":
                # Render analytical metric indicators
                tname = plan.db_tables[0].table_name
                colname = "deal_value" if "customers" in tname else ("revenue_impact" if "metric" in tname else "id")
                label = "Total Pipeline Value" if "customers" in tname else ("Financial Velocity" if "metric" in tname else "Total Backlog")
                icon = "dollar-sign" if colname != "id" else "check-square"
                
                components.append(
                    UIComponent(
                        id=f"metric_{tname}_card",
                        type=ComponentType.METRIC_CARD,
                        title=label,
                        target_api_path="/api/analytics/metrics",
                        grid_span=6,
                        props={
                            "operation": "sum" if colname != "id" else "count",
                            "column": colname,
                            "label": label,
                            "icon": icon
                        }
                    )
                )

            elif comp_type == "Chart":
                tname = plan.db_tables[0].table_name
                group_by_col = "status" if "customers" in tname else ("category" if "metric" in tname else "priority")
                agg_col = "deal_value" if "customers" in tname else "id"
                label = "Deals by Status" if "customers" in tname else "Telemetry Category Count"
                
                components.append(
                    UIComponent(
                        id=f"chart_{tname}_distribution",
                        type=ComponentType.CHART,
                        title=label,
                        target_api_path="/api/analytics/metrics",
                        grid_span=6,
                        props={
                            "chart_type": ChartType.BAR.value,
                            "operation": "sum" if agg_col != "id" else "count",
                            "column": agg_col,
                            "group_by": group_by_col,
                            "x_axis": group_by_col,
                            "y_axis": "value"
                        }
                    )
                )

            elif comp_type == "Table":
                # Find DB Columns to show
                target_table = plan.db_tables[0].table_name
                if "members" in page_plan.route or "customers" in page_plan.route:
                    target_table = plan.db_tables[0].table_name
                elif len(plan.db_tables) > 1:
                    target_table = plan.db_tables[1].table_name
                
                # Retrieve columns
                matching_db = next((t for t in plan.db_tables if t.table_name == target_table), plan.db_tables[0])
                
                components.append(
                    UIComponent(
                        id=f"table_{target_table}_grid",
                        type=ComponentType.TABLE,
                        title=f"{matching_db.table_name.capitalize()} Database",
                        target_api_path=f"/api/{target_table}",
                        grid_span=12,
                        props={
                            "table_name": target_table,
                            "columns": matching_db.columns,
                            "actions": ["edit", "delete"]
                        }
                    )
                )

            elif comp_type == "Form":
                target_table = plan.db_tables[0].table_name
                if "members" in page_plan.route or "customers" in page_plan.route:
                    target_table = plan.db_tables[0].table_name
                elif len(plan.db_tables) > 1:
                    target_table = plan.db_tables[1].table_name
                
                matching_db = next((t for t in plan.db_tables if t.table_name == target_table), plan.db_tables[0])
                
                fields = []
                for c in matching_db.columns:
                    if c == "id":
                        continue
                    ftype = "text"
                    if "email" in c:
                        ftype = "email"
                    elif "value" in c or "amount" in c or "rating" in c:
                        ftype = "number"
                    elif "date" in c:
                        ftype = "date"
                        
                    fields.append({
                        "name": c,
                        "label": c.replace("_", " ").capitalize(),
                        "type": ftype,
                        "required": True
                    })
                
                components.append(
                    UIComponent(
                        id=f"form_{target_table}_create",
                        type=ComponentType.FORM,
                        title=f"Add New {matching_db.table_name.rstrip('s').capitalize()}",
                        target_api_path=f"/api/{target_table}",
                        grid_span=12,
                        props={
                            "table_name": target_table,
                            "fields": fields
                        }
                    )
                )

            elif comp_type == "PremiumGate":
                components.append(
                    UIComponent(
                        id="premium_payment_wall",
                        type=ComponentType.PREMIUM_GATE,
                        title="Billing & Gated Analytics",
                        grid_span=12,
                        props={
                            "feature_name": "billing_telemetry",
                            "upgrade_message": "Unlock Unlimited Metrics & Enterprise Scale Integrations."
                        }
                    )
                )

        pages.append(
            UIPage(
                route=page_plan.route,
                title=page_plan.title,
                required_role="admin" if "members" in page_plan.route or "subscriptions" in page_plan.route else None,
                is_premium_gated=True if "subscriptions" in page_plan.route else False,
                components=components
            )
        )

    return UISchemaSpec(nav_items=nav_items, pages=pages)
