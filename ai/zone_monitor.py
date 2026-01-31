"""
Zone Monitoring Module
Maxsus hududlarni kuzatish va nazorat qilish.
"""
import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import os

from utils.logger import logger


class ZoneType(Enum):
    """Hudud turlari."""
    RESTRICTED = "restricted"       # Taqiqlangan hudud
    MONITORED = "monitored"         # Kuzatiladigan hudud
    ENTRANCE = "entrance"           # Kirish joyi
    EXIT = "exit"                   # Chiqish joyi
    PARKING = "parking"             # Parking
    COUNTING = "counting"           # Sanash hududi


class AlertType(Enum):
    """Ogohlantirish turlari."""
    INTRUSION = "intrusion"         # Ruxsatsiz kirish
    LOITERING = "loitering"         # Aylanib yurish
    WRONG_WAY = "wrong_way"         # Noto'g'ri yo'nalish
    OVERCROWD = "overcrowd"         # Olomon
    OBJECT_LEFT = "object_left"     # Tashlab ketilgan ob'ekt


@dataclass
class Zone:
    """Kuzatish hududi."""
    zone_id: int
    name: str
    zone_type: ZoneType
    points: List[Tuple[int, int]]  # Poligon nuqtalari
    camera_id: int
    user_id: int
    
    # Settings
    max_people: int = 10            # Max odamlar soni
    max_time: int = 300             # Max vaqt (soniya)
    active_hours: Tuple[int, int] = (0, 24)  # Faol soatlar
    
    # Stats
    current_count: int = 0
    total_entries: int = 0
    total_exits: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Nuqta hudud ichidami."""
        return cv2.pointPolygonTest(
            np.array(self.points, dtype=np.int32), 
            point, 
            False
        ) >= 0
    
    def contains_bbox(self, bbox: Tuple[int, int, int, int]) -> bool:
        """Bbox hudud ichidami (markaziga qarab)."""
        x, y, w, h = bbox
        center = (x + w // 2, y + h // 2)
        return self.contains_point(center)
    
    def is_active(self) -> bool:
        """Hudud hozir faolmi."""
        current_hour = datetime.now().hour
        return self.active_hours[0] <= current_hour < self.active_hours[1]
    
    def to_dict(self) -> dict:
        """Dict ga o'girish."""
        return {
            'zone_id': self.zone_id,
            'name': self.name,
            'zone_type': self.zone_type.value,
            'points': self.points,
            'camera_id': self.camera_id,
            'user_id': self.user_id,
            'max_people': self.max_people,
            'max_time': self.max_time,
            'active_hours': self.active_hours,
            'current_count': self.current_count,
            'total_entries': self.total_entries,
            'total_exits': self.total_exits
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Zone':
        """Dict dan yaratish."""
        return cls(
            zone_id=data['zone_id'],
            name=data['name'],
            zone_type=ZoneType(data['zone_type']),
            points=[(p[0], p[1]) for p in data['points']],
            camera_id=data['camera_id'],
            user_id=data['user_id'],
            max_people=data.get('max_people', 10),
            max_time=data.get('max_time', 300),
            active_hours=tuple(data.get('active_hours', (0, 24))),
            current_count=data.get('current_count', 0),
            total_entries=data.get('total_entries', 0),
            total_exits=data.get('total_exits', 0)
        )


@dataclass
class ZoneEvent:
    """Hudud hodisasi."""
    event_id: int
    zone_id: int
    alert_type: AlertType
    description: str
    timestamp: datetime
    object_info: dict = field(default_factory=dict)
    screenshot_path: str = None


class ZoneMonitor:
    """Hududlarni kuzatish va nazorat qilish."""
    
    def __init__(self, data_dir: str = "data/zones"):
        self.data_dir = data_dir
        self.zones: Dict[int, Zone] = {}
        self.events: List[ZoneEvent] = []
        self.next_zone_id = 1
        self.next_event_id = 1
        
        # Object tracking per zone
        self.zone_objects: Dict[int, Dict[int, dict]] = {}  # zone_id -> {track_id: info}
        
        os.makedirs(data_dir, exist_ok=True)
        self._load_zones()
    
    def _load_zones(self):
        """Hududlarni yuklash."""
        try:
            zones_file = os.path.join(self.data_dir, "zones.json")
            if os.path.exists(zones_file):
                with open(zones_file, 'r') as f:
                    data = json.load(f)
                    for zone_data in data.get('zones', []):
                        zone = Zone.from_dict(zone_data)
                        self.zones[zone.zone_id] = zone
                    self.next_zone_id = data.get('next_id', 1)
                logger.info(f"Loaded {len(self.zones)} zones")
        except Exception as e:
            logger.error(f"Error loading zones: {e}")
    
    def _save_zones(self):
        """Hududlarni saqlash."""
        try:
            zones_file = os.path.join(self.data_dir, "zones.json")
            data = {
                'zones': [z.to_dict() for z in self.zones.values()],
                'next_id': self.next_zone_id
            }
            with open(zones_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving zones: {e}")
    
    def create_zone(self, name: str, zone_type: ZoneType,
                    points: List[Tuple[int, int]], camera_id: int,
                    user_id: int, **kwargs) -> Zone:
        """Yangi hudud yaratish."""
        zone = Zone(
            zone_id=self.next_zone_id,
            name=name,
            zone_type=zone_type,
            points=points,
            camera_id=camera_id,
            user_id=user_id,
            **kwargs
        )
        
        self.zones[zone.zone_id] = zone
        self.zone_objects[zone.zone_id] = {}
        self.next_zone_id += 1
        self._save_zones()
        
        logger.info(f"Created zone: {name} (ID: {zone.zone_id})")
        return zone
    
    def delete_zone(self, zone_id: int) -> bool:
        """Hududni o'chirish."""
        if zone_id in self.zones:
            del self.zones[zone_id]
            if zone_id in self.zone_objects:
                del self.zone_objects[zone_id]
            self._save_zones()
            return True
        return False
    
    def get_zones(self, user_id: int = None, camera_id: int = None) -> List[Zone]:
        """Hududlar ro'yxati."""
        zones = list(self.zones.values())
        if user_id:
            zones = [z for z in zones if z.user_id == user_id]
        if camera_id:
            zones = [z for z in zones if z.camera_id == camera_id]
        return zones
    
    def update_zone(self, zone_id: int, detections: List[dict],
                    tracks: List = None) -> List[ZoneEvent]:
        """Hududni yangilash va hodisalarni tekshirish."""
        events = []
        zone = self.zones.get(zone_id)
        
        if not zone or not zone.is_active():
            return events
        
        if zone_id not in self.zone_objects:
            self.zone_objects[zone_id] = {}
        
        current_time = datetime.now()
        objects_in_zone = self.zone_objects[zone_id]
        
        # Track objects in zone
        current_inside = set()
        
        for det in detections:
            bbox = det.get('bbox') or det.get('box')
            if not bbox:
                continue
            
            track_id = det.get('track_id', id(det))
            
            if zone.contains_bbox(bbox):
                current_inside.add(track_id)
                
                if track_id not in objects_in_zone:
                    # New object entered
                    objects_in_zone[track_id] = {
                        'entered_at': current_time,
                        'class': det.get('class', 'object'),
                        'bbox': bbox
                    }
                    zone.total_entries += 1
                    
                    # Check for intrusion
                    if zone.zone_type == ZoneType.RESTRICTED:
                        event = self._create_event(
                            zone, AlertType.INTRUSION,
                            f"Taqiqlangan hududga kirish: {zone.name}"
                        )
                        events.append(event)
                else:
                    # Update position
                    objects_in_zone[track_id]['bbox'] = bbox
                    
                    # Check loitering
                    entered_at = objects_in_zone[track_id]['entered_at']
                    time_in_zone = (current_time - entered_at).total_seconds()
                    
                    if time_in_zone > zone.max_time:
                        # Check if we haven't alerted for this object recently
                        if not objects_in_zone[track_id].get('loitering_alerted'):
                            event = self._create_event(
                                zone, AlertType.LOITERING,
                                f"Aylanib yurish: {zone.name} da {time_in_zone/60:.1f} daqiqa"
                            )
                            events.append(event)
                            objects_in_zone[track_id]['loitering_alerted'] = True
        
        # Check for exits
        exited = set(objects_in_zone.keys()) - current_inside
        for track_id in exited:
            del objects_in_zone[track_id]
            zone.total_exits += 1
        
        # Update current count
        zone.current_count = len(objects_in_zone)
        
        # Check overcrowding
        if zone.current_count > zone.max_people:
            event = self._create_event(
                zone, AlertType.OVERCROWD,
                f"Olomon: {zone.name} da {zone.current_count} odam ({zone.max_people} dan ko'p)"
            )
            events.append(event)
        
        return events
    
    def _create_event(self, zone: Zone, alert_type: AlertType,
                      description: str) -> ZoneEvent:
        """Yangi hodisa yaratish."""
        event = ZoneEvent(
            event_id=self.next_event_id,
            zone_id=zone.zone_id,
            alert_type=alert_type,
            description=description,
            timestamp=datetime.now()
        )
        self.events.append(event)
        self.next_event_id += 1
        
        # Keep only last 1000 events
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
        
        return event
    
    def process_frame(self, frame: np.ndarray, camera_id: int,
                      detections: List[dict]) -> Tuple[np.ndarray, List[ZoneEvent]]:
        """Frame'ni qayta ishlash va hududlarni tekshirish."""
        all_events = []
        output = frame.copy()
        
        # Get zones for this camera
        camera_zones = [z for z in self.zones.values() if z.camera_id == camera_id]
        
        for zone in camera_zones:
            # Draw zone
            output = self.draw_zone(output, zone)
            
            # Update zone
            events = self.update_zone(zone.zone_id, detections)
            all_events.extend(events)
        
        return output, all_events
    
    def draw_zone(self, frame: np.ndarray, zone: Zone) -> np.ndarray:
        """Hududni frame ustiga chizish."""
        output = frame.copy()
        points = np.array(zone.points, dtype=np.int32)
        
        # Zone colors
        colors = {
            ZoneType.RESTRICTED: (0, 0, 255),    # Red
            ZoneType.MONITORED: (0, 255, 255),   # Yellow
            ZoneType.ENTRANCE: (0, 255, 0),      # Green
            ZoneType.EXIT: (255, 0, 0),          # Blue
            ZoneType.PARKING: (255, 255, 0),     # Cyan
            ZoneType.COUNTING: (255, 0, 255),    # Magenta
        }
        
        color = colors.get(zone.zone_type, (128, 128, 128))
        
        # Draw polygon
        cv2.polylines(output, [points], True, color, 2)
        
        # Transparent fill
        overlay = output.copy()
        cv2.fillPoly(overlay, [points], color)
        cv2.addWeighted(overlay, 0.2, output, 0.8, 0, output)
        
        # Label
        if zone.points:
            x, y = zone.points[0]
            label = f"{zone.name} ({zone.current_count})"
            cv2.putText(output, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return output
    
    def get_zone_stats(self, zone_id: int) -> dict:
        """Hudud statistikasi."""
        zone = self.zones.get(zone_id)
        if not zone:
            return {}
        
        # Get events for this zone
        zone_events = [e for e in self.events if e.zone_id == zone_id]
        
        return {
            'zone_id': zone_id,
            'name': zone.name,
            'type': zone.zone_type.value,
            'current_count': zone.current_count,
            'total_entries': zone.total_entries,
            'total_exits': zone.total_exits,
            'events_count': len(zone_events),
            'is_active': zone.is_active()
        }
    
    def get_recent_events(self, hours: int = 24, zone_id: int = None,
                          user_id: int = None) -> List[ZoneEvent]:
        """Oxirgi hodisalar."""
        cutoff = datetime.now() - timedelta(hours=hours)
        events = [e for e in self.events if e.timestamp > cutoff]
        
        if zone_id:
            events = [e for e in events if e.zone_id == zone_id]
        
        if user_id:
            user_zones = {z.zone_id for z in self.zones.values() if z.user_id == user_id}
            events = [e for e in events if e.zone_id in user_zones]
        
        return sorted(events, key=lambda x: x.timestamp, reverse=True)
    
    def get_summary(self, user_id: int = None) -> dict:
        """Umumiy xulosa."""
        zones = self.get_zones(user_id)
        events = self.get_recent_events(24, user_id=user_id)
        
        return {
            'total_zones': len(zones),
            'active_zones': len([z for z in zones if z.is_active()]),
            'total_people': sum(z.current_count for z in zones),
            'events_24h': len(events),
            'intrusions': len([e for e in events if e.alert_type == AlertType.INTRUSION]),
            'loitering': len([e for e in events if e.alert_type == AlertType.LOITERING])
        }


# Global instance
zone_monitor = ZoneMonitor()
