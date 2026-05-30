from fastapi import FastAPI, HTTPException, Request, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import os
import json

from app.schemas.app_spec import AppSpecification
from app.core.pipeline import compile_application
from app.modules.validator import validate_spec
import app.database.dynamic_db as db

app = FastAPI(
    title="AI-Native Compiler Platform",
    description="A multi-stage compiler pipeline that translates natural language specifications into dynamic, strict APIs.",
    version="1.0.0"
)

# Enable CORS for frontend schema renderer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory cache for current active application specification
CURRENT_SPEC: Optional[AppSpecification] = None
SPEC_CACHE_FILE = os.path.join(os.path.dirname(__file__), "current_spec.json")

def load_cached_spec():
    global CURRENT_SPEC
    if os.path.exists(SPEC_CACHE_FILE):
        try:
            with open(SPEC_CACHE_FILE, "r") as f:
                data = json.load(f)
                CURRENT_SPEC = AppSpecification(**data)
                # Auto-initialize database tables in case the SQLite DB file was deleted
                db.init_db(CURRENT_SPEC.db_schema)
        except Exception:
            pass

load_cached_spec()

class CompileRequest(BaseModel):
    prompt: str = Field(..., example="Create a secure CRM with deal value metrics.")

class RepairRequest(BaseModel):
    spec: AppSpecification = Field(..., description="The current invalid/broken application specification")
    errors: List[str] = Field(..., description="The list of compile-time static analysis violations to heal")

# ==========================================
# 1. TOP-LEVEL COMPILER ENDPOINTS (User Requested)
# ==========================================

