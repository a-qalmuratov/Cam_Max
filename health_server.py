"""
Health check server for Fly.io and HuggingFace Spaces deployment.
Provides HTTP endpoint for platform health checks while bot runs in polling mode.
"""
from fastapi import FastAPI

app = FastAPI(title="Cam Max Bot Health Check")

@app.get("/health")
def health_check():
    """Health check endpoint for deployment platforms."""
    return {
        "status": "ok",
        "service": "cam_max_bot",
        "mode": "polling"
    }

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Cam Max Bot is running",
        "docs": "/docs"
    }
