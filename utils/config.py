"""Configuration management for Cam_Max bot."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Telegram Bot - safer loading (don't crash on import)
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    import warnings
    warnings.warn(
        "BOT_TOKEN not found in environment variables! "
        "Bot will not start. Create .env file from .env.example",
        UserWarning
    )

# Database
DATABASE_PATH = os.getenv('DATABASE_PATH', './data/cam_max.db')
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# AI Model Settings
YOLO_MODEL = os.getenv('YOLO_MODEL', 'yolov8n.pt')
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
MODELS_DIR = BASE_DIR / 'ai' / 'models'
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Gemini AI API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Camera Settings
DEFAULT_RTSP_PORT = 554
DEFAULT_TIMEOUT = 10  # seconds

# Logging
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Cache
CACHE_DIR = BASE_DIR / 'cache'
CACHE_DIR.mkdir(exist_ok=True)

# Supported camera brands and their RTSP URL formats
CAMERA_RTSP_FORMATS = {
    'hikvision': 'rtsp://{username}:{password}@{ip}:{port}/Streaming/Channels/101',
    'dahua': 'rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel=1&subtype=0',
    'tp-link': 'rtsp://{username}:{password}@{ip}:{port}/stream1',
    'xiaomi': 'rtsp://{username}:{password}@{ip}:{port}/stream1',
    'generic': 'rtsp://{username}:{password}@{ip}:{port}/stream',
}

# Admin user IDs (will be configured via bot)
ADMIN_IDS = []

def get_rtsp_url(camera_type: str, ip: str, port: int, username: str, password: str) -> str:
    """Generate RTSP URL based on camera type."""
    camera_type = camera_type.lower()
    
    # Try to get specific format for camera type
    rtsp_format = CAMERA_RTSP_FORMATS.get(camera_type, CAMERA_RTSP_FORMATS['generic'])
    
    return rtsp_format.format(
        username=username,
        password=password,
        ip=ip,
        port=port
    )
