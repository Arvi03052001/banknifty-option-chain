#!/usr/bin/env python3
"""
Startup script for BankNifty application on Render
This script starts the web app and background services
"""

import os
import sys
import time
import threading
import subprocess
from datetime import datetime
import signal

def log_message(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def start_snapshot_service():
    """Start the snapshot service in background"""
    try:
        log_message("Starting snapshot service...")
        # Import and run snapshot service
        import snapshot_service
        snapshot_service.main()
    except Exception as e:
        log_message(f"Snapshot service error: {e}")
        # Restart after 30 seconds
        time.sleep(30)
        start_snapshot_service()

def start_csv_backup_service():
    """Start the CSV backup service in background"""
    try:
        log_message("Starting CSV backup service...")
        # Import and run CSV backup service
        import csv_backup_service
        csv_backup_service.main()
    except Exception as e:
        log_message(f"CSV backup service error: {e}")
        # Restart after 60 seconds
        time.sleep(60)
        start_csv_backup_service()

def start_web_app():
    """Start the main web application"""
    try:
        log_message("Starting web application...")
        # Import and run web app
        import web_app
        port = int(os.environ.get('PORT', 5000))
        web_app.app.run(debug=False, host='0.0.0.0', port=port)
    except Exception as e:
        log_message(f"Web app error: {e}")
        sys.exit(1)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    log_message("Received shutdown signal, stopping services...")
    sys.exit(0)

def main():
    """Main startup function"""
    log_message("BankNifty Application Starting...")
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check if we're in production (Render sets this)
    is_production = os.environ.get('RENDER') is not None
    
    if is_production:
        log_message("Running in production mode on Render")
        
        # Start snapshot service in background thread
        snapshot_thread = threading.Thread(target=start_snapshot_service, daemon=True)
        snapshot_thread.start()
        log_message("Snapshot service started in background")
        
        # Start CSV backup service in background thread
        csv_backup_thread = threading.Thread(target=start_csv_backup_service, daemon=True)
        csv_backup_thread.start()
        log_message("CSV backup service started in background")
        
        # Give services time to initialize
        time.sleep(10)
    else:
        log_message("Running in development mode")
    
    # Start web application (this blocks)
    start_web_app()

if __name__ == "__main__":
    main()