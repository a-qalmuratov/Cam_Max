"""AI tracking system for persons and objects."""
import uuid
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import numpy as np
from ai.detector import detector
from database.v2_models import v2db
from utils.logger import logger

class PersonTracker:
    """Track persons across frames and cameras."""
    
    def __init__(self):
        self.active_tracks = {}  # {tracking_id: last_detection_info}
        self.next_id = 1
        
    def update(self, detections: List[dict], camera_id: int) -> List[str]:
        """
        Update tracking with new detections.
        Returns list of tracking IDs.
        """
        current_time = datetime.now()
        person_detections = [d for d in detections if d['class'] == 'person']
        
        tracking_ids = []
        
        for detection in person_detections:
            # Simple tracking: assign new ID for each person
            # TODO: Implement proper tracking algorithm (IOU matching)
            tracking_id = f"P{self.next_id:06d}"
            self.next_id += 1
            
            # Create tracking record
            v2db.create_person_track(
                tracking_id=tracking_id,
                first_seen=current_time,
                entry_camera_id=camera_id
            )
            
            tracking_ids.append(tracking_id)
            
            # Store in active tracks
            self.active_tracks[tracking_id] = {
                'last_seen': current_time,
                'camera_id': camera_id,
                'bbox': detection['bbox']
            }
        
        return tracking_ids
    
    def get_person_info(self, tracking_id: str) -> Optional[Dict]:
        """Get person tracking information."""
        return v2db.get_person_track(tracking_id)

class ObjectTracker:
    """Track objects (bags, items, etc.)."""
    
    def __init__(self):
        self.tracked_objects = {}  # {object_id: info}
        
    def update(self, detections: List[dict], camera_id: int,
               person_tracking_ids: List[str] = None) -> List[int]:
        """
        Update object tracking.
        Returns list of object track IDs.
        """
        current_time = datetime.now()
        
        # Filter non-person objects
        object_detections = [d for d in detections if d['class'] != 'person']
        
        track_ids = []
        
        for detection in object_detections:
            # Create object track
            track_id = v2db.create_object_track(
                object_type=detection['class'],
                first_detected=current_time,
                camera_id=camera_id
            )
            
            track_ids.append(track_id)
            
            # If object is near a person, associate it
            if person_tracking_ids:
                # Simple association: first person (TODO: improve with proximity)
                v2db.update_object_track(
                    track_id=track_id,
                    person_tracking_id=person_tracking_ids[0],
                    status='in_hand'
                )
        
        return track_ids

class EventDetector:
    """Detect and log events."""
    
    EVENT_TYPES = {
        'person_entry': 'Shaxs kirdi',
        'person_exit': 'Shaxs chiqdi',
        'object_pickup': 'Narsa olindi',
        'object_drop': 'Narsa qo\'yildi',
        'suspicious': 'Shubhali harakat'
    }
    
    @staticmethod
    def detect_event(detections: List[dict], camera_id: int,
                     person_ids: List[str], object_ids: List[int]) -> List[int]:
        """Detect events from current frame analysis."""
        events = []
        current_time = datetime.now()
        
        # Person entry event
        for person_id in person_ids:
            event_id = v2db.add_detection_event(
                camera_id=camera_id,
                event_type='person_entry',
                person_tracking_id=person_id,
                confidence=0.95,
                description_uzbek='Yangi shaxs kameraga kirdi'
            )
            events.append(event_id)
        
        # Object pickup event
        if person_ids and object_ids:
            for obj_id in object_ids:
                event_id = v2db.add_detection_event(
                    camera_id=camera_id,
                    event_type='object_pickup',
                    person_tracking_id=person_ids[0],
                    object_tracking_id=obj_id,
                    confidence=0.85,
                    description_uzbek='Shaxs narsani qo\'liga oldi'
                )
                events.append(event_id)
        
        return events

# Global trackers
person_tracker = PersonTracker()
object_tracker = ObjectTracker()
event_detector = EventDetector()
