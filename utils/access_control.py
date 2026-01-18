"""
Markaziy Access Control va Xavfsizlik moduli.
Barcha org_id tekshiruvlari shu yerda.
"""
from typing import Optional, Dict, Any, Tuple
from database.models import db
from utils.logger import logger
from datetime import datetime, timezone, timedelta
import pytz

# Timezone configuration
UZBEKISTAN_TZ = pytz.timezone('Asia/Tashkent')


class AccessControl:
    """Markaziy kirish nazorati."""
    
    @staticmethod
    def get_user_org(user_id: int) -> Optional[int]:
        """Get user's organization ID."""
        user = db.get_user(user_id)
        if user:
            return user.get('organization_id')
        return None
    
    @staticmethod
    def check_camera_access(user_id: int, camera_id: int) -> Tuple[bool, str]:
        """
        Check if user has access to camera.
        
        Returns:
            (has_access, message)
        """
        user = db.get_user(user_id)
        if not user:
            return False, "❌ Paydalaniwshi tabilmadi!"
        
        camera = db.get_camera(camera_id)
        if not camera:
            return False, "❌ Kamera tabilmadi!"
        
        user_org = user.get('organization_id')
        camera_org = camera.get('organization_id')
        
        if user_org != camera_org:
            logger.warning(f"Access denied: user {user_id} (org {user_org}) tried to access camera {camera_id} (org {camera_org})")
            return False, "❌ Bul kameraga kirisiwiniz joq!"
        
        return True, "OK"
    
    @staticmethod
    def check_bookmark_access(user_id: int, bookmark_id: int) -> Tuple[bool, str]:
        """Check if user owns the bookmark."""
        bookmarks = db.get_bookmarks(user_id)
        bookmark = next((b for b in bookmarks if b['id'] == bookmark_id), None)
        
        if not bookmark:
            logger.warning(f"Access denied: user {user_id} tried to access bookmark {bookmark_id}")
            return False, "❌ Bul qiziqliqlarga kirisiwiniz joq!"
        
        return True, "OK"
    
    @staticmethod
    def filter_cameras_by_org(user_id: int, cameras: list) -> list:
        """Filter cameras list to only user's organization."""
        user = db.get_user(user_id)
        if not user:
            return []
        
        user_org = user.get('organization_id')
        return [c for c in cameras if c.get('organization_id') == user_org]
    
    @staticmethod
    def get_user_cameras(user_id: int) -> list:
        """Get all cameras for user's organization."""
        user = db.get_user(user_id)
        if not user:
            return []
        
        return db.get_cameras_by_organization(user.get('organization_id')) or []
    
    @staticmethod
    def check_video_access(user_id: int, video_id: int) -> Tuple[bool, str]:
        """Check if user has access to video archive by ID."""
        user = db.get_user(user_id)
        if not user:
            return False, "❌ Paydalaniwshi tabilmadi!"
        
        # Get video and check camera ownership
        try:
            from database.v2_models import v2db
            video = v2db.get_video_by_id(video_id)
            if not video:
                return False, "❌ Video tabilmadi!"
            
            camera_id = video.get('camera_id')
            return AccessControl.check_camera_access(user_id, camera_id)
        except:
            # Fallback - deny by default
            logger.warning(f"Video access check failed for user {user_id}, video {video_id}")
            return False, "❌ Video kirisiw xatasi!"
    
    @staticmethod
    def check_detection_access(user_id: int, detection_id: int) -> Tuple[bool, str]:
        """Check if user has access to detection by ID."""
        user = db.get_user(user_id)
        if not user:
            return False, "❌ Paydalaniwshi tabilmadi!"
        
        # Get detection and check camera ownership
        try:
            detection = db.get_detection_by_id(detection_id)
            if not detection:
                return False, "❌ Detection tabilmadi!"
            
            camera_id = detection.get('camera_id')
            return AccessControl.check_camera_access(user_id, camera_id)
        except:
            logger.warning(f"Detection access check failed for user {user_id}, detection {detection_id}")
            return False, "❌ Kiriw xatasi!"
    
    @staticmethod
    def filter_results_by_org(user_id: int, results: list, camera_id_field: str = 'camera_id') -> list:
        """
        Filter any result list by user's organization.
        Works for detections, events, videos, etc.
        """
        user = db.get_user(user_id)
        if not user:
            return []
        
        user_org = user.get('organization_id')
        user_cameras = db.get_cameras_by_organization(user_org) or []
        user_camera_ids = {c['id'] for c in user_cameras}
        
        filtered = []
        for result in results:
            cam_id = result.get(camera_id_field)
            if cam_id in user_camera_ids:
                filtered.append(result)
        
        return filtered


