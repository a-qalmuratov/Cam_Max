"""YOLOv8 Object Detector."""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from ultralytics import YOLO
from utils.config import YOLO_MODEL, CONFIDENCE_THRESHOLD, MODELS_DIR
from utils.logger import logger

class ObjectDetector:
    """YOLOv8-based object detection."""
    
    def __init__(self, model_name: str = YOLO_MODEL, confidence: float = CONFIDENCE_THRESHOLD):
        """Initialize detector."""
        self.model_name = model_name
        self.confidence = confidence
        self.model: Optional[YOLO] = None
        
        logger.info(f"Initializing YOLOv8 detector with model: {model_name}")
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model."""
        try:
            model_path = MODELS_DIR / self.model_name
            
            # If model doesn't exist, ultralytics will download it automatically
            if not model_path.exists():
                logger.info(f"Model not found. Downloading {self.model_name}...")
            
            self.model = YOLO(str(model_path) if model_path.exists() else self.model_name)
            logger.info("✅ YOLOv8 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> List[dict]:
        """
        Detect objects in frame.
        
        Returns:
            List of detections with format:
            {
                'class': class_name,
                'confidence': confidence_score,
                'bbox': (x, y, w, h)
            }
        """
        if self.model is None:
            logger.error("Model not loaded")
            return []
        
        try:
            # Run inference
            results = self.model(frame, conf=self.confidence, verbose=False)
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Convert to x, y, w, h format
                    x, y = int(x1), int(y1)
                    w, h = int(x2 - x1), int(y2 - y1)
                    
                    # Get class and confidence
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = self.model.names[cls]
                    
                    detection = {
                        'class': class_name,
                        'confidence': conf,
                        'bbox': (x, y, w, h)
                    }
                    
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return []
    
    def draw_detections(self, frame: np.ndarray, detections: List[dict]) -> np.ndarray:
        """Draw bounding boxes and labels on frame."""
        annotated_frame = frame.copy()
        
        for det in detections:
            x, y, w, h = det['bbox']
            class_name = det['class']
            confidence = det['confidence']
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            
            # Background for text
            cv2.rectangle(
                annotated_frame,
                (x, y - label_size[1] - 5),
                (x + label_size[0], y),
                (0, 255, 0),
                -1
            )
            
            # Text
            cv2.putText(
                annotated_frame,
                label,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                2
            )
        
        return annotated_frame
    
    def get_detection_summary(self, detections: List[dict]) -> str:
        """Get human-readable summary of detections in Uzbek."""
        if not detections:
            return "Hech narsa aniqlanmadi"
        
        # Count by class
        class_counts = {}
        for det in detections:
            class_name = det['class']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        # Translate common classes to Uzbek
        translations = {
            'person': 'odam',
            'backpack': 'ryukzak',
            'handbag': 'sumka',
            'bottle': 'butilka',
            'cup': 'stakan',
            'cell phone': 'telefon',
            'book': 'kitob',
            'laptop': 'noutbuk',
            'mouse': 'mouse',
            'keyboard': 'klaviatura',
            'chair': 'stul',
            'bag': 'sumka'
        }
        
        summary_parts = []
        for class_name, count in class_counts.items():
            uzbek_name = translations.get(class_name, class_name)
            summary_parts.append(f"{count} ta {uzbek_name}")
        
        return "Aniqlandi: " + ", ".join(summary_parts)

# Global detector instance
detector = ObjectDetector()
