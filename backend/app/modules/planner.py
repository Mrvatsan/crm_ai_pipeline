from typing import Optional
from app.schemas.intent import IntentSpec
from app.schemas.plan import ArchitecturePlan
from app.schemas.app_spec import AppSpecification
from app.services.gemini_service import GeminiService

def plan_architecture(
    intent: IntentSpec,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    existing_spec: Optional[AppSpecification] = None
) -> ArchitecturePlan:
    """
    Formulates a comprehensive systems plan containing DB layout, API paths, pages, and auth configurations.
    Delegates to the central GeminiService abstraction.
    """
    gemini = GeminiService(api_key=api_key, model_name=model_name)
    system_instruction = (
        "You are an expert lead software architect. Convert high-level user intent JSON into an "
        "ArchitecturePlan JSON. Do not include markdown formatting."
    )
    if existing_spec:
        system_instruction += (
            f"\n\nConversational App Evolution Context:\n"
            f"You are evolving an existing application structure. Current schema is:\n"
            f"{existing_spec.model_dump_json()}\n"
            f"Integrate and map the evolved IntentSpec into a cohesive, upgraded ArchitecturePlan. "
            f"Preserve existing tables, APIs, gated routes, and pages unless specifically instructed to drop them."
        )
        gemini.existing_spec = existing_spec
        
    prompt = f"Intent Spec JSON: {intent.model_dump_json()}"
    return gemini.generate_structured(prompt, ArchitecturePlan, system_instruction)
