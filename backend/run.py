import uvicorn
import os
import sys

# Ensure the backend directory is in the system path (required for Render deployment)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Expose app at module level so `uvicorn run:app` works on Render
from app.main import app  # noqa: E402

if __name__ == "__main__":
    print("Starting AI-Native Compiler Pipeline & Runtime Backend...")
    print("Local Swagger Docs available at: http://localhost:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
