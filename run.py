"""
Run script for deploying bot with health check server.
Starts both FastAPI health server and Telegram bot in parallel.
"""
import threading
import uvicorn
import sys
import os

def run_health_server():
    """Run FastAPI health check server."""
    uvicorn.run(
        "health_server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 7860)),
        log_level="warning"
    )

def run_bot():
    """Run Telegram bot."""
    from bot.main import main
    main()

if __name__ == "__main__":
    print("🚀 Starting Cam Max Bot with health server...")
    
    # Start health server in daemon thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    print("✅ Health server started")
    print(f"📡 Health endpoint: http://0.0.0.0:{os.getenv('PORT', 7860)}/health")
    
    # Run bot in main thread
    run_bot()
