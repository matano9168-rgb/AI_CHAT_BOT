#!/usr/bin/env python3
"""
Simple startup script for the AI Chatbot backend server.
This script starts only the backend with minimal dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install minimal dependencies"""
    print("Installing minimal dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_minimal.txt"
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the backend server"""
    print("🚀 Starting AI Chatbot Backend Server...")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found - using default settings")
    
    # Create necessary directories
    Path("chroma_db").mkdir(exist_ok=True)
    
    # Add current directory to Python path
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], env=env)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main function"""
    print("AI Chatbot - Simple Startup")
    print("=" * 30)
    
    # Install dependencies first
    if not install_dependencies():
        print("Please install dependencies manually and try again")
        return
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()