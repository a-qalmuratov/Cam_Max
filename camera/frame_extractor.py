"""
Video Frame Extractor
Video arxivdan keyframe'larni olish.
"""
import os
import cv2
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import numpy as np

from camera.video_recorder import video_recorder, VIDEO_DIR, SEGMENT_DURATION
from utils.logger import logger


class VideoFrameExtractor:
    """Video arxivdan frame'larni olish."""
    
    def __init__(self):
        self.video_dir = VIDEO_DIR
    
    def extract_frames(self, camera_id: int, 
                       start_time: datetime, 
                       end_time: datetime,
                       interval_seconds: float = 2.0) -> List[Dict]:
        """
        Vaqt oralig'idagi frame'larni olish.
        
        Args:
            camera_id: Kamera ID
            start_time: Boshlanish vaqti
            end_time: Tugash vaqti
            interval_seconds: Har necha sekundda 1 frame (default 2)
            
        Returns:
            List of {'frame': np.array, 'timestamp': datetime, 'camera_id': int}
        """
        frames = []
        
        try:
            # Find relevant video segments
            segments = video_recorder._find_segments(camera_id, start_time, end_time)
            
            if not segments:
                logger.warning(f"No video segments found for camera {camera_id}")
                return frames
            
            for segment_path in segments:
                if not os.path.exists(segment_path):
                    continue
                
                # Parse segment start time from filename
                try:
                    seg_filename = os.path.basename(segment_path)
                    time_str = seg_filename.replace('.mp4', '')
                    date_str = os.path.basename(os.path.dirname(segment_path))
                    seg_start = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H-%M-%S')
                except Exception:
                    continue
                
                # Open video
                cap = cv2.VideoCapture(segment_path)
                if not cap.isOpened():
                    continue
                
                fps = cap.get(cv2.CAP_PROP_FPS) or 15
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = total_frames / fps
                
                # Calculate which frames to extract
                frames_to_skip = int(interval_seconds * fps)
                current_frame = 0
                
                while True:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                    ret, frame = cap.read()
                    
                    if not ret:
                        break
                    
                    # Calculate timestamp for this frame
                    frame_time_offset = current_frame / fps
                    frame_timestamp = seg_start + timedelta(seconds=frame_time_offset)
                    
                    # Only include frames within requested time range
                    if start_time <= frame_timestamp <= end_time:
                        frames.append({
                            'frame': frame,
                            'timestamp': frame_timestamp,
                            'camera_id': camera_id
                        })
                    
                    current_frame += frames_to_skip
                    
                    if current_frame >= total_frames:
                        break
                
                cap.release()
            
            logger.info(f"Extracted {len(frames)} frames from camera {camera_id}")
            
        except Exception as e:
            logger.error(f"Error extracting frames: {e}")
        
        return frames
    
    def extract_frame_at_time(self, camera_id: int, 
                              timestamp: datetime) -> Optional[np.ndarray]:
        """Aniq vaqtdagi frame'ni olish."""
        try:
            # Find the segment containing this timestamp
            segments = video_recorder._find_segments(
                camera_id, 
                timestamp - timedelta(seconds=1),
                timestamp + timedelta(seconds=1)
            )
            
            if not segments:
                return None
            
            segment_path = segments[0]
            
            if not os.path.exists(segment_path):
                return None
            
            # Parse segment start time
            seg_filename = os.path.basename(segment_path)
            time_str = seg_filename.replace('.mp4', '')
            date_str = os.path.basename(os.path.dirname(segment_path))
            seg_start = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H-%M-%S')
            
            # Open video
            cap = cv2.VideoCapture(segment_path)
            if not cap.isOpened():
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS) or 15
            
            # Calculate frame position
            offset_seconds = (timestamp - seg_start).total_seconds()
            frame_pos = int(offset_seconds * fps)
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, frame_pos))
            ret, frame = cap.read()
            cap.release()
            
            return frame if ret else None
            
        except Exception as e:
            logger.error(f"Error extracting frame at time: {e}")
            return None
    
    def get_screenshot(self, camera_id: int, 
                       timestamp: datetime) -> Optional[bytes]:
        """Screenshot JPEG formatida olish."""
        frame = self.extract_frame_at_time(camera_id, timestamp)
        if frame is None:
            return None
        
        try:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            return buffer.tobytes()
        except Exception as e:
            logger.error(f"Error encoding screenshot: {e}")
            return None


# Global instance
frame_extractor = VideoFrameExtractor()