class TimeHelper:
    """Vaqt konversiya helper - Asia/Tashkent <-> UTC."""
    
    @staticmethod
    def now_local() -> datetime:
        """Get current time in Uzbekistan timezone."""
        return datetime.now(UZBEKISTAN_TZ)
    
    @staticmethod
    def now_utc() -> datetime:
        """Get current UTC time."""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def local_to_utc(local_dt: datetime) -> datetime:
        """Convert local (Uzbekistan) datetime to UTC."""
        if local_dt.tzinfo is None:
            # Assume it's Uzbekistan time
            local_dt = UZBEKISTAN_TZ.localize(local_dt)
        return local_dt.astimezone(timezone.utc)
    
    @staticmethod
    def utc_to_local(utc_dt: datetime) -> datetime:
        """Convert UTC datetime to Uzbekistan time."""
        if utc_dt.tzinfo is None:
            utc_dt = utc_dt.replace(tzinfo=timezone.utc)
        return utc_dt.astimezone(UZBEKISTAN_TZ)
    
    @staticmethod
    def get_today_range_utc() -> Tuple[datetime, datetime]:
        """Get today's start and end in UTC (for Uzbekistan day)."""
        local_now = TimeHelper.now_local()
        local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        local_end = local_now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return TimeHelper.local_to_utc(local_start), TimeHelper.local_to_utc(local_end)
    
    @staticmethod
    def get_yesterday_range_utc() -> Tuple[datetime, datetime]:
        """Get yesterday's start and end in UTC (for Uzbekistan day)."""
        local_now = TimeHelper.now_local()
        yesterday = local_now - timedelta(days=1)
        local_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        local_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return TimeHelper.local_to_utc(local_start), TimeHelper.local_to_utc(local_end)
    
    @staticmethod
    def parse_uzbek_time_phrase(phrase: str) -> Tuple[datetime, datetime]:
        """
        Parse Uzbek time phrases to UTC datetime range.
        
        Phrases: bugun, kecha, ertalab, tushdan keyin, kechqurun
        """
        local_now = TimeHelper.now_local()
        
        phrase = phrase.lower().strip()
        
        if 'bugun' in phrase:
            start = local_now.replace(hour=0, minute=0, second=0)
            end = local_now
            
            if 'ertalab' in phrase:
                start = local_now.replace(hour=6, minute=0, second=0)
                end = local_now.replace(hour=12, minute=0, second=0)
            elif 'tushdan keyin' in phrase:
                start = local_now.replace(hour=12, minute=0, second=0)
                end = local_now.replace(hour=18, minute=0, second=0)
            elif 'kechqurun' in phrase:
                start = local_now.replace(hour=18, minute=0, second=0)
                end = local_now
                
        elif 'kecha' in phrase:
            yesterday = local_now - timedelta(days=1)
            start = yesterday.replace(hour=0, minute=0, second=0)
            end = yesterday.replace(hour=23, minute=59, second=59)
        else:
            # Default: last 24 hours
            start = local_now - timedelta(hours=24)
            end = local_now
        
        return TimeHelper.local_to_utc(start), TimeHelper.local_to_utc(end)
    
    @staticmethod
    def format_for_display(utc_dt: datetime) -> str:
        """Format UTC datetime for display in Uzbekistan time."""
        if utc_dt is None:
            return "N/A"
        local_dt = TimeHelper.utc_to_local(utc_dt)
        return local_dt.strftime('%Y-%m-%d %H:%M')


# Global instances
access_control = AccessControl()
time_helper = TimeHelper()
