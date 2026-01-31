"""Universal RTSP camera client."""
import cv2
import time
from typing import Optional, Tuple
from utils.logger import logger
from utils.config import DEFAULT_TIMEOUT, get_rtsp_url

class RTSPCamera:
    """Universal RTSP camera handler."""
    
    def __init__(self, camera_id: int, name: str, ip: str, port: int,
                 username: str, password: str, camera_type: str = 'generic'):
        """Initialize RTSP camera."""
        self.camera_id = camera_id
        self.name = name
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.camera_type = camera_type
        
        # Generate RTSP URL
        self.rtsp_url = get_rtsp_url(camera_type, ip, port, username, password)
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_connected = False
        
        logger.info(f"RTSP Camera initialized: {name} ({ip}:{port})")
    
    def connect(self) -> bool:
        """Connect to camera stream."""
        try:
            logger.info(f"Connecting to camera '{self.name}' at {self.ip}...")
            
            # Try to open video capture
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            # Set timeout
            self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, DEFAULT_TIMEOUT * 1000)
            
            # Check if opened successfully
            if self.cap.isOpened():
                # Try to read a frame to verify
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.is_connected = True
                    logger.info(f"✅ Successfully connected to camera '{self.name}'")
                    return True
            
            logger.error(f"❌ Failed to connect to camera '{self.name}'")
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to camera '{self.name}': {e}")
            return False
    
    def read_frame(self) -> Optional[Tuple[bool, any]]:
        """Read a frame from camera."""
        if not self.is_connected or self.cap is None:
            return None
        
        try:
            ret, frame = self.cap.read()
            return (ret, frame) if ret else None
        except Exception as e:
            logger.error(f"Error reading frame from '{self.name}': {e}")
            return None
    
    def get_frame(self) -> Optional[any]:
        """Get current frame from camera."""
        result = self.read_frame()
        if result:
            ret, frame = result
            return frame if ret else None
        return None
    
    def disconnect(self):
        """Disconnect from camera."""
        if self.cap is not None:
            self.cap.release()
            self.is_connected = False
            logger.info(f"Disconnected from camera '{self.name}'")
    
    def reconnect(self) -> bool:
        """Reconnect to camera."""
        self.disconnect()
        time.sleep(1)
        return self.connect()
    
    def get_info(self) -> dict:
        """Get camera information."""
        info = {
            'id': self.camera_id,
            'name': self.name,
            'ip': self.ip,
            'port': self.port,
            'type': self.camera_type,
            'status': 'connected' if self.is_connected else 'disconnected'
        }
        
        if self.is_connected and self.cap is not None:
            try:
                info['width'] = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                info['height'] = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                info['fps'] = int(self.cap.get(cv2.CAP_PROP_FPS))
            except:
                pass
        
        return info
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test camera connection and return status message."""
        if self.connect():
            frame = self.get_frame()
            if frame is not None:
                info = self.get_info()
                message = (
                    f"✅ '{self.name}' kamerasi muvaffaqiyatli ulandi!\n"
                    f"📹 Kamera turi: {self.camera_type.title()}\n"
                    f"📊 Razmer: {info.get('width', 'N/A')}x{info.get('height', 'N/A')}\n"
                    f"🎬 FPS: {info.get('fps', 'N/A')}"
                )
                return True, message
            else:
                return False, f"❌ '{self.name}' kamerasidan video olib bo'lmadi"
        else:
            return False, (
                f"❌ '{self.name}' kamerasiga ulanib bo'lmadi\n\n"
                f"Iltimos tekshiring:\n"
                f"• IP manzil to'g'ri: {self.ip}\n"
                f"• Port to'g'ri: {self.port}\n"
                f"• Login/parol to'g'ri\n"
                f"• Kamera tarmoqda ishlayapti"
            )
    
    def __del__(self):
        """Cleanup on deletion."""
        self.disconnect()


def detect_camera_type(ip: str, username: str, password: str) -> str:
    """
    Try to detect camera type by testing different RTSP URL formats.
    Returns detected camera type or 'generic'.
    """
    from utils.config import CAMERA_RTSP_FORMATS
    
    test_types = ['hikvision', 'dahua', 'tp-link', 'xiaomi', 'generic']
    
    for cam_type in test_types:
        try:
            rtsp_url = get_rtsp_url(cam_type, ip, 554, username, password)
            cap = cv2.VideoCapture(rtsp_url)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)  # 3 second timeout
            
            if cap.isOpened():
                ret, _ = cap.read()
                cap.release()
                if ret:
                    logger.info(f"Detected camera type: {cam_type}")
                    return cam_type
        except:
            continue
    
    logger.warning("Could not detect camera type, using generic")
    return 'generic'