@app.post("/generate", tags=["AI App Compiler"], response_model=Dict[str, Any])
def generate_endpoint(
    req: CompileRequest,
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key"),
    x_gemini_model: Optional[str] = Header(None, alias="X-Gemini-Model")
):
    """
    Compiles natural language prompt into fully integrated, strictly validated schemas.
    """
    global CURRENT_SPEC
    try:
        spec, errors = compile_application(
            req.prompt,
            api_key=x_gemini_api_key,
            model_name=x_gemini_model,
            existing_spec=CURRENT_SPEC
        )
        CURRENT_SPEC = spec
        with open(SPEC_CACHE_FILE, "w") as f:
            f.write(spec.model_dump_json(indent=2))
        return {
            "status": "success" if not errors else "partial_success",
            "app_name": spec.app_name,
            "spec": spec,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compiler pipeline failed: {str(e)}")

@app.post("/validate", tags=["AI App Compiler"])
def validate_endpoint(spec: AppSpecification):
    """
    Statically audits the provided specification to detect structural inconsistencies.
    """
    errors = validate_spec(spec)
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

@app.post("/repair", tags=["AI App Compiler"])
def repair_endpoint(
    req: RepairRequest,
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key"),
    x_gemini_model: Optional[str] = Header(None, alias="X-Gemini-Model")
):
    """
    Triggers self-healing routine to fix compiler integration errors.
    """
    try:
        from app.modules.repair_engine import repair_spec
        repaired = repair_spec(
            req.spec,
            req.errors,
            api_key=x_gemini_api_key,
            model_name=x_gemini_model
        )
        errors = validate_spec(repaired)
        return {
            "status": "success" if not errors else "partial_success",
            "spec": repaired,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heuristic repair phase failed: {str(e)}")

# ==========================================
# 2. CONTROL API (Pipeline & Compiler Namespace)
# ==========================================

@app.post("/api/compiler/compile", tags=["Compiler Pipeline"])
def compile_app(
    req: CompileRequest,
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key"),
    x_gemini_model: Optional[str] = Header(None, alias="X-Gemini-Model")
):
    global CURRENT_SPEC
    try:
        spec, errors = compile_application(
            req.prompt,
            api_key=x_gemini_api_key,
            model_name=x_gemini_model,
            existing_spec=CURRENT_SPEC
        )
        
        # Save spec if compilation succeeded (even with errors, we want to expose it for manual tuning/repair)
        CURRENT_SPEC = spec
        with open(SPEC_CACHE_FILE, "w") as f:
            f.write(spec.model_dump_json(indent=2))
            
        return {
            "status": "success" if not errors else "partial_success",
            "app_name": spec.app_name,
            "spec": spec,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compilation pipeline failed: {str(e)}")

@app.get("/api/compiler/spec", tags=["Compiler Pipeline"])
def get_spec():
    global CURRENT_SPEC
    if not CURRENT_SPEC:
        raise HTTPException(status_code=404, detail="No active application has been compiled yet. Use /api/compiler/compile first.")
    return CURRENT_SPEC

@app.post("/api/compiler/spec", tags=["Compiler Pipeline"])
def update_spec(spec: AppSpecification):
    global CURRENT_SPEC
    errors = validate_spec(spec)
    if errors:
        return {
            "status": "failed_validation",
            "errors": errors
        }
    
    CURRENT_SPEC = spec
    with open(SPEC_CACHE_FILE, "w") as f:
        f.write(spec.model_dump_json(indent=2))
    
    # Reload DB structure with new schema definitions
    try:
        db.init_db(spec.db_schema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to migrate database structure: {str(e)}")
        
    return {
        "status": "success",
        "message": "Specification manually updated and runtime database re-synchronized successfully."
    }

@app.post("/api/compiler/validate", tags=["Compiler Pipeline"])
def validate_custom_spec(spec: AppSpecification):
    errors = validate_spec(spec)
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


# ==========================================
# 2. EXECUTABLE RUNTIME API (Dynamic CRUD Engine)
# ==========================================

@app.get("/api/runtime/analytics/metrics", tags=["Dynamic App Runtime"])
def get_analytics(
    operation: str = Query(..., description="Aggregation operation: count, sum, avg, min, max"),
    column: str = Query(..., description="Target database column to aggregate"),
    group_by: Optional[str] = Query(None, description="Optional column to group calculations by"),
    table_name: Optional[str] = Query(None, description="Target database table name to aggregate")
):
    global CURRENT_SPEC
    if not CURRENT_SPEC:
        raise HTTPException(status_code=404, detail="Application spec not initialized.")
    
    # Identify target table
    if table_name:
        target_table = table_name
    elif CURRENT_SPEC.db_schema.tables:
        target_table = CURRENT_SPEC.db_schema.tables[0].name
    else:
        raise HTTPException(status_code=400, detail="Active database schema has no tables.")
        
    try:
        results = db.aggregate_records(target_table, operation, column, group_by)
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Aggregation query failed: {str(e)}")

@app.get("/api/runtime/{table_name}", tags=["Dynamic App Runtime"])
def runtime_list(table_name: str, request: Request):
    global CURRENT_SPEC
    if not CURRENT_SPEC:
        raise HTTPException(status_code=404, detail="Application spec not initialized.")
        
    # Check if table exists in compiled schema
    valid_tables = {t.name for t in CURRENT_SPEC.db_schema.tables}
    if table_name not in valid_tables:
        raise HTTPException(status_code=404, detail=f"Dynamic table '{table_name}' does not exist in schema specification.")
        
    # Convert query parameters to dynamic database filter arguments
    params = dict(request.query_params)
    filters = {k: v for k, v in params.items() if k not in ["limit", "offset"]}
    
    try:
        records = db.list_records(table_name, filters)
        return records
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database list query failed: {str(e)}")

@app.get("/api/runtime/{table_name}/{id}", tags=["Dynamic App Runtime"])
def runtime_retrieve(table_name: str, id: int):
    global CURRENT_SPEC
    if not CURRENT_SPEC:
        raise HTTPException(status_code=404, detail="Application spec not initialized.")
        
    valid_tables = {t.name for t in CURRENT_SPEC.db_schema.tables}
    if table_name not in valid_tables:
        raise HTTPException(status_code=404, detail=f"Dynamic table '{table_name}' does not exist in schema specification.")
        
    record = db.get_record(table_name, id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record {id} not found in table '{table_name}'.")
    return record

@app.post("/api/runtime/{table_name}", tags=["Dynamic App Runtime"])
async def runtime_create(table_name: str, request: Request):
    global CURRENT_SPEC
    if not CURRENT_SPEC:
        raise HTTPException(status_code=404, detail="Application spec not initialized.")
        
    valid_tables = {t.name for t in CURRENT_SPEC.db_schema.tables}
    if table_name not in valid_tables:
        raise HTTPException(status_code=404, detail=f"Dynamic table '{table_name}' does not exist in schema specification.")
        
    try:
        body = await request.json()
        new_record = db.create_record(table_name, body)
        return new_record
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create dynamic record: {str(e)}")

@app.put("/api/runtime/{table_name}/{id}", tags=["Dynamic App Runtime"])
async def runtime_update(table_name: str, id: int, request: Request):
    global CURRENT_SPEC
    if not CURRENT_SPEC:
        raise HTTPException(status_code=404, detail="Application spec not initialized.")
        
    valid_tables = {t.name for t in CURRENT_SPEC.db_schema.tables}
    if table_name not in valid_tables:
        raise HTTPException(status_code=404, detail=f"Dynamic table '{table_name}' does not exist.")
        
    try:
        body = await request.json()
        updated_record = db.update_record(table_name, id, body)
        if not updated_record:
            raise HTTPException(status_code=404, detail=f"Record {id} not found.")
        return updated_record
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update dynamic record: {str(e)}")

@app.delete("/api/runtime/{table_name}/{id}", tags=["Dynamic App Runtime"])
def runtime_delete(table_name: str, id: int):
    global CURRENT_SPEC
    if not CURRENT_SPEC:
        raise HTTPException(status_code=404, detail="Application spec not initialized.")
        
    valid_tables = {t.name for t in CURRENT_SPEC.db_schema.tables}
    if table_name not in valid_tables:
        raise HTTPException(status_code=404, detail=f"Dynamic table '{table_name}' does not exist.")
        
    success = db.delete_record(table_name, id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Record {id} not found.")
    return {"status": "success", "message": f"Successfully deleted record {id} from '{table_name}'."}
