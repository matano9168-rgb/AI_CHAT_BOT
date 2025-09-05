#!/usr/bin/env python3
"""
Startup script for the AI Chatbot backend server.
This script initializes the FastAPI application and starts the server.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def main():
    """Main startup function."""
    print("Starting AI Chatbot Backend Server...")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("Warning: .env file not found!")
        print("   Please create a .env file from env.example")
        print("   and configure your API keys and settings.")
        print()
    
    # Check if required directories exist
    chroma_dir = Path(__file__).parent / "chroma_db"
    chroma_dir.mkdir(exist_ok=True)
    
    # Start the server
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
