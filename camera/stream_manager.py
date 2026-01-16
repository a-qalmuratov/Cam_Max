"""Camera stream manager for handling multiple cameras - Production Ready."""
from typing import Dict, Optional
from camera.rtsp_client import RTSPCamera
from database.models import db
from utils.logger import logger


class StreamManager:
    """Manage multiple camera streams."""
    
    def __init__(self):
        """Initialize stream manager."""
        self.cameras: Dict[int, RTSPCamera] = {}
        logger.info("Stream Manager initialized")
    
    def load_cameras_from_db(self):
        """Load all cameras from database and initialize them."""
        cameras_data = db.get_all_cameras()
        
        for cam_data in cameras_data:
            self.add_camera_from_data(cam_data)
        
        logger.info(f"Loaded {len(self.cameras)} cameras from database")
    
    def add_camera_from_data(self, cam_data: dict) -> Optional[RTSPCamera]:
        """Add camera from database record."""
        try:
            camera = RTSPCamera(
                camera_id=cam_data['id'],
                name=cam_data['name'],
                ip=cam_data['ip_address'],
                port=cam_data['port'],
                username=cam_data['username'],
                password=cam_data['password'],
                camera_type=cam_data.get('camera_type', 'generic')
            )
            
            self.cameras[cam_data['id']] = camera
            logger.info(f"Added camera to manager: {cam_data['name']} (ID: {cam_data['id']})")
            return camera
        except Exception as e:
            logger.error(f"Error adding camera {cam_data.get('name', 'unknown')}: {e}")
            return None
    
    def add_camera(self, camera_id: int, name: str = None, ip: str = None, 
                   port: int = 554, username: str = 'admin', password: str = '',
                   camera_type: str = 'generic', rtsp_url: str = None) -> Optional[RTSPCamera]:
        """Add a camera to the manager."""
        
        # If only camera_id provided, load from database
        if name is None:
            cam_data = db.get_camera(camera_id)
            if cam_data:
                return self.add_camera_from_data(cam_data)
            else:
                logger.error(f"Camera {camera_id} not found in database")
                return None
        
        camera = RTSPCamera(
            camera_id=camera_id,
            name=name,
            ip=ip,
            port=port,
            username=username,
            password=password,
            camera_type=camera_type
        )
        
        # Override RTSP URL if provided
        if rtsp_url:
            camera.rtsp_url = rtsp_url
        
        self.cameras[camera_id] = camera
        logger.info(f"Added camera to manager: {name} (ID: {camera_id})")
        return camera
    
    def get_camera(self, camera_id: int) -> Optional[RTSPCamera]:
        """Get camera by ID. Loads from DB if not in memory."""
        if camera_id not in self.cameras:
            # Try to load from database
            cam_data = db.get_camera(camera_id)
            if cam_data:
                self.add_camera_from_data(cam_data)
        
        return self.cameras.get(camera_id)
    
    def get_or_connect_camera(self, camera_id: int) -> Optional[RTSPCamera]:
        """Get camera and ensure it's connected."""
        camera = self.get_camera(camera_id)
        
        if camera is None:
            return None
        
        if not camera.is_connected:
            camera.connect()
        
        return camera
    
    def remove_camera(self, camera_id: int):
        """Remove camera from manager."""
        if camera_id in self.cameras:
            self.cameras[camera_id].disconnect()
            del self.cameras[camera_id]
            logger.info(f"Removed camera ID: {camera_id}")
    
    def connect_all(self):
        """Connect to all cameras."""
        for camera in self.cameras.values():
            camera.connect()
    
    def disconnect_all(self):
        """Disconnect from all cameras."""
        for camera in self.cameras.values():
            camera.disconnect()
    
    def get_all_camera_info(self) -> list:
        """Get info for all cameras."""
        return [camera.get_info() for camera in self.cameras.values()]
    
    def test_camera_connection(self, camera_id: int) -> tuple:
        """Test camera connection and return (success, message)."""
        camera = self.get_camera(camera_id)
        
        if camera is None:
            return False, "Kamera topilmadi"
        
        return camera.test_connection()
    
    def cleanup(self):
        """Cleanup all cameras."""
        self.disconnect_all()
        self.cameras.clear()


# Global stream manager instance
stream_manager = StreamManager()
