"""
Multi-Object Tracking Module
Bir nechta ob'ektni kuzatish va track qilish.
"""
import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import time

from utils.logger import logger


@dataclass
class Track:
    """Bitta ob'ekt kuzatuvi."""
    track_id: int
    class_name: str
    positions: List[Tuple[int, int, int, int, datetime]] = field(default_factory=list)  # (x, y, w, h, time)
    last_seen: datetime = field(default_factory=datetime.now)
    first_seen: datetime = field(default_factory=datetime.now)
    camera_id: int = None
    is_active: bool = True
    color: Tuple[int, int, int] = (0, 255, 0)
    
    def add_position(self, bbox: tuple, timestamp: datetime = None):
        """Yangi pozitsiya qo'shish."""
        if timestamp is None:
            timestamp = datetime.now()
        x, y, w, h = bbox
        self.positions.append((x, y, w, h, timestamp))
        self.last_seen = timestamp
        
        # Keep only last 100 positions
        if len(self.positions) > 100:
            self.positions = self.positions[-100:]
    
    @property
    def center(self) -> Tuple[int, int]:
        """Oxirgi markaz koordinatasi."""
        if not self.positions:
            return (0, 0)
        x, y, w, h, _ = self.positions[-1]
        return (x + w // 2, y + h // 2)
    
    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        """Oxirgi bbox."""
        if not self.positions:
            return (0, 0, 0, 0)
        x, y, w, h, _ = self.positions[-1]
        return (x, y, w, h)
    
    @property
    def duration(self) -> float:
        """Kuzatuv davomiyligi (soniyada)."""
        if not self.positions:
            return 0
        return (self.last_seen - self.first_seen).total_seconds()
    
    @property
    def path(self) -> List[Tuple[int, int]]:
        """Harakat yo'li (markazlar)."""
        return [(x + w//2, y + h//2) for x, y, w, h, _ in self.positions]
    
    @property
    def total_distance(self) -> float:
        """Jami bosib o'tgan masofa (pikselda)."""
        if len(self.positions) < 2:
            return 0
        
        total = 0
        for i in range(1, len(self.positions)):
            x1, y1, _, _, _ = self.positions[i-1]
            x2, y2, _, _, _ = self.positions[i]
            total += np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        return total
    
    @property
    def average_speed(self) -> float:
        """O'rtacha tezlik (pixel/sekund)."""
        if self.duration == 0:
            return 0
        return self.total_distance / self.duration


class MultiObjectTracker:
    """Bir nechta ob'ektni kuzatish."""
    
    def __init__(self, max_age: int = 30, min_hits: int = 3, iou_threshold: float = 0.3):
        """
        Args:
            max_age: Track yo'qolguncha kutish (frameda)
            min_hits: Track aktiv bo'lishi uchun min deteksiya soni
            iou_threshold: IOU threshold for matching
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        
        self.tracks: Dict[int, Track] = {}
        self.next_id = 1
        self.frame_count = 0
        
        # History
        self.completed_tracks: List[Track] = []
        
        # Cross-camera tracking
        self.camera_handoffs: Dict[int, List[dict]] = defaultdict(list)
    
    def _iou(self, bbox1: tuple, bbox2: tuple) -> float:
        """Calculate Intersection over Union."""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Intersection
        xi1 = max(x1, x2)
        yi1 = max(y1, y2)
        xi2 = min(x1 + w1, x2 + w2)
        yi2 = min(y1 + h1, y2 + h2)
        
        if xi2 <= xi1 or yi2 <= yi1:
            return 0.0
        
        inter_area = (xi2 - xi1) * (yi2 - yi1)
        
        # Union
        box1_area = w1 * h1
        box2_area = w2 * h2
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
    
    def update(self, detections: List[dict], camera_id: int = None) -> List[Track]:
        """Yangi deteksiyalar bilan trackni yangilash."""
        self.frame_count += 1
        current_time = datetime.now()
        
        # Extract bboxes and classes
        det_bboxes = []
        det_classes = []
        for det in detections:
            bbox = det.get('bbox') or det.get('box')
            if bbox:
                det_bboxes.append(bbox)
                det_classes.append(det.get('class', det.get('class_name', 'object')))
        
        if not det_bboxes:
            # No detections - age existing tracks
            self._age_tracks()
            return list(self.tracks.values())
        
        # Match detections to existing tracks
        matched_tracks = set()
        matched_detections = set()
        
        for det_idx, (det_bbox, det_class) in enumerate(zip(det_bboxes, det_classes)):
            best_track_id = None
            best_iou = self.iou_threshold
            
            for track_id, track in self.tracks.items():
                if track_id in matched_tracks:
                    continue
                if track.class_name != det_class:
                    continue
                
                iou = self._iou(det_bbox, track.bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_track_id = track_id
            
            if best_track_id is not None:
                # Update existing track
                self.tracks[best_track_id].add_position(det_bbox, current_time)
                self.tracks[best_track_id].is_active = True
                self.tracks[best_track_id].camera_id = camera_id
                matched_tracks.add(best_track_id)
                matched_detections.add(det_idx)
        
        # Create new tracks for unmatched detections
        for det_idx, (det_bbox, det_class) in enumerate(zip(det_bboxes, det_classes)):
            if det_idx not in matched_detections:
                track = Track(
                    track_id=self.next_id,
                    class_name=det_class,
                    camera_id=camera_id,
                    color=self._get_random_color()
                )
                track.add_position(det_bbox, current_time)
                self.tracks[self.next_id] = track
                self.next_id += 1
        
        # Age unmatched tracks
        self._age_tracks(matched_tracks)
        
        return list(self.tracks.values())
    
    def _age_tracks(self, matched_tracks: set = None):
        """Eski tracklarni o'chirish."""
        if matched_tracks is None:
            matched_tracks = set()
        
        to_remove = []
        current_time = datetime.now()
        
        for track_id, track in self.tracks.items():
            if track_id not in matched_tracks:
                age = (current_time - track.last_seen).total_seconds()
                if age > self.max_age:
                    track.is_active = False
                    self.completed_tracks.append(track)
                    to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.tracks[track_id]
        
        # Keep only last 1000 completed tracks
        if len(self.completed_tracks) > 1000:
            self.completed_tracks = self.completed_tracks[-1000:]
    
    def _get_random_color(self) -> Tuple[int, int, int]:
        """Tasodifiy rang."""
        return (
            np.random.randint(50, 255),
            np.random.randint(50, 255),
            np.random.randint(50, 255)
        )
    
    def get_active_tracks(self, class_filter: str = None) -> List[Track]:
        """Aktiv tracklarni olish."""
        tracks = [t for t in self.tracks.values() if t.is_active]
        if class_filter:
            tracks = [t for t in tracks if t.class_name == class_filter]
        return tracks
    
    def get_track_by_id(self, track_id: int) -> Optional[Track]:
        """ID bo'yicha track olish."""
        return self.tracks.get(track_id)
    
    def draw_tracks(self, frame: np.ndarray, 
                    show_path: bool = True,
                    show_id: bool = True) -> np.ndarray:
        """Trackni frame ustiga chizish."""
        output = frame.copy()
        
        for track in self.tracks.values():
            if not track.is_active:
                continue
            
            x, y, w, h = track.bbox
            color = track.color
            
            # Draw bbox
            cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
            
            # Draw ID
            if show_id:
                label = f"ID:{track.track_id} {track.class_name}"
                cv2.putText(output, label, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw path
            if show_path and len(track.path) > 1:
                points = np.array(track.path, dtype=np.int32)
                cv2.polylines(output, [points], False, color, 2)
        
        return output
    
    def get_cross_camera_matches(self, camera1_id: int, camera2_id: int,
                                   time_window: int = 60) -> List[dict]:
        """Kameralar o'rtasidagi mos keluvchi tracklarni topish."""
        matches = []
        
        # Get tracks from both cameras
        cam1_tracks = [t for t in self.completed_tracks if t.camera_id == camera1_id]
        cam2_tracks = [t for t in self.completed_tracks if t.camera_id == camera2_id]
        
        for t1 in cam1_tracks:
            for t2 in cam2_tracks:
                # Check time proximity
                time_diff = abs((t2.first_seen - t1.last_seen).total_seconds())
                if time_diff < time_window and t1.class_name == t2.class_name:
                    matches.append({
                        'camera1_track': t1,
                        'camera2_track': t2,
                        'time_diff': time_diff,
                        'class': t1.class_name
                    })
        
        return sorted(matches, key=lambda x: x['time_diff'])
    
    def get_summary(self) -> dict:
        """Kuzatuv xulosasi."""
        active = list(self.tracks.values())
        
        by_class = defaultdict(int)
        for track in active:
            by_class[track.class_name] += 1
        
        return {
            'active_tracks': len(active),
            'total_tracked': len(self.completed_tracks) + len(active),
            'by_class': dict(by_class),
            'frame_count': self.frame_count
        }
    
    def search_track(self, class_name: str = None, 
                     min_duration: float = None,
                     camera_id: int = None) -> List[Track]:
        """Track qidirish."""
        all_tracks = list(self.tracks.values()) + self.completed_tracks
        results = []
        
        for track in all_tracks:
            if class_name and track.class_name != class_name:
                continue
            if min_duration and track.duration < min_duration:
                continue
            if camera_id and track.camera_id != camera_id:
                continue
            results.append(track)
        
        return sorted(results, key=lambda x: x.last_seen, reverse=True)


# Global instance
object_tracker = MultiObjectTracker()
