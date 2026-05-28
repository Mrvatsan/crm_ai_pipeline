import os

# Base environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDn2FchAWt2BS9fWTGR9SaUcyYAKg8RM3Q")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

# SQLite dynamic database path
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "dynamic_app.db"
)
