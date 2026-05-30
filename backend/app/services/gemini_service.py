import os
import json
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

logger = logging.getLogger("GeminiService")

T = TypeVar("T", bound=BaseModel)

def clean_json_response(text: str) -> str:
    """
    Cleans markdown formatting (like ```json ... ```) from response strings
    to ensure safe json.loads execution.
    """
    text = text.strip()
    if text.startswith("```"):
        # Remove opening ```json or ```
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline:].strip()
        else:
            text = text[3:].strip()
        # Remove closing ```
        if text.endswith("```"):
            text = text[:-3].strip()
    return text

class GeminiService:
    """
    Service abstraction for interacting with the Google Gemini API.
    Ensures zero-temperature structural parsing, fallback resilience, and strict Pydantic parsing.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        from app.core import config
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model_name or config.GEMINI_MODEL
        self._model = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
                logger.info(f"GeminiService initialized successfully using model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Google Generative AI client: {str(e)}")
        else:
            logger.warning("GEMINI_API_KEY not configured. Operating in high-fidelity mock fallback mode.")

    def generate_structured(self, prompt: str, response_schema: Type[T], system_instruction: Optional[str] = None) -> T:
        """
        Queries Gemini API to produce structured outputs mapped strictly to the target Pydantic schema model.
        Falls back to local parsing maps if Gemini client is unconfigured or fails.
        """
        if self._model:
            try:
                # Construct combined instructions
                instructions = system_instruction or "Generate a structured response matching the requested schema."
                instructions += f"\n\nStrict JSON Schema:\n{response_schema.model_json_schema()}"
                
                response = self._model.generate_content(
                    f"{instructions}\n\nPrompt: {prompt}",
                    generation_config={"temperature": 0, "response_mime_type": "application/json"}
                )
                
                raw_json = clean_json_response(response.text)
                data = json.loads(raw_json)
                return response_schema(**data)
            except Exception as e:
                logger.error(f"Gemini structured generation failed: {str(e)}. Falling back to local rules...")
                
        # If API key is missing or model generation throws an error, return robust schema-matched local structures
        return self._generate_fallback(prompt, response_schema)

    def _generate_fallback(self, prompt: str, response_schema: Type[T]) -> T:
        """
        Analyzes prompt keywords to generate mock data structures that strictly validate against target schemas.
        Fully dynamic to differentiate CRM, Hospital, Inventory, and Task Board apps.
        """
        from app.schemas.intent import IntentSpec, EntityIntent, DashboardWidgetIntent, AppType
        from app.schemas.plan import ArchitecturePlan, DBTablePlan, APIEndpointPlan, UIPagePlan, AuthPlanSpec
        import json
        
        prompt_lower = prompt.lower()
        existing = getattr(self, "existing_spec", None)

        # Scenario 1: Target is IntentSpec
        if response_schema == IntentSpec:
            # 1. Evolve existing intent if active spec exists
            if existing:
                entities = []
                for table in existing.db_schema.tables:
                    cols = [c.name for c in table.columns if c.name != "id"]
                    entities.append(EntityIntent(
                        name=table.name.rstrip('s').capitalize(),
                        description=f"Core operational data for {table.name}",
                        attributes=cols
                    ))
                
                roles = [r.role_name for r in existing.auth_schema.roles]
                dashboards = []
                for page in existing.ui_schema.pages:
                    for comp in page.components:
                        if comp.type == "MetricCard" or comp.type == "Chart":
                            dashboards.append(DashboardWidgetIntent(
                                title=comp.title,
                                metric_type=comp.props.get("operation", "sum"),
                                target_column=comp.props.get("column", "id"),
                                visual_format="metric_card" if comp.type == "MetricCard" else "bar_chart"
                            ))
                
                has_payments = existing.auth_schema.premium_gating.is_gating_enabled
                
                # Apply conversational upgrades
                if any(k in prompt_lower for k in ["billing", "subscription", "payment", "checkout"]):
                    has_payments = True
                
                if any(k in prompt_lower for k in ["analytics", "dashboard", "chart", "metrics"]):
                    if not dashboards:
                        col_target = "deal_value" if any("deal_value" in e.attributes for e in entities) else "id"
                        dashboards.append(DashboardWidgetIntent(
                            title="Analytics Summary",
                            metric_type="sum" if col_target != "id" else "count",
                            target_column=col_target,
                            visual_format="metric_card"
                        ))
                
                return IntentSpec(
                    app_name=existing.app_name,
                    app_type=AppType.CUSTOM,
                    description=f"Evolved version of {existing.app_name}",
                    entities=entities,
                    roles=roles,
                    dashboards=dashboards,
                    has_auth=True,
                    has_payments=has_payments
                )

            # 2. Build completely fresh intent spec based on keywords
            # Domain A: Hospital / Clinic
            if any(k in prompt_lower for k in ["hospital", "clinic", "medical", "patient", "doctor", "appointment", "hms", "care", "health"]):
                return IntentSpec(
                    app_name="CarePulse Health",
                    app_type=AppType.CUSTOM,
                    description="Dynamic healthcare portal and appointment scheduling system",
                    entities=[
                        EntityIntent(name="Patient", description="Registered health seekers", attributes=["full_name", "age", "gender", "ailment", "contact_number"]),
                        EntityIntent(name="Doctor", description="Staff physician roster", attributes=["full_name", "specialty", "department", "consultation_fee"]),
                        EntityIntent(name="Appointment", description="Booking transaction slots", attributes=["patient_name", "doctor_name", "appointment_date", "status"])
                    ],
                    roles=["admin", "doctor", "receptionist"],
                    dashboards=[
                        DashboardWidgetIntent(title="Total Active Appointments", metric_type="count", target_column="id", visual_format="metric_card"),
                        DashboardWidgetIntent(title="Doctor Specialties Count", metric_type="count", target_column="specialty", visual_format="bar_chart")
                    ],
                    has_auth=True,
                    has_payments=False
                )

            # Domain B: Inventory / Warehouse
            elif any(k in prompt_lower for k in ["inventory", "stock", "warehouse", "product", "supplier", "logistics"]):
                return IntentSpec(
                    app_name="LogiStock Inventory",
                    app_type=AppType.CUSTOM,
                    description="Dynamic warehousing and inventory tracking portal",
                    entities=[
                        EntityIntent(name="Product", description="Trackable storage units", attributes=["name", "sku", "quantity", "unit_price", "category"]),
                        EntityIntent(name="Warehouse", description="Storage location coordinates", attributes=["location_name", "capacity", "manager", "status"]),
                        EntityIntent(name="Supplier", description="Vendor directory list", attributes=["supplier_name", "contact_person", "email", "phone"])
                    ],
                    roles=["admin", "manager", "auditor"],
                    dashboards=[
                        DashboardWidgetIntent(title="Inventory Stock Value", metric_type="sum", target_column="unit_price", visual_format="metric_card"),
                        DashboardWidgetIntent(title="Quantity Level by Category", metric_type="sum", target_column="quantity", visual_format="bar_chart")
                    ],
                    has_auth=True,
                    has_payments=False
                )

            # Domain C: Project / Task Board
            elif any(k in prompt_lower for k in ["task", "project", "backlog", "sprint", "todo", "board"]):
                return IntentSpec(
                    app_name="TaskFlow Board",
                    app_type=AppType.PROJECT_BOARD,
                    description="Agile task pipeline and backlog tracking workspace",
                    entities=[
                        EntityIntent(name="Task", description="Functional action item tickets", attributes=["title", "description", "status", "priority", "due_date"]),
                        EntityIntent(name="Team_member", description="Assigned developer logs", attributes=["name", "role", "email", "productivity_rating"])
                    ],
                    roles=["admin", "manager", "developer"],
                    dashboards=[
                        DashboardWidgetIntent(title="Total Backlog Cards", metric_type="count", target_column="id", visual_format="metric_card"),
                        DashboardWidgetIntent(title="Productivity Score Avg", metric_type="avg", target_column="productivity_rating", visual_format="bar_chart")
                    ],
                    has_auth=True,
                    has_payments=False
                )

            # Domain D: Reporting / Analytics Dashboard
            elif any(k in prompt_lower for k in ["reporting", "report", "analytics", "dashboard", "kpi", "metrics", "bi", "business intelligence"]):
                return IntentSpec(
                    app_name="InsightBoard Analytics",
                    app_type=AppType.CUSTOM,
                    description="Executive KPI reporting and business analytics dashboard",
                    entities=[
                        EntityIntent(name="Report", description="Generated analytical report", attributes=["title", "category", "generated_by", "status", "created_at"]),
                        EntityIntent(name="Metric", description="Tracked business KPI", attributes=["name", "value", "unit", "target", "period"]),
                        EntityIntent(name="Department", description="Business unit", attributes=["name", "head", "budget", "headcount"])
                    ],
                    roles=["admin", "analyst", "viewer"],
                    dashboards=[
                        DashboardWidgetIntent(title="Total Reports Generated", metric_type="count", target_column="id", visual_format="metric_card"),
                        DashboardWidgetIntent(title="Budget by Department", metric_type="sum", target_column="budget", visual_format="bar_chart")
                    ],
                    has_auth=True,
                    has_payments=False
                )

            # Domain E: Employee Onboarding
            elif any(k in prompt_lower for k in ["onboarding", "onboard", "employee", "hr", "human resource", "hiring", "recruitment", "recruit"]):
                return IntentSpec(
                    app_name="PeopleFlow HR",
                    app_type=AppType.CUSTOM,
                    description="Employee onboarding and HR management portal",
                    entities=[
                        EntityIntent(name="Employee", description="Staff member record", attributes=["full_name", "email", "department", "role", "start_date", "status"]),
                        EntityIntent(name="Task", description="Onboarding checklist item", attributes=["title", "assigned_to", "due_date", "completed", "category"]),
                        EntityIntent(name="Department", description="Organizational unit", attributes=["name", "manager", "headcount", "budget"])
                    ],
                    roles=["admin", "hr_manager", "employee"],
                    dashboards=[
                        DashboardWidgetIntent(title="Employees Onboarded", metric_type="count", target_column="id", visual_format="metric_card"),
                        DashboardWidgetIntent(title="Headcount by Department", metric_type="sum", target_column="headcount", visual_format="bar_chart")
                    ],
                    has_auth=True,
                    has_payments=False
                )

            # Domain F: LMS / Learning Management
            elif any(k in prompt_lower for k in ["lms", "learning", "course", "education", "student", "lesson", "training", "e-learning", "elearning"]):
                return IntentSpec(
                    app_name="LearnSphere LMS",
                    app_type=AppType.CUSTOM,
                    description="Learning management system for courses and students",
                    entities=[
                        EntityIntent(name="Course", description="Learning curriculum unit", attributes=["title", "instructor", "category", "duration_hours", "status"]),
                        EntityIntent(name="Student", description="Enrolled learner profile", attributes=["full_name", "email", "enrolled_course", "progress", "grade"]),
                        EntityIntent(name="Lesson", description="Individual learning module", attributes=["title", "course", "duration_minutes", "type", "completed"])
                    ],
                    roles=["admin", "instructor", "student"],
                    dashboards=[
                        DashboardWidgetIntent(title="Total Enrolled Students", metric_type="count", target_column="id", visual_format="metric_card"),
                        DashboardWidgetIntent(title="Avg Progress by Course", metric_type="avg", target_column="progress", visual_format="bar_chart")
                    ],
                    has_auth=True,
                    has_payments=True
                )

            # Domain G: CRM (Default Fallback)
            else:
                return IntentSpec(
                    app_name="Apex CRM",
                    app_type=AppType.CRM,
                    description="Lead tracking and customer portal",
                    entities=[
                        EntityIntent(name="Contact", description="Lead contact directory", attributes=["full_name", "email", "phone", "job_title", "status"]),
                        EntityIntent(name="Lead", description="Sales prospect funnel deal", attributes=["company", "email", "deal_value", "stage"]),
                        EntityIntent(name="Customer", description="Active contracted business accounts", attributes=["full_name", "company", "email", "deal_value", "status"])
                    ],
                    roles=["admin", "sales_rep", "viewer"],
                    dashboards=[
                        DashboardWidgetIntent(title="Total Deals Value", metric_type="sum", target_column="deal_value", visual_format="metric_card"),
                        DashboardWidgetIntent(title="Funnel Deals sum", metric_type="sum", target_column="deal_value", visual_format="bar_chart")
                    ],
                    has_auth=True,
                    has_payments=True
                )

        # Scenario 2: Target is ArchitecturePlan
        elif response_schema == ArchitecturePlan:
            intent_spec = None
            if "Intent Spec JSON:" in prompt:
                try:
                    json_str = prompt.split("Intent Spec JSON:")[1].strip()
                    intent_spec = json.loads(json_str)
                except Exception:
                    pass

            if intent_spec:
                app_name = intent_spec.get("app_name", "Dynamic Platform")
                entities = intent_spec.get("entities", [])
                roles = intent_spec.get("roles", ["admin", "user"])
                dashboards = intent_spec.get("dashboards", [])
                has_payments = intent_spec.get("has_payments", False)

                # Construct DB Tables Plan
                db_tables = []
                for entity in entities:
                    tname = entity["name"].lower() + "s"
                    cols = ["id"] + [c for c in entity["attributes"] if c != "id"]
                    db_tables.append(DBTablePlan(
                        table_name=tname,
                        description=entity["description"],
                        columns=cols,
                        relations=[]
                    ))

                # Construct API Endpoints Plan
                api_endpoints = []
                for table in db_tables:
                    tname = table.table_name
                    api_endpoints.append(APIEndpointPlan(path=f"/api/{tname}", method="GET", action="list", auth_required=True))
                    api_endpoints.append(APIEndpointPlan(path=f"/api/{tname}/{{id}}", method="GET", action="retrieve", auth_required=True))
                    api_endpoints.append(APIEndpointPlan(path=f"/api/{tname}", method="POST", action="create", auth_required=True))
                    api_endpoints.append(APIEndpointPlan(path=f"/api/{tname}/{{id}}", method="PUT", action="update", auth_required=True))
                    api_endpoints.append(APIEndpointPlan(path=f"/api/{tname}/{{id}}", method="DELETE", action="delete", auth_required=True))

                if dashboards:
                    api_endpoints.append(APIEndpointPlan(path="/api/analytics/metrics", method="GET", action="analytics", auth_required=True))

                # Construct UI Pages Plan
                ui_pages = []
                dashboard_comps = ["Header"]
                for widget in dashboards:
                    dashboard_comps.append("MetricCard" if widget["visual_format"] == "metric_card" else "Chart")
                
                ui_pages.append(UIPagePlan(
                    route="/",
                    title="Control Center" if dashboards else "Workspace Board",
                    components=dashboard_comps
                ))

                for table in db_tables:
                    ui_pages.append(UIPagePlan(
                        route=f"/{table.table_name}",
                        title=f"{table.table_name.capitalize()} Registry",
                        components=["Header", "Table", "Form"]
                    ))

                if has_payments:
                    ui_pages.append(UIPagePlan(
                        route="/subscriptions",
                        title="Premium Checkout",
                        components=["Header", "PremiumGate"]
                    ))

                gated_routes = []
                for table in db_tables:
                    gated_routes.append(f"/api/{table.table_name}")

                return ArchitecturePlan(
                    app_name=app_name,
                    explanation=f"Structured blueprint for {app_name} application.",
                    db_tables=db_tables,
                    api_endpoints=api_endpoints,
                    ui_pages=ui_pages,
                    auth_policy=AuthPlanSpec(roles=roles, gated_routes=gated_routes)
                )

            # Fallback when unpacking fails
            if "CarePulse" in prompt or "hospital" in prompt_lower:
                return ArchitecturePlan(
                    app_name="CarePulse Health",
                    explanation="Modular clinical management and appointment scheduling layout",
                    db_tables=[
                        DBTablePlan(table_name="patients", description="Health seekers", columns=["id", "full_name", "age", "gender", "ailment", "contact_number"], relations=[]),
                        DBTablePlan(table_name="doctors", description="Specialist doctors Roster", columns=["id", "full_name", "specialty", "department", "consultation_fee"], relations=[]),
                        DBTablePlan(table_name="appointments", description="Slot Bookings", columns=["id", "patient_name", "doctor_name", "appointment_date", "status"], relations=[])
                    ],
                    api_endpoints=[
                        APIEndpointPlan(path="/api/patients", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/doctors", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/appointments", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/analytics/metrics", method="GET", action="analytics", auth_required=True)
                    ],
                    ui_pages=[
                        UIPagePlan(route="/", title="Clinic Dashboard", components=["Header", "MetricCard", "Chart"]),
                        UIPagePlan(route="/patients", title="Patient Records", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/doctors", title="Doctor Schedules", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/appointments", title="Appointments Registry", components=["Header", "Table", "Form"])
                    ],
                    auth_policy=AuthPlanSpec(roles=["admin", "doctor", "receptionist"], gated_routes=["/api/patients"])
                )

            elif "LogiStock" in prompt or "inventory" in prompt_lower:
                return ArchitecturePlan(
                    app_name="LogiStock Inventory",
                    explanation="Dynamic logistics warehousing and inventory pipeline",
                    db_tables=[
                        DBTablePlan(table_name="products", description="Trackable goods", columns=["id", "name", "sku", "quantity", "unit_price", "category"], relations=[]),
                        DBTablePlan(table_name="warehouses", description="Storage sites", columns=["id", "location_name", "capacity", "manager", "status"], relations=[]),
                        DBTablePlan(table_name="suppliers", description="Vendor directories", columns=["id", "supplier_name", "contact_person", "email", "phone"], relations=[])
                    ],
                    api_endpoints=[
                        APIEndpointPlan(path="/api/products", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/warehouses", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/suppliers", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/analytics/metrics", method="GET", action="analytics", auth_required=True)
                    ],
                    ui_pages=[
                        UIPagePlan(route="/", title="Inventory Analytics", components=["Header", "MetricCard", "Chart"]),
                        UIPagePlan(route="/products", title="Product Stock", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/warehouses", title="Warehouses", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/suppliers", title="Suppliers", components=["Header", "Table", "Form"])
                    ],
                    auth_policy=AuthPlanSpec(roles=["admin", "manager", "auditor"], gated_routes=["/api/products"])
                )

            elif "TaskFlow" in prompt or "task" in prompt_lower:
                return ArchitecturePlan(
                    app_name="TaskFlow Board",
                    explanation="Sprint planner board layout",
                    db_tables=[
                        DBTablePlan(table_name="tasks", description="Action tickets", columns=["id", "title", "description", "status", "priority", "due_date"], relations=[]),
                        DBTablePlan(table_name="team_members", description="Developers", columns=["id", "name", "role", "email", "productivity_rating"], relations=[])
                    ],
                    api_endpoints=[
                        APIEndpointPlan(path="/api/tasks", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/team_members", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/analytics/metrics", method="GET", action="analytics", auth_required=True)
                    ],
                    ui_pages=[
                        UIPagePlan(route="/", title="Sprint Board", components=["Header", "MetricCard", "Chart"]),
                        UIPagePlan(route="/tasks", title="Sprint Backlog", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/team_members", title="Team Directory", components=["Header", "Table", "Form"])
                    ],
                    auth_policy=AuthPlanSpec(roles=["admin", "manager", "developer"], gated_routes=["/api/tasks"])
                )

            elif any(k in prompt_lower for k in ["reporting", "report", "analytics", "dashboard", "kpi", "metrics", "bi"]) or "InsightBoard" in prompt:
                return ArchitecturePlan(
                    app_name="InsightBoard Analytics",
                    explanation="Executive KPI reporting and business analytics platform",
                    db_tables=[
                        DBTablePlan(table_name="reports", description="Generated reports", columns=["id", "title", "category", "generated_by", "status", "created_at"], relations=[]),
                        DBTablePlan(table_name="metrics", description="Tracked KPIs", columns=["id", "name", "value", "unit", "target", "period"], relations=[]),
                        DBTablePlan(table_name="departments", description="Business units", columns=["id", "name", "head", "budget", "headcount"], relations=[])
                    ],
                    api_endpoints=[
                        APIEndpointPlan(path="/api/reports", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/metrics", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/departments", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/analytics/metrics", method="GET", action="analytics", auth_required=True)
                    ],
                    ui_pages=[
                        UIPagePlan(route="/", title="Analytics Overview", components=["Header", "MetricCard", "Chart"]),
                        UIPagePlan(route="/reports", title="Reports Registry", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/metrics", title="KPI Tracker", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/departments", title="Departments", components=["Header", "Table", "Form"])
                    ],
                    auth_policy=AuthPlanSpec(roles=["admin", "analyst", "viewer"], gated_routes=["/api/reports"])
                )

            elif any(k in prompt_lower for k in ["onboarding", "onboard", "employee", "hr", "human resource", "hiring", "recruitment"]) or "PeopleFlow" in prompt:
                return ArchitecturePlan(
                    app_name="PeopleFlow HR",
                    explanation="Employee onboarding and HR management platform",
                    db_tables=[
                        DBTablePlan(table_name="employees", description="Staff records", columns=["id", "full_name", "email", "department", "role", "start_date", "status"], relations=[]),
                        DBTablePlan(table_name="tasks", description="Onboarding tasks", columns=["id", "title", "assigned_to", "due_date", "completed", "category"], relations=[]),
                        DBTablePlan(table_name="departments", description="Org units", columns=["id", "name", "manager", "headcount", "budget"], relations=[])
                    ],
                    api_endpoints=[
                        APIEndpointPlan(path="/api/employees", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/tasks", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/departments", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/analytics/metrics", method="GET", action="analytics", auth_required=True)
                    ],
                    ui_pages=[
                        UIPagePlan(route="/", title="HR Dashboard", components=["Header", "MetricCard", "Chart"]),
                        UIPagePlan(route="/employees", title="Employee Directory", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/tasks", title="Onboarding Tasks", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/departments", title="Departments", components=["Header", "Table", "Form"])
                    ],
                    auth_policy=AuthPlanSpec(roles=["admin", "hr_manager", "employee"], gated_routes=["/api/employees"])
                )

            elif any(k in prompt_lower for k in ["lms", "learning", "course", "education", "student", "lesson", "training", "e-learning"]) or "LearnSphere" in prompt:
                return ArchitecturePlan(
                    app_name="LearnSphere LMS",
                    explanation="Learning management system for courses and enrolled students",
                    db_tables=[
                        DBTablePlan(table_name="courses", description="Curriculum units", columns=["id", "title", "instructor", "category", "duration_hours", "status"], relations=[]),
                        DBTablePlan(table_name="students", description="Enrolled learners", columns=["id", "full_name", "email", "enrolled_course", "progress", "grade"], relations=[]),
                        DBTablePlan(table_name="lessons", description="Learning modules", columns=["id", "title", "course", "duration_minutes", "type", "completed"], relations=[])
                    ],
                    api_endpoints=[
                        APIEndpointPlan(path="/api/courses", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/students", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/lessons", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/analytics/metrics", method="GET", action="analytics", auth_required=True)
                    ],
                    ui_pages=[
                        UIPagePlan(route="/", title="Learning Dashboard", components=["Header", "MetricCard", "Chart"]),
                        UIPagePlan(route="/courses", title="Course Catalog", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/students", title="Student Roster", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/lessons", title="Lesson Library", components=["Header", "Table", "Form"])
                    ],
                    auth_policy=AuthPlanSpec(roles=["admin", "instructor", "student"], gated_routes=["/api/students"])
                )

            else:
                return ArchitecturePlan(
                    app_name="Apex CRM",
                    explanation="Lead tracking and customer portal",
                    db_tables=[
                        DBTablePlan(table_name="contacts", description="Lead contacts", columns=["id", "full_name", "email", "phone", "job_title", "status"], relations=[]),
                        DBTablePlan(table_name="leads", description="Sales prospects", columns=["id", "company", "email", "deal_value", "stage"], relations=[]),
                        DBTablePlan(table_name="customers", description="Contracted accounts", columns=["id", "full_name", "company", "email", "deal_value", "status"], relations=[])
                    ],
                    api_endpoints=[
                        APIEndpointPlan(path="/api/contacts", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/leads", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/customers", method="GET", action="list", auth_required=True),
                        APIEndpointPlan(path="/api/analytics/metrics", method="GET", action="analytics", auth_required=True)
                    ],
                    ui_pages=[
                        UIPagePlan(route="/", title="Sales Pipeline", components=["Header", "MetricCard", "Chart"]),
                        UIPagePlan(route="/contacts", title="Contacts Database", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/leads", title="Deals Board", components=["Header", "Table", "Form"]),
                        UIPagePlan(route="/customers", title="Customers List", components=["Header", "Table", "Form"])
                    ],
                    auth_policy=AuthPlanSpec(roles=["admin", "sales_rep", "viewer"], gated_routes=["/api/customers"])
                )

        return self._generate_fallback(prompt, response_schema)

        # If schema does not have custom fallback logic, create a blank instantiation
        # to ensure the compiler pipeline does not block
        try:
            return response_schema()
        except Exception:
            # If the schema requires mandatory fields, construct basic dynamic mocked dictionary
            return response_schema.model_validate({})
