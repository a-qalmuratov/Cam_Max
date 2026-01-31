"""Database models for Cam_Max bot."""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from utils.config import DATABASE_PATH
from utils.logger import logger

class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize database connection."""
        self.db_path = db_path
        self._create_tables()
    
    def _get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Cameras table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                name TEXT NOT NULL,
                location TEXT,
                ip_address TEXT NOT NULL,
                port INTEGER NOT NULL DEFAULT 554,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                camera_type TEXT DEFAULT 'generic',
                rtsp_url TEXT,
                status TEXT DEFAULT 'inactive',
                recording_enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Organizations table (NEW for V2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                owner_id INTEGER,
                subscription_type TEXT DEFAULT 'free',
                camera_limit INTEGER DEFAULT 3,
                storage_limit_gb INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users table (ENHANCED for V2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone_number TEXT UNIQUE,
                role TEXT DEFAULT 'user',
                organization_id INTEGER,
                is_admin BOOLEAN DEFAULT 0,
                is_verified BOOLEAN DEFAULT 0,
                registration_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Video Archives (NEW for V2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_archives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration_seconds INTEGER,
                file_path TEXT,
                size_mb REAL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (camera_id) REFERENCES cameras (id)
            )
        ''')
        
        # Person Tracks (NEW for V2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS person_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_id TEXT UNIQUE NOT NULL,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP,
                entry_camera_id INTEGER,
                exit_camera_id INTEGER,
                description TEXT,
                path_data TEXT,
                screenshot_path TEXT,
                FOREIGN KEY (entry_camera_id) REFERENCES cameras (id),
                FOREIGN KEY (exit_camera_id) REFERENCES cameras (id)
            )
        ''')
        
        # Object Tracks (NEW for V2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS object_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_type TEXT NOT NULL,
                first_detected TIMESTAMP NOT NULL,
                last_detected TIMESTAMP,
                camera_id INTEGER,
                location TEXT,
                person_tracking_id TEXT,
                status TEXT DEFAULT 'stationary',
                path_data TEXT,
                FOREIGN KEY (camera_id) REFERENCES cameras (id),
                FOREIGN KEY (person_tracking_id) REFERENCES person_tracks (tracking_id)
            )
        ''')
        
        # Detection Events (ENHANCED for V2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                person_tracking_id TEXT,
                object_tracking_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence REAL,
                video_clip_path TEXT,
                screenshot_path TEXT,
                description_uzbek TEXT,
                metadata TEXT,
                FOREIGN KEY (camera_id) REFERENCES cameras (id),
                FOREIGN KEY (person_tracking_id) REFERENCES person_tracks (tracking_id),
                FOREIGN KEY (object_tracking_id) REFERENCES object_tracks (id)
            )
        ''')
        
        # Detections table (kept for backward compatibility)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id INTEGER NOT NULL,
                object_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                bbox_x REAL,
                bbox_y REAL,
                bbox_w REAL,
                bbox_h REAL,
                image_path TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (camera_id) REFERENCES cameras (id)
            )
        ''')
        
        # Query History (NEW for V2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                query_text TEXT NOT NULL,
                query_params TEXT,
                results_count INTEGER DEFAULT 0,
                response_time_ms INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Events table (for logging events)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                camera_id INTEGER,
                description TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (camera_id) REFERENCES cameras (id)
            )
        ''')
        
        # Bookmarks table (for saving favorite moments)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                camera_id INTEGER NOT NULL,
                name TEXT,
                timestamp TIMESTAMP NOT NULL,
                image_path TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (camera_id) REFERENCES cameras (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database tables created successfully")
    
    # Camera operations
    def add_camera(self, name: str, ip_address: str, port: int, 
                   username: str, password: str, camera_type: str = 'generic',
                   rtsp_url: str = None, organization_id: int = None) -> int:
        """Add a new camera to database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cameras (name, ip_address, port, username, password, camera_type, rtsp_url, status, organization_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)
        ''', (name, ip_address, port, username, password, camera_type, rtsp_url, organization_id))
        
        camera_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Camera '{name}' added with ID: {camera_id}")
        return camera_id
    
    def get_camera(self, camera_id: int) -> Optional[Dict[str, Any]]:
        """Get camera by ID."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cameras WHERE id = ?', (camera_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_all_cameras(self) -> List[Dict[str, Any]]:
        """Get all cameras."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cameras ORDER BY id')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_cameras_by_organization(self, org_id: int) -> List[Dict[str, Any]]:
        """Get cameras belonging to a specific organization."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cameras WHERE organization_id = ? ORDER BY id', (org_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_camera_status(self, camera_id: int, status: str):
        """Update camera status."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cameras 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (status, camera_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Camera {camera_id} status updated to: {status}")
    
    def delete_camera(self, camera_id: int):
        """Delete camera from database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM cameras WHERE id = ?', (camera_id,))
        conn.commit()
        conn.close()
        logger.info(f"Camera {camera_id} deleted")
    
    # Organization operations (NEW for V2)
    def create_organization(self, name: str, owner_id: int) -> int:
        """Create new organization."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO organizations (name, owner_id)
            VALUES (?, ?)
        ''', (name, owner_id))
        
        org_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Organization '{name}' created with ID: {org_id}")
        return org_id
    
    def get_organization(self, org_id: int) -> Optional[Dict[str, Any]]:
        """Get organization by ID."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM organizations WHERE id = ?', (org_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    # User operations (ENHANCED for V2)
    def add_user(self, user_id: int, username: str = None, 
                 first_name: str = None, last_name: str = None, 
                 is_admin: bool = False, phone_number: str = None,
                 organization_id: int = None, role: str = 'user'):
        """Add or update user."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (id, username, first_name, last_name, is_admin, phone_number, organization_id, role, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username, first_name, last_name, is_admin, phone_number, organization_id, role))
        
        conn.commit()
        conn.close()
        logger.info(f"User {user_id} added/updated")
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return bool(result[0]) if result else False
    
    # Detection operations
    def add_detection(self, camera_id: int, object_type: str, confidence: float,
                     bbox: tuple = None, image_path: str = None):
        """Add detection record."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        bbox_x, bbox_y, bbox_w, bbox_h = bbox if bbox else (None, None, None, None)
        
        cursor.execute('''
            INSERT INTO detections (camera_id, object_type, confidence, 
                                   bbox_x, bbox_y, bbox_w, bbox_h, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (camera_id, object_type, confidence, bbox_x, bbox_y, bbox_w, bbox_h, image_path))
        
        conn.commit()
        conn.close()
    
    def get_recent_detections(self, camera_id: int = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent detections."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if camera_id:
            cursor.execute('''
                SELECT * FROM detections 
                WHERE camera_id = ? 
                ORDER BY detected_at DESC 
                LIMIT ?
            ''', (camera_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM detections 
                ORDER BY detected_at DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Event logging
    def log_event(self, event_type: str, camera_id: int = None, 
                  description: str = None, metadata: str = None):
        """Log an event."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (event_type, camera_id, description, metadata)
            VALUES (?, ?, ?, ?)
        ''', (event_type, camera_id, description, metadata))
        
        conn.commit()
        conn.close()
    
    # User update methods
    def update_user_name(self, user_id: int, new_name: str):
        """Update user's first name."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET first_name = ? WHERE id = ?
        ''', (new_name, user_id))
        
        conn.commit()
        conn.close()
        logger.info(f"User {user_id} name updated to: {new_name}")
    
    def update_user_phone(self, user_id: int, new_phone: str):
        """Update user's phone number."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET phone_number = ? WHERE id = ?
        ''', (new_phone, user_id))
        
        conn.commit()
        conn.close()
        logger.info(f"User {user_id} phone updated to: {new_phone}")
    
    # Statistics methods
    def get_statistics(self, organization_id: int = None) -> Dict[str, Any]:
        """Get real statistics for dashboard, filtered by organization."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get camera counts
        if organization_id:
            cursor.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active
                FROM cameras WHERE organization_id = ?
            ''', (organization_id,))
        else:
            cursor.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active
                FROM cameras
            ''')
        
        row = cursor.fetchone()
        total_cameras = row[0] if row else 0
        active_cameras = row[1] if row and row[1] else 0
        
        # Get today's detection counts - FILTERED BY ORGANIZATION
        if organization_id:
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN d.object_type = 'person' THEN 1 ELSE 0 END) as people,
                    SUM(CASE WHEN d.object_type IN ('car', 'truck', 'bus', 'motorcycle') THEN 1 ELSE 0 END) as vehicles,
                    COUNT(*) as total_detections
                FROM detections d
                JOIN cameras c ON d.camera_id = c.id
                WHERE DATE(d.detected_at) = DATE('now')
                AND c.organization_id = ?
            ''', (organization_id,))
        else:
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN object_type = 'person' THEN 1 ELSE 0 END) as people,
                    SUM(CASE WHEN object_type IN ('car', 'truck', 'bus', 'motorcycle') THEN 1 ELSE 0 END) as vehicles,
                    COUNT(*) as total_detections
                FROM detections 
                WHERE DATE(detected_at) = DATE('now')
            ''')
        
        row = cursor.fetchone()
        people_today = row[0] if row and row[0] else 0
        vehicles_today = row[1] if row and row[1] else 0
        total_detections = row[2] if row and row[2] else 0
        
        # Get events count - FILTERED BY ORGANIZATION
        if organization_id:
            cursor.execute('''
                SELECT COUNT(*) FROM events e
                LEFT JOIN cameras c ON e.camera_id = c.id
                WHERE DATE(e.created_at) = DATE('now')
                AND (c.organization_id = ? OR e.camera_id IS NULL)
            ''', (organization_id,))
        else:
            cursor.execute('''
                SELECT COUNT(*) FROM events WHERE DATE(created_at) = DATE('now')
            ''')
        row = cursor.fetchone()
        events_today = row[0] if row else 0
        
        conn.close()
        
        return {
            'cameras_total': total_cameras,
            'cameras_active': active_cameras,
            'cameras_inactive': total_cameras - active_cameras,
            'people_today': people_today,
            'vehicles_today': vehicles_today,
            'detections_today': total_detections,
            'events_today': events_today
        }
    
    def get_weekly_statistics(self, organization_id: int = None) -> List[Dict[str, Any]]:
        """Get weekly statistics breakdown, filtered by organization."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if organization_id:
            cursor.execute('''
                SELECT 
                    DATE(d.detected_at) as date,
                    SUM(CASE WHEN d.object_type = 'person' THEN 1 ELSE 0 END) as people,
                    SUM(CASE WHEN d.object_type IN ('car', 'truck', 'bus', 'motorcycle') THEN 1 ELSE 0 END) as vehicles,
                    COUNT(*) as total
                FROM detections d
                JOIN cameras c ON d.camera_id = c.id
                WHERE d.detected_at >= DATE('now', '-7 days')
                AND c.organization_id = ?
                GROUP BY DATE(d.detected_at)
                ORDER BY date DESC
            ''', (organization_id,))
        else:
            cursor.execute('''
                SELECT 
                    DATE(detected_at) as date,
                    SUM(CASE WHEN object_type = 'person' THEN 1 ELSE 0 END) as people,
                    SUM(CASE WHEN object_type IN ('car', 'truck', 'bus', 'motorcycle') THEN 1 ELSE 0 END) as vehicles,
                    COUNT(*) as total
                FROM detections 
                WHERE detected_at >= DATE('now', '-7 days')
                GROUP BY DATE(detected_at)
                ORDER BY date DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            result.append({
                'date': row[0],
                'people': row[1] or 0,
                'vehicles': row[2] or 0,
                'total': row[3] or 0
            })
        
        return result
    
    # Bookmark operations
    def add_bookmark(self, user_id: int, camera_id: int, timestamp: str, 
                     name: str = None, image_path: str = None, note: str = None) -> int:
        """Add a bookmark (favorite moment)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bookmarks (user_id, camera_id, name, timestamp, image_path, note)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, camera_id, name, timestamp, image_path, note))
        
        bookmark_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Bookmark {bookmark_id} added for user {user_id}")
        return bookmark_id
    
    def get_bookmarks(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all bookmarks for a user."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT b.*, c.name as camera_name 
            FROM bookmarks b
            LEFT JOIN cameras c ON b.camera_id = c.id
            WHERE b.user_id = ?
            ORDER BY b.created_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_bookmark(self, bookmark_id: int, user_id: int) -> bool:
        """Delete a bookmark (only if owned by user)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM bookmarks WHERE id = ? AND user_id = ?
            ''', (bookmark_id, user_id))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if deleted:
                logger.info(f"Bookmark {bookmark_id} deleted for user {user_id}")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting bookmark: {e}")
            return False

# Global database instance
db = Database()


