#!/usr/bin/env python3
"""
Unified startup script for AI Chatbot
Starts both backend and frontend servers
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Process tracking
processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down servers...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception:
            pass
    sys.exit(0)

def check_requirements():
    """Check if required files and directories exist"""
    if not BACKEND_DIR.exists():
        print("Error: Backend directory not found!")
        return False
    
    if not FRONTEND_DIR.exists():
        print("Error: Frontend directory not found!")
        return False
    
    if not (PROJECT_ROOT / ".env").exists():
        print("Warning: .env file not found. Make sure to configure environment variables.")
    
    return True

def start_backend():
    """Start the backend server"""
    print("Starting backend server...")
    
    # Change to project root for backend
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    
    try:
        # Try to start with uvicorn directly
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=PROJECT_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        processes.append(process)
        
        # Monitor backend output in a separate thread
        def monitor_backend():
            for line in process.stdout:
                print(f"[BACKEND] {line.strip()}")
        
        backend_thread = threading.Thread(target=monitor_backend, daemon=True)
        backend_thread.start()
        
        return process
        
    except Exception as e:
        print(f"Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend development server"""
    print("Starting frontend server...")
    
    try:
        # Check if node_modules exists
        if not (FRONTEND_DIR / "node_modules").exists():
            print("Installing frontend dependencies...")
            install_process = subprocess.run(
                ["npm", "install"],
                cwd=FRONTEND_DIR,
                capture_output=True,
                text=True
            )
            if install_process.returncode != 0:
                print(f"Failed to install dependencies: {install_process.stderr}")
                return None
        
        # Start the frontend server
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        processes.append(process)
        
        # Monitor frontend output in a separate thread
        def monitor_frontend():
            for line in process.stdout:
                print(f"[FRONTEND] {line.strip()}")
        
        frontend_thread = threading.Thread(target=monitor_frontend, daemon=True)
        frontend_thread.start()
        
        return process
        
    except Exception as e:
        print(f"Failed to start frontend: {e}")
        return None

def main():
    """Main function to start both servers"""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("AI Chatbot - Unified Startup Script")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Start backend server
    backend_process = start_backend()
    if not backend_process:
        print("Failed to start backend server!")
        sys.exit(1)
    
    # Wait a moment for backend to start
    print("Waiting for backend to initialize...")
    time.sleep(3)
    
    # Start frontend server
    frontend_process = start_frontend()
    if not frontend_process:
        print("Failed to start frontend server!")
        # Kill backend if frontend fails
        backend_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("Both servers are starting up!")
    print("Backend:  http://localhost:8000")
    print("Frontend: http://localhost:3000")
    print("API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop both servers")
    print("=" * 40)
    
    # Keep the main thread alive
    try:
        while True:
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("Backend process has stopped!")
                break
            if frontend_process.poll() is not None:
                print("Frontend process has stopped!")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
