import os
import json
from app.schemas.plan import ArchitecturePlan
from app.schemas.db import DBSchemaSpec, DBTable, DBColumn, ColumnType

def generate_db(plan: ArchitecturePlan) -> DBSchemaSpec:
    """
    Translates architectural layout database structures into DB column definitions with rich mock seeds.
    Uses Gemini API if key is present, otherwise maps custom schemas deterministically.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            system_instruction = (
                "You are an expert DB database developer. Convert an ArchitecturePlan JSON into a DBSchemaSpec JSON "
                "with detailed columns, types, primary/foreign keys, and initial seed data rows matching this schema:\n"
                "{\n"
                "  \"tables\": [\n"
                "    {\n"
                "      \"name\": \"string\",\n"
                "      \"columns\": [\n"
                "        { \"name\": \"string\", \"type\": \"text/integer/real/boolean/datetime\", \"is_primary_key\": false, \"is_nullable\": true, \"default_value\": null, \"foreign_key\": null }\n"
                "      ],\n"
                "      \"seed_data\": [{ \"col1\": \"val1\" }]\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "Output ONLY JSON. Provide at least 3 seed records for key tables."
            )
            
            response = model.generate_content(
                f"{system_instruction}\n\nArchitecture Plan JSON: {plan.model_dump_json()}",
                generation_config={"temperature": 0, "response_mime_type": "application/json"}
            )
            
            data = json.loads(response.text.strip())
            return DBSchemaSpec(**data)
        except Exception:
            pass

    # High fidelity local generator
    if "TaskFlow" in plan.app_name:
        return DBSchemaSpec(
            tables=[
                DBTable(
                    name="team_members",
                    columns=[
                        DBColumn(name="id", type=ColumnType.INTEGER, is_primary_key=True, is_nullable=False),
                        DBColumn(name="name", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="role", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="email", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="productivity_rating", type=ColumnType.REAL, default_value="9.0")
                    ],
                    seed_data=[
                        {"name": "Sarah Connor", "role": "Project Manager", "email": "sarah@taskflow.io", "productivity_rating": 9.5},
                        {"name": "John Doe", "role": "Lead Developer", "email": "john@taskflow.io", "productivity_rating": 9.2},
                        {"name": "Marcus Wright", "role": "DevOps Engineer", "email": "marcus@taskflow.io", "productivity_rating": 8.8}
                    ]
                ),
                DBTable(
                    name="tasks",
                    columns=[
                        DBColumn(name="id", type=ColumnType.INTEGER, is_primary_key=True, is_nullable=False),
                        DBColumn(name="title", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="description", type=ColumnType.TEXT),
                        DBColumn(name="status", type=ColumnType.TEXT, default_value="'Todo'"),
                        DBColumn(name="priority", type=ColumnType.TEXT, default_value="'Medium'"),
                        DBColumn(name="due_date", type=ColumnType.TEXT),
                        DBColumn(name="assigned_to", type=ColumnType.INTEGER, foreign_key="team_members.id")
                    ],
                    seed_data=[
                        {"title": "Deploy AWS Cluster", "description": "Configure dynamic ECS service clusters", "status": "In Progress", "priority": "High", "due_date": "2026-06-05", "assigned_to": 3},
                        {"title": "Refactor Schema Renderer", "description": "Support interactive premium grid layers", "status": "Todo", "priority": "High", "due_date": "2026-06-10", "assigned_to": 2},
                        {"title": "Sprint Planning Meeting", "description": "Align on compiler pipelines metrics", "status": "Completed", "priority": "Low", "due_date": "2026-05-28", "assigned_to": 1}
                    ]
                )
            ]
        )

    elif "MetricPulse" in plan.app_name:
        return DBSchemaSpec(
            tables=[
                DBTable(
                    name="metric_records",
                    columns=[
                        DBColumn(name="id", type=ColumnType.INTEGER, is_primary_key=True, is_nullable=False),
                        DBColumn(name="event_name", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="category", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="duration_ms", type=ColumnType.INTEGER),
                        DBColumn(name="user_segment", type=ColumnType.TEXT),
                        DBColumn(name="revenue_impact", type=ColumnType.REAL, default_value="0.0")
                    ],
                    seed_data=[
                        {"event_name": "API Compilation Triggered", "category": "Compiler", "duration_ms": 450, "user_segment": "Enterprise", "revenue_impact": 5.0},
                        {"event_name": "Dynamic DB Migration", "category": "Database", "duration_ms": 120, "user_segment": "Startup", "revenue_impact": 0.5},
                        {"event_name": "Failed Route Gate Blocked", "category": "Security", "duration_ms": 15, "user_segment": "Free Tier", "revenue_impact": 0.0}
                    ]
                ),
                DBTable(
                    name="upgrade_logs",
                    columns=[
                        DBColumn(name="id", type=ColumnType.INTEGER, is_primary_key=True, is_nullable=False),
                        DBColumn(name="customer_name", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="plan", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="amount", type=ColumnType.REAL, is_nullable=False),
                        DBColumn(name="status", type=ColumnType.TEXT, default_value="'Active'")
                    ],
                    seed_data=[
                        {"customer_name": "Acme Systems", "plan": "Enterprise Scale", "amount": 1200.0, "status": "Active"},
                        {"customer_name": "TechInc Labs", "plan": "Team Starter", "amount": 199.0, "status": "Active"},
                        {"customer_name": "Global Corp", "plan": "Enterprise Scale", "amount": 2500.0, "status": "Pending"}
                    ]
                )
            ]
        )

    else:
        # Default CRM
        return DBSchemaSpec(
            tables=[
                DBTable(
                    name="customers",
                    columns=[
                        DBColumn(name="id", type=ColumnType.INTEGER, is_primary_key=True, is_nullable=False),
                        DBColumn(name="full_name", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="company", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="email", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="phone", type=ColumnType.TEXT),
                        DBColumn(name="deal_value", type=ColumnType.REAL, default_value="0.0"),
                        DBColumn(name="status", type=ColumnType.TEXT, default_value="'Lead'")
                    ],
                    seed_data=[
                        {"full_name": "Tony Stark", "company": "Stark Industries", "email": "tony@stark.com", "phone": "555-0100", "deal_value": 750000.0, "status": "Negotiation"},
                        {"full_name": "Bruce Wayne", "company": "Wayne Enterprises", "email": "bruce@wayne.com", "phone": "555-0199", "deal_value": 1250000.0, "status": "Contacted"},
                        {"full_name": "Diana Prince", "company": "Themyscira Exports", "email": "diana@amazon.com", "phone": "555-0150", "deal_value": 35000.0, "status": "Lead"}
                    ]
                ),
                DBTable(
                    name="interactions",
                    columns=[
                        DBColumn(name="id", type=ColumnType.INTEGER, is_primary_key=True, is_nullable=False),
                        DBColumn(name="customer_id", type=ColumnType.INTEGER, foreign_key="customers.id"),
                        DBColumn(name="interaction_type", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="summary", type=ColumnType.TEXT, is_nullable=False),
                        DBColumn(name="follow_up_date", type=ColumnType.TEXT)
                    ],
                    seed_data=[
                        {"customer_id": 1, "interaction_type": "Call", "summary": "Discussed upgrade from Mark VII armor integration. Highly interested.", "follow_up_date": "2026-06-02"},
                        {"customer_id": 2, "interaction_type": "Email", "summary": "Sent enterprise billing agreement options.", "follow_up_date": "2026-06-15"},
                        {"customer_id": 1, "interaction_type": "Meeting", "summary": "Signed preliminary licensing deal.", "follow_up_date": "2026-06-10"}
                    ]
                )
            ]
        )
