"""Bot handlers package - V3 Complete."""
from bot.handlers.registration import registration_handler
from bot.handlers.main_menu import main_menu_handler
from bot.handlers.camera_management import camera_management_handler
from bot.handlers.video_view import video_view_handler
from bot.handlers.ai_search import ai_search_handler
from bot.handlers.camera import CameraHandler
from bot.handlers.setup import SetupHandler
from bot.handlers.ai_test import ai_test_handler
from bot.handlers.query import query_handler
from bot.handlers.recording import recording_handler
from bot.handlers.settings import settings_handler
from bot.handlers.analytics import analytics_handler

__all__ = [
    'registration_handler',
    'main_menu_handler', 
    'camera_management_handler',
    'video_view_handler',
    'ai_search_handler',
    'CameraHandler',
    'SetupHandler',
    'ai_test_handler',
    'query_handler',
    'recording_handler',
    'settings_handler',
    'analytics_handler'
]
