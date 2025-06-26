"""
Startup script to run both web app and snapshot service
"""

import subprocess
import sys
import time
import os

def start_services():
    """Start both web app and snapshot service"""
    print("Starting BankNifty Application Suite...")
    
    try:
        # Start snapshot service in background
        print("Starting snapshot service...")
        snapshot_process = subprocess.Popen([
            sys.executable, "snapshot_service.py"
        ], cwd=os.getcwd())
        
        # Give snapshot service time to start
        time.sleep(2)
        
        # Start web application
        print("Starting web application...")
        web_process = subprocess.Popen([
            sys.executable, "web_app.py"
        ], cwd=os.getcwd())
        
        print("\n" + "="*60)
        print("✅ BankNifty Application Suite Started Successfully!")
        print("="*60)
        print("🌐 Web Application: http://localhost:5000")
        print("📊 Snapshot Service: Running in background")
        print("="*60)
        print("Press Ctrl+C to stop all services")
        print("="*60 + "\n")
        
        # Wait for both processes
        try:
            web_process.wait()
        except KeyboardInterrupt:
            print("\nShutting down services...")
            
        # Cleanup
        if snapshot_process.poll() is None:
            snapshot_process.terminate()
            snapshot_process.wait()
            
        if web_process.poll() is None:
            web_process.terminate()
            web_process.wait()
            
        print("All services stopped successfully")
        
    except Exception as e:
        print(f"Error starting services: {e}")
        return False
    
    return True

if __name__ == '__main__':
    start_services()