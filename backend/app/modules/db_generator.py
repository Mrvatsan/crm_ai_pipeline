import os
import json
from typing import Optional
from app.schemas.plan import ArchitecturePlan
from app.schemas.db import DBSchemaSpec, DBTable, DBColumn, ColumnType

def generate_db(
    plan: ArchitecturePlan,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> DBSchemaSpec:
    """
    Translates architectural layout database structures into DB column definitions with rich mock seeds.
    Uses Gemini API if key is present, otherwise maps custom schemas deterministically.
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
            
            raw_json = clean_json_response(response.text)
            data = json.loads(raw_json)
            return DBSchemaSpec(**data)
        except Exception:
            pass

    # High fidelity dynamic local DB Schema Spec builder!
    tables = []
    for table_plan in plan.db_tables:
        tname = table_plan.table_name
        columns = []
        for col_name in table_plan.columns:
            # Determine column type dynamically
            col_type = ColumnType.TEXT
            if col_name == "id":
                col_type = ColumnType.INTEGER
            elif any(k in col_name.lower() for k in ["price", "value", "amount", "revenue", "fee", "cost", "rating"]):
                col_type = ColumnType.REAL
            elif any(k in col_name.lower() for k in ["age", "quantity", "count", "assigned_to", "doctor_id", "patient_id", "product_id"]):
                col_type = ColumnType.INTEGER
            elif col_name.startswith("is_") or col_name.startswith("has_"):
                col_type = ColumnType.BOOLEAN
                
            columns.append(DBColumn(
                name=col_name,
                type=col_type,
                is_primary_key=True if col_name == "id" else False,
                is_nullable=False if col_name == "id" else True,
                default_value="0.0" if col_type == ColumnType.REAL else ("0" if col_type == ColumnType.INTEGER else None)
            ))
            
        # Build beautiful seed data dynamically based on table keywords!
        seed_data = []
        if "patient" in tname.lower():
            seed_data = [
                {"full_name": "Peter Parker", "age": 22, "gender": "Male", "ailment": "Spider Bite", "contact_number": "555-1234"},
                {"full_name": "Clark Kent", "age": 35, "gender": "Male", "ailment": "Kryptonite Poisoning", "contact_number": "555-5678"},
                {"full_name": "Selina Kyle", "age": 28, "gender": "Female", "ailment": "Cat Allergy", "contact_number": "555-9012"}
            ]
        elif "doctor" in tname.lower():
            seed_data = [
                {"full_name": "Dr. Stephen Strange", "specialty": "Neurosurgery", "department": "Neurology", "consultation_fee": 500.0},
                {"full_name": "Dr. Charles Xavier", "specialty": "Psychiatry", "department": "Mental Health", "consultation_fee": 300.0},
                {"full_name": "Dr. Harleen Quinzel", "specialty": "Clinical Psychology", "department": "Mental Health", "consultation_fee": 250.0}
            ]
        elif "appointment" in tname.lower():
            seed_data = [
                {"patient_name": "Peter Parker", "doctor_name": "Dr. Stephen Strange", "appointment_date": "2026-06-01", "status": "Confirmed"},
                {"patient_name": "Clark Kent", "doctor_name": "Dr. Charles Xavier", "appointment_date": "2026-06-02", "status": "Pending"},
                {"patient_name": "Selina Kyle", "doctor_name": "Dr. Harleen Quinzel", "appointment_date": "2026-06-03", "status": "Completed"}
            ]
        elif "product" in tname.lower():
            seed_data = [
                {"name": "Quantum Processor", "sku": "QP-9000", "quantity": 100, "unit_price": 499.99, "category": "Hardware"},
                {"name": "Vibranium Shield", "sku": "VS-001", "quantity": 5, "unit_price": 9999.99, "category": "Defense"},
                {"name": "Web Shooter Fluid", "sku": "WSF-50", "quantity": 500, "unit_price": 19.99, "category": "Consumables"}
            ]
        elif "warehouse" in tname.lower():
            seed_data = [
                {"location_name": "Silo A", "capacity": 5000, "manager": "Pepper Potts", "status": "Active"},
                {"location_name": "Vault", "capacity": 100, "manager": "Happy Hogan", "status": "Active"},
                {"location_name": "Silo B", "capacity": 10000, "manager": "Ned Leeds", "status": "Inactive"}
            ]
        elif "supplier" in tname.lower():
            seed_data = [
                {"supplier_name": "Stark Industries", "contact_person": "Pepper Potts", "email": "pepper@stark.com", "phone": "555-0100"},
                {"supplier_name": "Wakanda Design Group", "contact_person": "Shuri", "email": "shuri@wakanda.gov", "phone": "555-0111"},
                {"supplier_name": "Oscorp Corp", "contact_person": "Norman Osborn", "email": "norman@oscorp.com", "phone": "555-0222"}
            ]
        elif "task" in tname.lower():
            seed_data = [
                {"title": "Deploy AWS Cluster", "description": "Configure dynamic ECS service clusters", "status": "In Progress", "priority": "High", "due_date": "2026-06-05"},
                {"title": "Refactor Schema Renderer", "description": "Support interactive premium grid layers", "status": "Todo", "priority": "High", "due_date": "2026-06-10"},
                {"title": "Sprint Planning Meeting", "description": "Align on compiler pipelines metrics", "status": "Completed", "priority": "Low", "due_date": "2026-05-28"}
            ]
        elif "member" in tname.lower():
            seed_data = [
                {"name": "Sarah Connor", "role": "Project Manager", "email": "sarah@taskflow.io", "productivity_rating": 9.5},
                {"name": "John Doe", "role": "Lead Developer", "email": "john@taskflow.io", "productivity_rating": 9.2},
                {"name": "Marcus Wright", "role": "DevOps Engineer", "email": "marcus@taskflow.io", "productivity_rating": 8.8}
            ]
        elif "contact" in tname.lower():
            seed_data = [
                {"full_name": "Tony Stark", "email": "tony@stark.com", "phone": "555-0100", "job_title": "CEO", "status": "Active"},
                {"full_name": "Bruce Wayne", "email": "bruce@wayne.com", "phone": "555-0199", "job_title": "Owner", "status": "Active"},
                {"full_name": "Diana Prince", "email": "diana@amazon.com", "phone": "555-0150", "job_title": "Director", "status": "Inactive"}
            ]
        elif "lead" in tname.lower():
            seed_data = [
                {"company": "Stark Industries", "email": "tony@stark.com", "deal_value": 750000.0, "stage": "Proposal"},
                {"company": "Wayne Enterprises", "email": "bruce@wayne.com", "deal_value": 1250000.0, "stage": "Negotiation"},
                {"company": "Themyscira Exports", "email": "diana@amazon.com", "deal_value": 35000.0, "stage": "Contacted"}
            ]
        elif "customer" in tname.lower():
            seed_data = [
                {"full_name": "Tony Stark", "company": "Stark Industries", "email": "tony@stark.com", "deal_value": 750000.0, "status": "Active"},
                {"full_name": "Bruce Wayne", "company": "Wayne Enterprises", "email": "bruce@wayne.com", "deal_value": 1250000.0, "status": "Active"},
                {"full_name": "Diana Prince", "company": "Themyscira Exports", "email": "diana@amazon.com", "deal_value": 35000.0, "status": "Active"}
            ]
        else:
            # Generic fallback seed data generator
            row = {}
            for col in columns:
                if col.name == "id":
                    continue
                if col.type == ColumnType.REAL:
                    row[col.name] = 100.0
                elif col.type == ColumnType.INTEGER:
                    row[col.name] = 10
                elif col.type == ColumnType.BOOLEAN:
                    row[col.name] = 1
                else:
                    row[col.name] = f"Sample {col.name.capitalize()}"
            seed_data = [row] * 3

        tables.append(DBTable(
            name=tname,
            columns=columns,
            seed_data=seed_data
        ))

    return DBSchemaSpec(tables=tables)
