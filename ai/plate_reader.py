"""
License Plate Reader Module
Avtomobil raqamlarini o'qish.
"""
import os
import re
import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from utils.logger import logger

# Try to import EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("EasyOCR not installed.")


class PlateRegion:
    """Avtomobil raqami hududi."""
    def __init__(self, bbox: tuple, image: np.ndarray = None):
        self.bbox = bbox  # (x, y, w, h)
        self.image = image
        self.text = None
        self.confidence = 0.0


class PlateReader:
    """Avtomobil raqamlarini o'qish."""
    
    # O'zbek raqam formatlari
    UZBEK_PLATE_PATTERNS = [
        r'^\d{2}[A-Z]\d{3}[A-Z]{2}$',  # 01A001AA (yangi)
        r'^\d{2}\s?[A-Z]\s?\d{3}\s?[A-Z]{2}$',  # spaces bilan
        r'^[A-Z]\d{3}[A-Z]{2}\d{2}$',  # Eski format
    ]
    
    def __init__(self, data_dir: str = "data/plates"):
        self.data_dir = data_dir
        self.reader = None
        self.plates_db: List[dict] = []
        os.makedirs(data_dir, exist_ok=True)
        
        if EASYOCR_AVAILABLE:
            try:
                # Lazy loading - yuklash faqat kerak bo'lganda
                self._reader_initialized = False
            except Exception as e:
                logger.error(f"EasyOCR init error: {e}")
    
    def _init_reader(self):
        """EasyOCR reader'ni boshlash."""
        if not self._reader_initialized and EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(['en'], gpu=False)
                self._reader_initialized = True
                logger.info("EasyOCR initialized")
            except Exception as e:
                logger.error(f"EasyOCR init error: {e}")
    
    def detect_plates(self, frame: np.ndarray) -> List[PlateRegion]:
        """Frame'dan raqam hududlarini aniqlash."""
        plates = []
        
        # Grayscale convert
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Bilateral filter for noise reduction
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Edge detection
        edged = cv2.Canny(gray, 30, 200)
        
        # Find contours
        contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
        
        for contour in contours:
            # Approximate the contour
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.018 * peri, True)
            
            # Raqam plakasi to'rtburchak bo'lishi kerak
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Aspect ratio check (raqam uzun bo'ladi)
                aspect_ratio = w / h
                if 2.0 < aspect_ratio < 6.0:
                    # Minimal size check
                    if w > 60 and h > 15:
                        plate_img = frame[y:y+h, x:x+w]
                        plates.append(PlateRegion(
                            bbox=(x, y, w, h),
                            image=plate_img
                        ))
        
        return plates[:5]  # Max 5 ta
    
    def read_plate(self, region: PlateRegion) -> str:
        """Raqam hududidan matnni o'qish."""
        if region.image is None:
            return ""
        
        self._init_reader()
        
        if not self.reader:
            return ""
        
        try:
            # Preprocess
            img = region.image.copy()
            
            # Resize for better OCR
            if img.shape[1] < 200:
                scale = 200 / img.shape[1]
                img = cv2.resize(img, None, fx=scale, fy=scale)
            
            # Convert to grayscale
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Threshold
            _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR
            results = self.reader.readtext(img)
            
            if results:
                # Combine all text
                texts = [r[1].upper().replace(' ', '') for r in results]
                combined = ''.join(texts)
                
                # Clean up
                combined = re.sub(r'[^A-Z0-9]', '', combined)
                
                region.text = combined
                region.confidence = max(r[2] for r in results) if results else 0.0
                
                return combined
                
        except Exception as e:
            logger.error(f"Plate OCR error: {e}")
        
        return ""
    
    def validate_uzbek_plate(self, text: str) -> Tuple[bool, str]:
        """O'zbek raqam formatini tekshirish."""
        if not text:
            return False, ""
        
        # Clean text
        clean = text.upper().replace(' ', '').replace('-', '')
        
        for pattern in self.UZBEK_PLATE_PATTERNS:
            if re.match(pattern, clean):
                return True, clean
        
        # Partial match - kamida format o'xshash
        if len(clean) >= 7 and clean[:2].isdigit() and clean[2].isalpha():
            return True, clean
        
        return False, clean
    
    def process_frame(self, frame: np.ndarray) -> List[dict]:
        """Frame'dan barcha raqamlarni o'qish."""
        results = []
        
        plates = self.detect_plates(frame)
        
        for plate in plates:
            text = self.read_plate(plate)
            is_valid, clean_text = self.validate_uzbek_plate(text)
            
            if text:
                results.append({
                    'text': clean_text,
                    'raw_text': text,
                    'is_valid': is_valid,
                    'confidence': plate.confidence,
                    'bbox': plate.bbox,
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def save_plate(self, camera_id: int, plate_text: str, 
                   frame: np.ndarray = None, category: str = "detected"):
        """Raqamni database'ga saqlash."""
        plate_data = {
            'plate_number': plate_text,
            'camera_id': camera_id,
            'timestamp': datetime.now().isoformat(),
            'category': category
        }
        
        # Save image if provided
        if frame is not None:
            img_path = os.path.join(
                self.data_dir, 
                f"{plate_text}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            )
            cv2.imwrite(img_path, frame)
            plate_data['image_path'] = img_path
        
        self.plates_db.append(plate_data)
        return plate_data
    
    def search_by_plate(self, plate_number: str) -> List[dict]:
        """Raqam bo'yicha qidirish."""
        clean = plate_number.upper().replace(' ', '').replace('-', '')
        
        results = []
        for plate in self.plates_db:
            if clean in plate['plate_number']:
                results.append(plate)
        
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    def get_recent_plates(self, camera_id: int = None, limit: int = 20) -> List[dict]:
        """Oxirgi raqamlar."""
        plates = self.plates_db
        
        if camera_id:
            plates = [p for p in plates if p.get('camera_id') == camera_id]
        
        return sorted(plates, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_unknown_plates(self, user_id: int = None) -> List[dict]:
        """Notanish raqamlar."""
        return [p for p in self.plates_db if p.get('category') == 'unknown']


# Global instance
plate_reader = PlateReader()
