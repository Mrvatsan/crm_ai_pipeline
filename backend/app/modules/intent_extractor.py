from typing import Optional
from app.schemas.intent import IntentSpec
from app.schemas.app_spec import AppSpecification
from app.services.gemini_service import GeminiService

def extract_intent(
    prompt: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    existing_spec: Optional[AppSpecification] = None
) -> IntentSpec:
    """
    Parses user natural language query into high-level IntentSpec.
    Delegates to the central GeminiService abstraction.
    """
    gemini = GeminiService(api_key=api_key, model_name=model_name)
    system_instruction = (
        "You are an expert compiler frontend. Parse user intent into a valid JSON matching the IntentSpec schema. "
        "Do not include Markdown block formats."
    )
    if existing_spec:
        system_instruction += (
            f"\n\nConversational App Evolution Context:\n"
            f"You are modifying/expanding an existing application structure. Current schema:\n"
            f"{existing_spec.model_dump_json()}\n"
            f"Modify and evolve the application intent spec based on the user's update request: '{prompt}'. "
            f"Do not delete existing entities or dashboards unless asked. Merge and append requested items carefully."
        )
        gemini.existing_spec = existing_spec
        
    return gemini.generate_structured(prompt, IntentSpec, system_instruction)
