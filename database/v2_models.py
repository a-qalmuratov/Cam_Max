"""
Enhanced database methods for V2 features.
This module extends the base database with V2 functionality.
"""
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from database.models import db
from utils.logger import logger

class V2Database:
    """Extended database operations for V2 features."""
    
    # Video Archive operations
    @staticmethod
    def add_video_archive(camera_id: int, start_time: datetime, 
                         end_time: datetime, file_path: str, size_mb: float) -> int:
        """Add video archive record."""
        conn = db._get_connection()
        cursor = conn.cursor()
        
        duration = int((end_time - start_time).total_seconds())
        
        cursor.execute('''
            INSERT INTO video_archives 
            (camera_id, start_time, end_time, duration_seconds, file_path, size_mb)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (camera_id, start_time, end_time, duration, file_path, size_mb))
        
        archive_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return archive_id
    
    @staticmethod
    def get_video_archives(camera_id: int = None, 
                          start_time: datetime = None,
                          end_time: datetime = None) -> List[Dict[str, Any]]:
        """Get video archives with filters."""
        conn = db._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM video_archives WHERE 1=1'
        params = []
        
        if camera_id:
            query += ' AND camera_id = ?'
            params.append(camera_id)
        
        if start_time:
            query += ' AND end_time >= ?'
            params.append(start_time)
        
        if end_time:
            query += ' AND start_time <= ?'
            params.append(end_time)
        
        query += ' ORDER BY start_time DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Person Tracking operations
    @staticmethod
    def create_person_track(tracking_id: str, first_seen: datetime,
                           entry_camera_id: int, screenshot_path: str = None) -> int:
        """Create new person tracking record."""
        conn = db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO person_tracks 
            (tracking_id, first_seen, entry_camera_id, screenshot_path)
            VALUES (?, ?, ?, ?)
        ''', (tracking_id, first_seen, entry_camera_id, screenshot_path))
        
        track_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Person track created: {tracking_id}")
        return track_id
    
    @staticmethod
    def update_person_track(tracking_id: str, last_seen: datetime = None,
                           exit_camera_id: int = None, path_data: dict = None):
        """Update person tracking record."""
        conn = db._get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if last_seen:
            updates.append('last_seen = ?')
            params.append(last_seen)
        
        if exit_camera_id:
            updates.append('exit_camera_id = ?')
            params.append(exit_camera_id)
        
        if path_data:
            updates.append('path_data = ?')
            params.append(json.dumps(path_data))
        
        if updates:
            query = f"UPDATE person_tracks SET {', '.join(updates)} WHERE tracking_id = ?"
            params.append(tracking_id)
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    @staticmethod
    def get_person_track(tracking_id: str) -> Optional[Dict[str, Any]]:
        """Get person track by ID."""
        conn = db._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM person_tracks WHERE tracking_id = ?', (tracking_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    # Object Tracking operations
    @staticmethod
    def create_object_track(object_type: str, first_detected: datetime,
                           camera_id: int, location: str = None) -> int:
        """Create object tracking record."""
        conn = db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO object_tracks 
            (object_type, first_detected, camera_id, location, status)
            VALUES (?, ?, ?, ?, 'stationary')
        ''', (object_type, first_detected, camera_id, location))
        
        track_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return track_id
    
    @staticmethod
    def update_object_track(track_id: int, person_tracking_id: str = None,
                           status: str = None, last_detected: datetime = None):
        """Update object tracking."""
        conn = db._get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if person_tracking_id:
            updates.append('person_tracking_id = ?')
            params.append(person_tracking_id)
        
        if status:
            updates.append('status = ?')
            params.append(status)
        
        if last_detected:
            updates.append('last_detected = ?')
            params.append(last_detected)
        
        if updates:
            query = f"UPDATE object_tracks SET {', '.join(updates)} WHERE id = ?"
            params.append(track_id)
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    # Detection Events operations
    @staticmethod
    def add_detection_event(camera_id: int, event_type: str,
                          person_tracking_id: str = None,
                          object_tracking_id: int = None,
                          confidence: float = None,
                          video_clip_path: str = None,
                          screenshot_path: str = None,
                          description_uzbek: str = None) -> int:
        """Add detection event."""
        conn = db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO detection_events 
            (camera_id, event_type, person_tracking_id, object_tracking_id,
             confidence, video_clip_path, screenshot_path, description_uzbek)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (camera_id, event_type, person_tracking_id, object_tracking_id,
              confidence, video_clip_path, screenshot_path, description_uzbek))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return event_id
    
    # Query History operations
    @staticmethod
    def add_query(user_id: int, query_text: str, query_params: dict = None,
                 results_count: int = 0, response_time_ms: int = 0) -> int:
        """Add query to history."""
        conn = db._get_connection()
        cursor = conn.cursor()
        
        params_json = json.dumps(query_params) if query_params else None
        
        cursor.execute('''
            INSERT INTO query_history 
            (user_id, query_text, query_params, results_count, response_time_ms)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, query_text, params_json, results_count, response_time_ms))
        
        query_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return query_id
    
    @staticmethod
    def get_user_queries(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's query history."""
        conn = db._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM query_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

# Global V2 database instance
v2db = V2Database()
