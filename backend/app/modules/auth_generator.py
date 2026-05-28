import os
import json
from app.schemas.plan import ArchitecturePlan
from app.schemas.auth import AuthSchemaSpec, RolePermission, PremiumGatingConfig

def generate_auth(plan: ArchitecturePlan) -> AuthSchemaSpec:
    """
    Formulates RBAC policies mapping roles to permitted API scopes and monetization restrictions.
    Uses Gemini API if key is present, otherwise maps custom access specifications.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            system_instruction = (
                "You are an expert Security Engineer. Convert an ArchitecturePlan JSON into an AuthSchemaSpec JSON "
                "with detailed roles permissions and premium gating matching this schema:\n"
                "{\n"
                "  \"roles\": [\n"
                "    { \"role_name\": \"string\", \"description\": \"string\", \"allowed_scopes\": [\"string\"] }\n"
                "  ],\n"
                "  \"premium_gating\": {\n"
                "    \"is_gating_enabled\": false,\n"
                "    \"premium_features\": [\"string\"],\n"
                "    \"upgrade_message\": \"string\"\n"
                "  }\n"
                "}\n"
                "Output ONLY JSON."
            )
            
            response = model.generate_content(
                f"{system_instruction}\n\nArchitecture Plan JSON: {plan.model_dump_json()}",
                generation_config={"temperature": 0, "response_mime_type": "application/json"}
            )
            
            data = json.loads(response.text.strip())
            return AuthSchemaSpec(**data)
        except Exception:
            pass

    # High fidelity local dynamic generator
    roles_registry = []
    
    # 1. Admin Role (Super privileges)
    roles_registry.append(
        RolePermission(
            role_name="admin",
            description="Full control over database CRUD, settings, and team access",
            allowed_scopes=["*:read", "*:write", "*:delete", "analytics:view"]
        )
    )

    # 2. Staff / Member Role
    staff_name = plan.auth_policy.roles[1] if len(plan.auth_policy.roles) > 1 else "editor"
    roles_registry.append(
        RolePermission(
            role_name=staff_name,
            description="Standard read and write access to core data streams",
            allowed_scopes=["*:read", "*:write"]
        )
    )

    # 3. Viewer / Guest Role
    viewer_name = plan.auth_policy.roles[2] if len(plan.auth_policy.roles) > 2 else "viewer"
    roles_registry.append(
        RolePermission(
            role_name=viewer_name,
            description="ReadOnly auditing access",
            allowed_scopes=["*:read"]
        )
    )

    # Monetization setup
    has_gating = "billing" in [p.route.strip("/") for p in plan.ui_pages] or "subscriptions" in [p.route.strip("/") for p in plan.ui_pages]
    
    return AuthSchemaSpec(
        roles=roles_registry,
        premium_gating=PremiumGatingConfig(
            is_gating_enabled=has_gating,
            premium_features=["analytics", "billing_telemetry"] if has_gating else [],
            upgrade_message="This high-impact dashboard requires an Active Enterprise Subscription. Contact Sales to unlock."
        )
    )
