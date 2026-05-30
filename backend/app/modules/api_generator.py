import os
import json
from typing import Optional
from app.schemas.plan import ArchitecturePlan
from app.schemas.api import APISchemaSpec, APIEndpoint, APIOperation, QueryParamSpec

def generate_api(
    plan: ArchitecturePlan,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> APISchemaSpec:
    """
    Constructs concrete backend contracts listing routes, HTTP verbs, and operational bindings.
    Uses Gemini API if key is present, otherwise maps custom contracts.
    """
    from app.services.gemini_service import clean_json_response
    from app.core import config
    
    api_key = api_key or os.environ.get("GEMINI_API_KEY") or config.GEMINI_API_KEY
    model_name = model_name or os.environ.get("GEMINI_MODEL") or config.GEMINI_MODEL or "gemini-1.5-flash"
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            
            system_instruction = (
                "You are an expert API software engineer. Convert an ArchitecturePlan JSON into an APISchemaSpec JSON "
                "with detailed endpoints matching this schema:\n"
                "{\n"
                "  \"endpoints\": [\n"
                "    {\n"
                "      \"path\": \"/api/something\",\n"
                "      \"method\": \"GET/POST/PUT/DELETE\",\n"
                "      \"operation\": \"list/retrieve/create/update/delete/analytics\",\n"
                "      \"target_table\": \"table_name\",\n"
                "      \"auth_required\": true,\n"
                "      \"allowed_roles\": [\"role1\"],\n"
                "      \"is_premium_gated\": false,\n"
                "      \"query_params\": [{ \"name\": \"name\", \"type\": \"str\", \"description\": \"desc\", \"required\": false }],\n"
                "      \"request_fields\": [\"field1\"],\n"
                "      \"response_fields\": [\"field1\"]\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "Output ONLY JSON."
            )
            
            response = model.generate_content(
                f"{system_instruction}\n\nArchitecture Plan JSON: {plan.model_dump_json()}",
                generation_config={"temperature": 0, "response_mime_type": "application/json"}
            )
            
            raw_json = clean_json_response(response.text)
            data = json.loads(raw_json)
            return APISchemaSpec(**data)
        except Exception:
            pass

    # High fidelity local dynamic generator
    endpoints = []
    for table_plan in plan.db_tables:
        tname = table_plan.table_name
        
        # 1. GET /api/{table} - LIST
        endpoints.append(
            APIEndpoint(
                path=f"/api/{tname}",
                method="GET",
                operation=APIOperation.LIST,
                target_table=tname,
                auth_required=True,
                allowed_roles=[],
                is_premium_gated=False,
                query_params=[
                    QueryParamSpec(name="limit", type="int", description="Max records to return", required=False),
                    QueryParamSpec(name="offset", type="int", description="Records to offset", required=False)
                ],
                request_fields=[],
                response_fields=["id"] + table_plan.columns
            )
        )
        
        # 2. GET /api/{table}/{id} - RETRIEVE
        endpoints.append(
            APIEndpoint(
                path=f"/api/{tname}/{{id}}",
                method="GET",
                operation=APIOperation.RETRIEVE,
                target_table=tname,
                auth_required=True,
                allowed_roles=[],
                is_premium_gated=False,
                query_params=[],
                request_fields=[],
                response_fields=["id"] + table_plan.columns
            )
        )

        # 3. POST /api/{table} - CREATE
        endpoints.append(
            APIEndpoint(
                path=f"/api/{tname}",
                method="POST",
                operation=APIOperation.CREATE,
                target_table=tname,
                auth_required=True,
                allowed_roles=plan.auth_policy.roles if tname in plan.auth_policy.gated_routes else [],
                is_premium_gated=False,
                query_params=[],
                request_fields=[c for c in table_plan.columns if c != "id"],
                response_fields=["id"] + table_plan.columns
            )
        )

        # 4. PUT /api/{table}/{id} - UPDATE
        endpoints.append(
            APIEndpoint(
                path=f"/api/{tname}/{{id}}",
                method="PUT",
                operation=APIOperation.UPDATE,
                target_table=tname,
                auth_required=True,
                allowed_roles=plan.auth_policy.roles if tname in plan.auth_policy.gated_routes else [],
                is_premium_gated=False,
                query_params=[],
                request_fields=[c for c in table_plan.columns if c != "id"],
                response_fields=["id"] + table_plan.columns
            )
        )

        # 5. DELETE /api/{table}/{id} - DELETE
        endpoints.append(
            APIEndpoint(
                path=f"/api/{tname}/{{id}}",
                method="DELETE",
                operation=APIOperation.DELETE,
                target_table=tname,
                auth_required=True,
                allowed_roles=["admin"], # Default admin gate for deletes
                is_premium_gated=False,
                query_params=[],
                request_fields=[],
                response_fields=["success", "message"]
            )
        )

    # 6. Analytics custom route
    endpoints.append(
        APIEndpoint(
            path="/api/analytics/metrics",
            method="GET",
            operation=APIOperation.ANALYTICS,
            target_table=plan.db_tables[0].table_name,
            auth_required=True,
            allowed_roles=[],
            is_premium_gated=True if "MetricPulse" in plan.app_name else False,
            query_params=[
                QueryParamSpec(name="operation", type="str", description="Aggregation: sum, count, avg", required=True),
                QueryParamSpec(name="column", type="str", description="Target column", required=True),
                QueryParamSpec(name="group_by", type="str", description="Group by column name", required=False),
                QueryParamSpec(name="table_name", type="str", description="Target table name to aggregate", required=False)
            ],
            request_fields=[],
            response_fields=["value"]
        )
    )

    return APISchemaSpec(endpoints=endpoints)
