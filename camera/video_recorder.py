"""
Video recording and archive management system.
Handles 24/7 recording, segmentation, and clip extraction.
"""
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from database.models import db
from utils.logger import logger
from utils.config import DATA_DIR

# Recording configuration
SEGMENT_DURATION = 600  # 10 minutes per segment
ARCHIVE_RETENTION_DAYS = 30
VIDEO_DIR = os.path.join(DATA_DIR, 'videos')


class VideoRecorder:
    """Handle video recording and archive management."""
    
    def __init__(self):
        self.is_recording: Dict[int, bool] = {}
        self.recording_threads: Dict[int, threading.Thread] = {}
        
        # Ensure video directory exists
        os.makedirs(VIDEO_DIR, exist_ok=True)
    
    def start_recording(self, camera_id: int) -> bool:
        """Start recording for a camera."""
        if camera_id in self.is_recording and self.is_recording[camera_id]:
            logger.warning(f"Camera {camera_id} already recording")
            return True
        
        self.is_recording[camera_id] = True
        
        # Start recording thread
        thread = threading.Thread(
            target=self._recording_loop,
            args=(camera_id,),
            daemon=True
        )
        self.recording_threads[camera_id] = thread
        thread.start()
        
        logger.info(f"Started recording for camera {camera_id}")
        return True
    
    def stop_recording(self, camera_id: int) -> bool:
        """Stop recording for a camera."""
        if camera_id not in self.is_recording:
            return True
        
        self.is_recording[camera_id] = False
        
        # Wait for thread to finish
        if camera_id in self.recording_threads:
            self.recording_threads[camera_id].join(timeout=5)
            del self.recording_threads[camera_id]
        
        logger.info(f"Stopped recording for camera {camera_id}")
        return True
    
    def _recording_loop(self, camera_id: int):
        """Main recording loop for a camera."""
        from camera.stream_manager import stream_manager
        import cv2
        
        camera = db.get_camera(camera_id)
        if not camera:
            logger.error(f"Camera {camera_id} not found")
            return
        
        cam_client = stream_manager.get_camera(camera_id)
        if not cam_client:
            # Try to connect
            rtsp_url = camera.get('rtsp_url') or f"rtsp://{camera['username']}:{camera['password']}@{camera['ip_address']}:{camera['port']}/stream1"
            stream_manager.add_camera(camera_id, rtsp_url)
            cam_client = stream_manager.get_camera(camera_id)
        
        if not cam_client:
            logger.error(f"Could not connect to camera {camera_id}")
            self.is_recording[camera_id] = False
            return
        
        segment_start = datetime.now()
        segment_path = self._get_segment_path(camera_id, segment_start)
        
        # Video writer setup
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 15
        frame_size = (640, 480)  # Default, will be updated from first frame
        writer = None
        
        while self.is_recording.get(camera_id, False):
            try:
                frame = cam_client.get_frame()
                
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Initialize writer with actual frame size
                if writer is None:
                    h, w = frame.shape[:2]
                    frame_size = (w, h)
                    writer = cv2.VideoWriter(segment_path, fourcc, fps, frame_size)
                
                writer.write(frame)
                
                # Check if segment duration exceeded
                if (datetime.now() - segment_start).total_seconds() >= SEGMENT_DURATION:
                    # Close current segment
                    if writer:
                        writer.release()
                    
                    # Save segment info to database
                    self._save_segment_info(camera_id, segment_start, segment_path)
                    
                    # Start new segment
                    segment_start = datetime.now()
                    segment_path = self._get_segment_path(camera_id, segment_start)
                    writer = cv2.VideoWriter(segment_path, fourcc, fps, frame_size)
                
                time.sleep(1.0 / fps)
                
            except Exception as e:
                logger.error(f"Recording error for camera {camera_id}: {e}")
                time.sleep(1)
        
        # Cleanup
        if writer:
            writer.release()
        
        # Save final segment
        self._save_segment_info(camera_id, segment_start, segment_path)
    
    def _get_segment_path(self, camera_id: int, timestamp: datetime) -> str:
        """Generate path for video segment."""
        date_dir = os.path.join(VIDEO_DIR, str(camera_id), timestamp.strftime('%Y-%m-%d'))
        os.makedirs(date_dir, exist_ok=True)
        
        filename = f"{timestamp.strftime('%H-%M-%S')}.mp4"
        return os.path.join(date_dir, filename)
    
    def _save_segment_info(self, camera_id: int, start_time: datetime, file_path: str):
        """Save segment information to database."""
        try:
            if os.path.exists(file_path):
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                duration = SEGMENT_DURATION
                
                # Save to database (using v2db if available)
                try:
                    from database.v2_models import v2db
                    v2db.save_video_archive(
                        camera_id=camera_id,
                        start_time=start_time,
                        duration=duration,
                        file_path=file_path,
                        size_mb=size_mb
                    )
                except:
                    pass
                
                logger.debug(f"Saved segment: {file_path} ({size_mb:.2f} MB)")
        except Exception as e:
            logger.error(f"Error saving segment info: {e}")
    
    def extract_clip(self, camera_id: int, start_time: datetime, end_time: datetime) -> Optional[str]:
        """Extract video clip from archive for given time range using ffmpeg."""
        try:
            import subprocess
            import shutil
            
            # Find relevant segment files
            segments = self._find_segments(camera_id, start_time, end_time)
            
            if not segments:
                logger.warning(f"No segments found for camera {camera_id} in time range")
                return None
            
            # Output path
            clip_dir = os.path.join(VIDEO_DIR, 'clips')
            os.makedirs(clip_dir, exist_ok=True)
            
            clip_filename = f"clip_{camera_id}_{start_time.strftime('%Y%m%d_%H%M%S')}.mp4"
            clip_path = os.path.join(clip_dir, clip_filename)
            
            # Check if ffmpeg is available
            ffmpeg_available = False
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                ffmpeg_available = True
            except:
                logger.warning("ffmpeg not found, using simple copy")
            
            if len(segments) == 1:
                # Single segment - trim if ffmpeg available
                segment_path = segments[0]
                
                if ffmpeg_available:
                    # Parse segment start time from filename
                    try:
                        seg_filename = os.path.basename(segment_path)
                        time_str = seg_filename.replace('.mp4', '')
                        date_str = os.path.basename(os.path.dirname(segment_path))
                        seg_start = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H-%M-%S')
                        
                        # Calculate offset
                        offset_seconds = max(0, (start_time - seg_start).total_seconds())
                        duration_seconds = (end_time - start_time).total_seconds()
                        
                        # Trim with ffmpeg
                        cmd = [
                            'ffmpeg', '-y',
                            '-ss', str(offset_seconds),
                            '-i', segment_path,
                            '-t', str(duration_seconds),
                            '-c', 'copy',
                            clip_path
                        ]
                        subprocess.run(cmd, capture_output=True, check=True)
                        logger.info(f"Extracted clip with ffmpeg: {clip_path}")
                        return clip_path
                    except Exception as e:
                        logger.warning(f"ffmpeg trim failed: {e}, falling back to copy")
                
                # Fallback: just copy
                shutil.copy(segment_path, clip_path)
                return clip_path
            
            else:
                # Multiple segments - concatenate with ffmpeg
                if ffmpeg_available:
                    try:
                        # Create concat file list
                        concat_list_path = os.path.join(clip_dir, f"concat_{camera_id}.txt")
                        with open(concat_list_path, 'w') as f:
                            for seg in segments:
                                f.write(f"file '{seg}'\n")
                        
                        # Concatenate with ffmpeg
                        cmd = [
                            'ffmpeg', '-y',
                            '-f', 'concat',
                            '-safe', '0',
                            '-i', concat_list_path,
                            '-c', 'copy',
                            clip_path
                        ]
                        subprocess.run(cmd, capture_output=True, check=True)
                        
                        # Clean up concat list
                        os.remove(concat_list_path)
                        
                        logger.info(f"Concatenated {len(segments)} segments to: {clip_path}")
                        return clip_path
                    except Exception as e:
                        logger.warning(f"ffmpeg concat failed: {e}, falling back to first segment")
                
                # Fallback: just copy first segment
                if segments and os.path.exists(segments[0]):
                    shutil.copy(segments[0], clip_path)
                    return clip_path
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting clip: {e}")
            return None
    
    def _find_segments(self, camera_id: int, start_time: datetime, end_time: datetime) -> List[str]:
        """Find video segments for given time range."""
        segments = []
        
        camera_dir = os.path.join(VIDEO_DIR, str(camera_id))
        if not os.path.exists(camera_dir):
            return segments
        
        # Iterate through date directories
        current_date = start_time.date()
        end_date = end_time.date()
        
        while current_date <= end_date:
            date_dir = os.path.join(camera_dir, current_date.strftime('%Y-%m-%d'))
            
            if os.path.exists(date_dir):
                for filename in sorted(os.listdir(date_dir)):
                    if filename.endswith('.mp4'):
                        file_path = os.path.join(date_dir, filename)
                        
                        # Parse timestamp from filename
                        try:
                            time_str = filename.replace('.mp4', '')
                            file_time = datetime.strptime(
                                f"{current_date.strftime('%Y-%m-%d')} {time_str}",
                                '%Y-%m-%d %H-%M-%S'
                            )
                            
                            # Check if segment overlaps with requested range
                            segment_end = file_time + timedelta(seconds=SEGMENT_DURATION)
                            
                            if file_time <= end_time and segment_end >= start_time:
                                segments.append(file_path)
                        except:
                            continue
            
            current_date += timedelta(days=1)
        
        return segments
    
    def cleanup_old_archives(self, retention_days: int = ARCHIVE_RETENTION_DAYS):
        """Remove archives older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            for camera_id_dir in os.listdir(VIDEO_DIR):
                camera_path = os.path.join(VIDEO_DIR, camera_id_dir)
                
                if not os.path.isdir(camera_path) or camera_id_dir == 'clips':
                    continue
                
                for date_dir in os.listdir(camera_path):
                    try:
                        dir_date = datetime.strptime(date_dir, '%Y-%m-%d')
                        
                        if dir_date < cutoff_date:
                            date_path = os.path.join(camera_path, date_dir)
                            import shutil
                            shutil.rmtree(date_path)
                            logger.info(f"Cleaned up old archive: {date_path}")
                    except:
                        continue
        except Exception as e:
            logger.error(f"Error cleaning archives: {e}")
    
    def get_archive_stats(self, camera_id: int) -> Dict:
        """Get archive statistics for a camera."""
        camera_dir = os.path.join(VIDEO_DIR, str(camera_id))
        
        stats = {
            'total_size_mb': 0,
            'segment_count': 0,
            'oldest_date': None,
            'newest_date': None
        }
        
        if not os.path.exists(camera_dir):
            return stats
        
        try:
            for date_dir in sorted(os.listdir(camera_dir)):
                date_path = os.path.join(camera_dir, date_dir)
                
                if not os.path.isdir(date_path):
                    continue
                
                try:
                    dir_date = datetime.strptime(date_dir, '%Y-%m-%d')
                    
                    if stats['oldest_date'] is None:
                        stats['oldest_date'] = date_dir
                    stats['newest_date'] = date_dir
                    
                    for filename in os.listdir(date_path):
                        if filename.endswith('.mp4'):
                            file_path = os.path.join(date_path, filename)
                            stats['total_size_mb'] += os.path.getsize(file_path) / (1024 * 1024)
                            stats['segment_count'] += 1
                except:
                    continue
        except Exception as e:
            logger.error(f"Error getting archive stats: {e}")
        
        return stats


# Global instance
video_recorder = VideoRecorder()
