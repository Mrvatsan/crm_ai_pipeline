import logging
from typing import Tuple, List
from app.schemas.app_spec import AppSpecification
from app.modules.intent_extractor import extract_intent
from app.modules.planner import plan_architecture
from app.modules.db_generator import generate_db
from app.modules.api_generator import generate_api
from app.modules.ui_generator import generate_ui
from app.modules.auth_generator import generate_auth
from app.modules.validator import validate_spec
from app.modules.repair_engine import repair_spec
from app.database.dynamic_db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CompilerPipeline")

def compile_application(prompt: str, max_repair_attempts: int = 3) -> Tuple[AppSpecification, List[str]]:
    """
    Compiler Pipeline:
    Natural Language -> Intent -> Plan -> Module Generation -> Validation -> Repair Loop -> Executable DB Runtime.
    Returns (CompiledAppSpecification, ValidationErrorsList).
    """
    logger.info(f"Step 1: Extracting intent from prompt: '{prompt[:60]}...'")
    intent = extract_intent(prompt)
    
    logger.info(f"Step 2: Designing architecture plan for app: '{intent.app_name}'")
    plan = plan_architecture(intent)
    
    logger.info("Step 3: Generating modular schemas (DB, API, UI, Auth)")
    db_spec = generate_db(plan)
    api_spec = generate_api(plan)
    ui_spec = generate_ui(plan)
    auth_spec = generate_auth(plan)
    
    spec = AppSpecification(
        app_name=plan.app_name,
        db_schema=db_spec,
        api_schema=api_spec,
        ui_schema=ui_spec,
        auth_schema=auth_spec
    )
    
    logger.info("Step 4: Running initial compiler static validation checks")
    errors = validate_spec(spec)
    
    # Step 5: Repair Engine loop if errors are detected
    attempt = 1
    while errors and attempt <= max_repair_attempts:
        logger.warning(f"Validation failed on compile attempt {attempt}. Starting target repair engine...")
        for err in errors:
            logger.warning(f" - [COMPILER ERROR]: {err}")
            
        spec = repair_spec(spec, errors)
        errors = validate_spec(spec)
        attempt += 1
        
    if errors:
        logger.error(f"Application compiled with remaining errors after {max_repair_attempts} repair attempts.")
    else:
        logger.info("Step 6: Application compiled successfully with 0 errors! Initializing dynamic database runtime...")
        try:
            init_db(spec.db_schema)
            logger.info("Dynamic SQLite Database successfully loaded with compiled seed dataset.")
        except Exception as e:
            logger.error(f"Failed to initialize dynamic database: {str(e)}")
            errors.append(f"DB Runtime Error: {str(e)}")
            
    return spec, errors
