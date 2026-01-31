"""
Anomaly Detection Module
Shubhali/anomal harakatlarni aniqlash.
"""
import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

from utils.logger import logger


class AnomalyType(Enum):
    """Anomal harakat turlari."""
    RUNNING = "running"           # Yugurish
    FALLING = "falling"           # Yiqilish
    FIGHTING = "fighting"         # Urush/janjal
    LOITERING = "loitering"       # Aylanib yurish
    INTRUSION = "intrusion"       # Ruxsatsiz kirish
    CROWD = "crowd"               # Olomon to'planishi
    ABANDONED = "abandoned"       # Tashlab ketilgan ob'ekt
    UNUSUAL_TIME = "unusual_time" # G'ayrioddiy vaqtda harakat


class AlertLevel(Enum):
    """Ogohlantirish darajasi."""
    INFO = "info"           # Ma'lumot
    WARNING = "warning"     # Ogohlantirish
    CRITICAL = "critical"   # Kritik


@dataclass
class Anomaly:
    """Anomal hodisa."""
    type: AnomalyType
    level: AlertLevel
    confidence: float
    description: str
    timestamp: datetime
    camera_id: int = None
    bbox: tuple = None
    frame: np.ndarray = None


@dataclass
class PersonTrack:
    """Odam kuzatuvi."""
    track_id: int
    positions: List[Tuple[int, int, datetime]]  # (x, y, time)
    last_seen: datetime
    speed: float = 0.0
    is_running: bool = False
    time_in_zone: float = 0.0


