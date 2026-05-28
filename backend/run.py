import uvicorn
import os
import sys

# Ensure the parent backend directory is in the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting AI-Native Compiler Pipeline & Runtime Backend...")
    print("Local Swagger Docs available at: http://localhost:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
