from app.schemas.intent import IntentSpec
from app.schemas.plan import ArchitecturePlan
from app.services.gemini_service import GeminiService

def plan_architecture(intent: IntentSpec) -> ArchitecturePlan:
    """
    Formulates a comprehensive systems plan containing DB layout, API paths, pages, and auth configurations.
    Delegates to the central GeminiService abstraction.
    """
    gemini = GeminiService()
    system_instruction = (
        "You are an expert lead software architect. Convert high-level user intent JSON into an "
        "ArchitecturePlan JSON. Do not include markdown formatting."
    )
    prompt = f"Intent Spec JSON: {intent.model_dump_json()}"
    return gemini.generate_structured(prompt, ArchitecturePlan, system_instruction)
