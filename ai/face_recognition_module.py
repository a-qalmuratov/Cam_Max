"""
Face Recognition Module
Yuzni tanish va saqlash.
"""
import os
import pickle
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import cv2

from utils.logger import logger

# Try to import face_recognition (may not be installed)
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("face_recognition not installed. Using fallback.")

# Try DeepFace as backup
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False


class Face:
    """Yuz ma'lumoti."""
    def __init__(self, bbox: tuple, embedding: np.ndarray = None, 
                 name: str = None, confidence: float = 0.0):
        self.bbox = bbox  # (x, y, w, h)
        self.embedding = embedding
        self.name = name
        self.confidence = confidence
        self.timestamp = datetime.now()


class FaceRecognizer:
    """Yuzni tanish va boshqarish."""
    
    def __init__(self, data_dir: str = "data/faces"):
        self.data_dir = data_dir
        self.known_faces: Dict[int, List[dict]] = {}  # user_id -> faces
        os.makedirs(data_dir, exist_ok=True)
        self._load_known_faces()
    
    def _load_known_faces(self):
        """Saqlangan yuzlarni yuklash."""
        try:
            db_path = os.path.join(self.data_dir, "faces_db.pkl")
            if os.path.exists(db_path):
                with open(db_path, 'rb') as f:
                    self.known_faces = pickle.load(f)
                logger.info(f"Loaded {sum(len(v) for v in self.known_faces.values())} known faces")
        except Exception as e:
            logger.error(f"Error loading faces: {e}")
            self.known_faces = {}
    
    def _save_known_faces(self):
        """Yuzlarni saqlash."""
        try:
            db_path = os.path.join(self.data_dir, "faces_db.pkl")
            with open(db_path, 'wb') as f:
                pickle.dump(self.known_faces, f)
        except Exception as e:
            logger.error(f"Error saving faces: {e}")
    
    def detect_faces(self, frame: np.ndarray) -> List[Face]:
        """Frame'dan yuzlarni aniqlash."""
        faces = []
        
        if FACE_RECOGNITION_AVAILABLE:
            try:
                # RGB convert
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                face_locations = face_recognition.face_locations(rgb_frame, model="hog")
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                
                for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                    bbox = (left, top, right - left, bottom - top)
                    faces.append(Face(bbox=bbox, embedding=encoding))
                    
            except Exception as e:
                logger.error(f"Face detection error: {e}")
        
        elif DEEPFACE_AVAILABLE:
            try:
                # DeepFace detection
                results = DeepFace.extract_faces(
                    frame, 
                    detector_backend='opencv',
                    enforce_detection=False
                )
                for result in results:
                    if result['confidence'] > 0.5:
                        region = result['facial_area']
                        bbox = (region['x'], region['y'], region['w'], region['h'])
                        faces.append(Face(bbox=bbox, confidence=result['confidence']))
            except Exception as e:
                logger.error(f"DeepFace error: {e}")
        
        else:
            # Fallback: OpenCV Haar Cascade
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                cascade = cv2.CascadeClassifier(cascade_path)
                detected = cascade.detectMultiScale(gray, 1.1, 4)
                
                for (x, y, w, h) in detected:
                    faces.append(Face(bbox=(x, y, w, h)))
            except Exception as e:
                logger.error(f"OpenCV face detection error: {e}")
        
        return faces
    
    def extract_embedding(self, frame: np.ndarray, face: Face) -> np.ndarray:
        """Yuz embedding'ini olish."""
        if face.embedding is not None:
            return face.embedding
        
        if not FACE_RECOGNITION_AVAILABLE:
            return None
        
        try:
            x, y, w, h = face.bbox
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # face_recognition format: (top, right, bottom, left)
            face_location = [(y, x + w, y + h, x)]
            encodings = face_recognition.face_encodings(rgb_frame, face_location)
            
            if encodings:
                face.embedding = encodings[0]
                return encodings[0]
        except Exception as e:
            logger.error(f"Embedding extraction error: {e}")
        
        return None
    
    def compare_faces(self, embedding1: np.ndarray, embedding2: np.ndarray, 
                      threshold: float = 0.6) -> Tuple[bool, float]:
        """Ikki yuzni solishtirish."""
        if embedding1 is None or embedding2 is None:
            return False, 0.0
        
        if FACE_RECOGNITION_AVAILABLE:
            distance = face_recognition.face_distance([embedding1], embedding2)[0]
            is_match = distance < threshold
            confidence = 1 - distance
            return is_match, confidence
        else:
            # Euclidean distance
            distance = np.linalg.norm(embedding1 - embedding2)
            is_match = distance < threshold
            confidence = max(0, 1 - distance)
            return is_match, confidence
    
    def add_known_face(self, user_id: int, name: str, 
                       frame: np.ndarray, category: str = "known") -> bool:
        """Yangi yuzni qo'shish."""
        faces = self.detect_faces(frame)
        
        if not faces:
            logger.warning("No face detected in image")
            return False
        
        face = faces[0]  # Birinchi yuzni olish
        embedding = self.extract_embedding(frame, face)
        
        if embedding is None:
            logger.warning("Could not extract face embedding")
            return False
        
        # Save face image
        x, y, w, h = face.bbox
        face_crop = frame[y:y+h, x:x+w]
        face_path = os.path.join(self.data_dir, f"{user_id}_{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
        cv2.imwrite(face_path, face_crop)
        
        # Add to known faces
        if user_id not in self.known_faces:
            self.known_faces[user_id] = []
        
        self.known_faces[user_id].append({
            'name': name,
            'embedding': embedding,
            'category': category,
            'image_path': face_path,
            'created_at': datetime.now().isoformat()
        })
        
        self._save_known_faces()
        logger.info(f"Added face for {name} (user {user_id})")
        return True
    
    def identify_person(self, user_id: int, frame: np.ndarray) -> List[dict]:
        """Frame'dagi yuzlarni aniqlash."""
        results = []
        faces = self.detect_faces(frame)
        
        if not faces:
            return results
        
        known = self.known_faces.get(user_id, [])
        
        for face in faces:
            embedding = self.extract_embedding(frame, face)
            if embedding is None:
                continue
            
            best_match = None
            best_confidence = 0.0
            
            for known_face in known:
                is_match, confidence = self.compare_faces(
                    embedding, known_face['embedding']
                )
                if is_match and confidence > best_confidence:
                    best_match = known_face
                    best_confidence = confidence
            
            if best_match:
                results.append({
                    'name': best_match['name'],
                    'category': best_match['category'],
                    'confidence': best_confidence,
                    'bbox': face.bbox,
                    'known': True
                })
            else:
                results.append({
                    'name': 'Notanish',
                    'category': 'unknown',
                    'confidence': 0.0,
                    'bbox': face.bbox,
                    'known': False
                })
        
        return results
    
    def get_known_faces(self, user_id: int) -> List[dict]:
        """User'ning saqlangan yuzlari."""
        faces = self.known_faces.get(user_id, [])
        return [
            {
                'name': f['name'],
                'category': f['category'],
                'created_at': f['created_at']
            }
            for f in faces
        ]
    
    def delete_face(self, user_id: int, name: str) -> bool:
        """Yuzni o'chirish."""
        if user_id not in self.known_faces:
            return False
        
        original_count = len(self.known_faces[user_id])
        self.known_faces[user_id] = [
            f for f in self.known_faces[user_id] 
            if f['name'].lower() != name.lower()
        ]
        
        if len(self.known_faces[user_id]) < original_count:
            self._save_known_faces()
            return True
        return False
    
    def search_by_face(self, user_id: int, target_frame: np.ndarray,
                       frames: List[np.ndarray]) -> List[dict]:
        """Target yuzni boshqa frame'lardan qidirish."""
        results = []
        
        target_faces = self.detect_faces(target_frame)
        if not target_faces:
            return results
        
        target_embedding = self.extract_embedding(target_frame, target_faces[0])
        if target_embedding is None:
            return results
        
        for i, frame in enumerate(frames):
            faces = self.detect_faces(frame)
            for face in faces:
                embedding = self.extract_embedding(frame, face)
                if embedding is not None:
                    is_match, confidence = self.compare_faces(target_embedding, embedding)
                    if is_match:
                        results.append({
                            'frame_index': i,
                            'confidence': confidence,
                            'bbox': face.bbox
                        })
        
        return sorted(results, key=lambda x: x['confidence'], reverse=True)


# Global instance
face_recognizer = FaceRecognizer()