class AnomalyDetector:
    """Anomal harakatlarni aniqlash."""
    
    # Thresholds
    RUNNING_SPEED_THRESHOLD = 5.0  # pixels per frame
    LOITERING_TIME_THRESHOLD = 300  # seconds (5 min)
    CROWD_THRESHOLD = 5  # number of people
    FALLING_ACCELERATION = 10.0
    
    def __init__(self):
        self.tracks: Dict[int, PersonTrack] = {}
        self.alerts: List[Anomaly] = []
        self.last_frame = None
        self.motion_history = []
        
        # Zone-based detection (will be configured)
        self.restricted_zones: List[tuple] = []  # (x, y, w, h) polygons
        self.alert_callbacks = []
    
    def add_alert_callback(self, callback):
        """Alert callback qo'shish."""
        self.alert_callbacks.append(callback)
    
    def _notify_alert(self, anomaly: Anomaly):
        """Alert yuborish."""
        self.alerts.append(anomaly)
        for callback in self.alert_callbacks:
            try:
                callback(anomaly)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def update_tracks(self, detections: List[dict], camera_id: int = None):
        """Kuzatuvlarni yangilash."""
        current_time = datetime.now()
        
        for det in detections:
            if det.get('class') not in ['person', 'odam']:
                continue
            
            bbox = det.get('bbox', (0, 0, 0, 0))
            x, y, w, h = bbox
            center = (x + w // 2, y + h // 2)
            
            # Find matching track
            track_id = det.get('track_id', id(det))
            
            if track_id not in self.tracks:
                self.tracks[track_id] = PersonTrack(
                    track_id=track_id,
                    positions=[(center[0], center[1], current_time)],
                    last_seen=current_time
                )
            else:
                track = self.tracks[track_id]
                track.positions.append((center[0], center[1], current_time))
                track.last_seen = current_time
                
                # Keep only last 30 positions
                if len(track.positions) > 30:
                    track.positions = track.positions[-30:]
                
                # Calculate speed
                if len(track.positions) >= 2:
                    pos1 = track.positions[-2]
                    pos2 = track.positions[-1]
                    
                    dx = pos2[0] - pos1[0]
                    dy = pos2[1] - pos1[1]
                    dt = (pos2[2] - pos1[2]).total_seconds() or 1
                    
                    track.speed = np.sqrt(dx**2 + dy**2) / dt
                
                # Update time in zone
                track.time_in_zone = (current_time - track.positions[0][2]).total_seconds()
        
        # Clean old tracks
        self._clean_old_tracks()
    
    def _clean_old_tracks(self, max_age_seconds: int = 30):
        """Eski kuzatuvlarni tozalash."""
        current_time = datetime.now()
        old_tracks = [
            tid for tid, track in self.tracks.items()
            if (current_time - track.last_seen).total_seconds() > max_age_seconds
        ]
        for tid in old_tracks:
            del self.tracks[tid]
    
    def detect_running(self, camera_id: int = None) -> List[Anomaly]:
        """Yugurish aniqlash."""
        anomalies = []
        
        for track_id, track in self.tracks.items():
            if track.speed > self.RUNNING_SPEED_THRESHOLD:
                track.is_running = True
                
                anomaly = Anomaly(
                    type=AnomalyType.RUNNING,
                    level=AlertLevel.WARNING,
                    confidence=min(1.0, track.speed / (self.RUNNING_SPEED_THRESHOLD * 2)),
                    description=f"Yugurish aniqlandi (tezlik: {track.speed:.1f})",
                    timestamp=datetime.now(),
                    camera_id=camera_id
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def detect_falling(self, previous_poses: List[dict] = None, 
                       current_poses: List[dict] = None,
                       camera_id: int = None) -> List[Anomaly]:
        """Yiqilish aniqlash."""
        anomalies = []
        
        for track_id, track in self.tracks.items():
            if len(track.positions) < 3:
                continue
            
            # Check for sudden vertical movement
            pos_prev2 = track.positions[-3]
            pos_prev1 = track.positions[-2]
            pos_curr = track.positions[-1]
            
            # Y coordinate acceleration
            dy1 = pos_prev1[1] - pos_prev2[1]
            dy2 = pos_curr[1] - pos_prev1[1]
            acceleration = dy2 - dy1
            
            if acceleration > self.FALLING_ACCELERATION:
                anomaly = Anomaly(
                    type=AnomalyType.FALLING,
                    level=AlertLevel.CRITICAL,
                    confidence=min(1.0, acceleration / (self.FALLING_ACCELERATION * 2)),
                    description=f"Yiqilish aniqlandi!",
                    timestamp=datetime.now(),
                    camera_id=camera_id
                )
                anomalies.append(anomaly)
                self._notify_alert(anomaly)
        
        return anomalies
    
    def detect_fighting(self, camera_id: int = None) -> List[Anomaly]:
        """Urush/janjal aniqlash."""
        anomalies = []
        
        # Need multiple people close together with fast movement
        active_tracks = [t for t in self.tracks.values() 
                        if t.speed > self.RUNNING_SPEED_THRESHOLD * 0.5]
        
        if len(active_tracks) >= 2:
            # Check if they're close to each other
            for i, t1 in enumerate(active_tracks):
                for t2 in active_tracks[i+1:]:
                    if len(t1.positions) < 1 or len(t2.positions) < 1:
                        continue
                    
                    pos1 = t1.positions[-1]
                    pos2 = t2.positions[-1]
                    
                    distance = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                    
                    # Close and fast moving
                    if distance < 100 and (t1.speed + t2.speed) > self.RUNNING_SPEED_THRESHOLD:
                        anomaly = Anomaly(
                            type=AnomalyType.FIGHTING,
                            level=AlertLevel.CRITICAL,
                            confidence=0.8,
                            description="Janjal yoki urush bo'lishi mumkin!",
                            timestamp=datetime.now(),
                            camera_id=camera_id
                        )
                        anomalies.append(anomaly)
                        self._notify_alert(anomaly)
        
        return anomalies
    
    def detect_loitering(self, camera_id: int = None) -> List[Anomaly]:
        """Aylanib yurish (loitering) aniqlash."""
        anomalies = []
        
        for track_id, track in self.tracks.items():
            if track.time_in_zone > self.LOITERING_TIME_THRESHOLD:
                # Check if movement is minimal (staying in same area)
                if len(track.positions) >= 2:
                    first_pos = track.positions[0]
                    last_pos = track.positions[-1]
                    
                    total_distance = np.sqrt(
                        (last_pos[0] - first_pos[0])**2 + 
                        (last_pos[1] - first_pos[1])**2
                    )
                    
                    # Small movement over long time = loitering
                    if total_distance < 200:  # pixels
                        anomaly = Anomaly(
                            type=AnomalyType.LOITERING,
                            level=AlertLevel.WARNING,
                            confidence=min(1.0, track.time_in_zone / (self.LOITERING_TIME_THRESHOLD * 2)),
                            description=f"Aylanib yurish: {track.time_in_zone/60:.1f} daqiqa",
                            timestamp=datetime.now(),
                            camera_id=camera_id
                        )
                        anomalies.append(anomaly)
        
        return anomalies
    
    def detect_crowd(self, person_count: int, camera_id: int = None) -> List[Anomaly]:
        """Olomon to'planishi aniqlash."""
        anomalies = []
        
        if person_count >= self.CROWD_THRESHOLD:
            anomaly = Anomaly(
                type=AnomalyType.CROWD,
                level=AlertLevel.WARNING,
                confidence=min(1.0, person_count / 10),
                description=f"Olomon: {person_count} kishi to'plandi",
                timestamp=datetime.now(),
                camera_id=camera_id
            )
            anomalies.append(anomaly)
        
        return anomalies
    
    def detect_unusual_time(self, camera_id: int = None,
                            work_hours: Tuple[int, int] = (8, 22)) -> List[Anomaly]:
        """G'ayrioddiy vaqtda harakat aniqlash."""
        anomalies = []
        current_hour = datetime.now().hour
        
        if current_hour < work_hours[0] or current_hour >= work_hours[1]:
            if len(self.tracks) > 0:
                anomaly = Anomaly(
                    type=AnomalyType.UNUSUAL_TIME,
                    level=AlertLevel.WARNING,
                    confidence=0.9,
                    description=f"G'ayrioddiy vaqtda harakat ({current_hour}:00)",
                    timestamp=datetime.now(),
                    camera_id=camera_id
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def analyze_frame(self, detections: List[dict], 
                      camera_id: int = None) -> List[Anomaly]:
        """Frame'ni to'liq tahlil qilish."""
        all_anomalies = []
        
        # Update tracks
        self.update_tracks(detections, camera_id)
        
        # Run all detections
        all_anomalies.extend(self.detect_running(camera_id))
        all_anomalies.extend(self.detect_falling(camera_id=camera_id))
        all_anomalies.extend(self.detect_fighting(camera_id))
        all_anomalies.extend(self.detect_loitering(camera_id))
        
        # Count people
        person_count = sum(1 for d in detections if d.get('class') in ['person', 'odam'])
        all_anomalies.extend(self.detect_crowd(person_count, camera_id))
        
        all_anomalies.extend(self.detect_unusual_time(camera_id))
        
        return all_anomalies
    
    def get_recent_alerts(self, hours: int = 24, 
                          camera_id: int = None) -> List[Anomaly]:
        """Oxirgi alertlar."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        alerts = [a for a in self.alerts if a.timestamp > cutoff]
        
        if camera_id:
            alerts = [a for a in alerts if a.camera_id == camera_id]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_alert_summary(self, camera_id: int = None) -> dict:
        """Alert xulosasi."""
        alerts = self.get_recent_alerts(24, camera_id)
        
        summary = {
            'total': len(alerts),
            'critical': len([a for a in alerts if a.level == AlertLevel.CRITICAL]),
            'warning': len([a for a in alerts if a.level == AlertLevel.WARNING]),
            'info': len([a for a in alerts if a.level == AlertLevel.INFO]),
            'by_type': {}
        }
        
        for alert in alerts:
            type_name = alert.type.value
            summary['by_type'][type_name] = summary['by_type'].get(type_name, 0) + 1
        
        return summary


# Global instance
anomaly_detector = AnomalyDetector()
