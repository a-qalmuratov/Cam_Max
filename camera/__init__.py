"""Camera package for Cam_Max."""
from .rtsp_client import RTSPCamera, detect_camera_type
from .stream_manager import stream_manager, StreamManager

__all__ = ['RTSPCamera', 'detect_camera_type', 'stream_manager', 'StreamManager']
