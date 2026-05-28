from app.schemas.intent import IntentSpec
from app.services.gemini_service import GeminiService

def extract_intent(prompt: str) -> IntentSpec:
    """
    Parses user natural language query into high-level IntentSpec.
    Delegates to the central GeminiService abstraction.
    """
    gemini = GeminiService()
    system_instruction = (
        "You are an expert compiler frontend. Parse user intent into a valid JSON matching the IntentSpec schema. "
        "Do not include Markdown block formats."
    )
    return gemini.generate_structured(prompt, IntentSpec, system_instruction)
