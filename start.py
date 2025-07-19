#!/usr/bin/env python3
"""
TechPal Startup Script
Launches both the FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'openai', 'anthropic',
        'sqlalchemy', 'pydantic', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install them with:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has API keys"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  No .env file found!")
        print("Please create one from env_example.txt:")
        print("cp env_example.txt .env")
        print("Then add your API keys to the .env file")
        return False
    
    # Check for API keys
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_openai_api_key_here' in content and 'your_anthropic_api_key_here' in content:
            print("⚠️  Please configure your API keys in the .env file")
            print("You need at least one of:")
            print("  - OPENAI_API_KEY")
            print("  - ANTHROPIC_API_KEY")
            return False
    
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting TechPal Backend...")
    try:
        # Start backend in background
        backend_process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Check if backend is running
        if backend_process.poll() is None:
            print("✅ Backend started successfully at http://localhost:8000")
            return backend_process
        else:
            stdout, stderr = backend_process.communicate()
            print("❌ Backend failed to start:")
            print(stderr.decode())
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎨 Starting TechPal Frontend...")
    try:
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for frontend to start
        time.sleep(5)
        
        # Check if frontend is running
        if frontend_process.poll() is None:
            print("✅ Frontend started successfully at http://localhost:8501")
            return frontend_process
        else:
            stdout, stderr = frontend_process.communicate()
            print("❌ Frontend failed to start:")
            print(stderr.decode())
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("=" * 50)
    print("🚀 TechPal - Educational AI Assistant")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        print("\nWould you like to continue anyway? (y/N): ", end="")
        response = input().lower().strip()
        if response != 'y':
            sys.exit(1)
    
    print("\n🔧 Starting TechPal...")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend. Exiting.")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend. Stopping backend.")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 TechPal is now running!")
    print("=" * 50)
    print("📱 Frontend: http://localhost:8501")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("\n💡 Tips:")
    print("   - Open the frontend URL in your browser")
    print("   - Select your age group in the sidebar")
    print("   - Start asking questions about technology!")
    print("   - Press Ctrl+C to stop both services")
    print("=" * 50)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
                
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down TechPal...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
            
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
            
        print("👋 Goodbye!")

if __name__ == "__main__":
    main() 