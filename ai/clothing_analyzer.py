"""
Clothing Recognition Module
Kiyim tahlili va natural language qidirish (CLIP asosida).
"""
import os
import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from utils.logger import logger

# Try to import transformers for CLIP
try:
    from transformers import CLIPProcessor, CLIPModel
    import torch
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    logger.warning("Transformers/CLIP not installed.")


@dataclass
class ClothingInfo:
    """Kiyim ma'lumoti."""
    colors: List[str]
    types: List[str]
    description: str
    confidence: float
    bbox: tuple = None


class ClothingAnalyzer:
    """CLIP yordamida kiyim tahlili."""
    
    # Color names
    COLORS = [
        "qizil", "ko'k", "yashil", "sariq", "oq", "qora",
        "kulrang", "jigarrang", "pushti", "binafsha",
        "red", "blue", "green", "yellow", "white", "black",
        "gray", "brown", "pink", "purple", "orange"
    ]
    
    # Clothing types
    CLOTHING_TYPES = [
        "ko'ylak", "shim", "kurtka", "palto", "futbolka",
        "jemper", "kostyum", "sport kiyim", "ko'ynak",
        "shirt", "pants", "jacket", "coat", "t-shirt",
        "sweater", "suit", "sportswear", "dress", "jeans"
    ]
    
    def __init__(self):
        self.model = None
        self.processor = None
        self._initialized = False
    
    def _init_model(self):
        """CLIP modelini yuklash."""
        if self._initialized or not CLIP_AVAILABLE:
            return
        
        try:
            logger.info("Loading CLIP model...")
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self._initialized = True
            logger.info("CLIP model loaded successfully")
        except Exception as e:
            logger.error(f"CLIP model loading error: {e}")
    
    def analyze_clothing(self, person_crop: np.ndarray) -> ClothingInfo:
        """Kiyimni tahlil qilish."""
        colors = self._detect_colors(person_crop)
        types = []
        description = ""
        confidence = 0.0
        
        if CLIP_AVAILABLE:
            self._init_model()
            
            if self.model and self.processor:
                try:
                    # Convert BGR to RGB
                    rgb_image = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
                    
                    # Generate clothing type queries
                    type_queries = [f"a person wearing {t}" for t in self.CLOTHING_TYPES]
                    
                    # Process with CLIP
                    inputs = self.processor(
                        text=type_queries,
                        images=rgb_image,
                        return_tensors="pt",
                        padding=True
                    )
                    
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                        logits = outputs.logits_per_image
                        probs = logits.softmax(dim=1)
                    
                    # Get top matches
                    top_indices = probs[0].topk(3).indices.tolist()
                    
                    for idx in top_indices:
                        types.append(self.CLOTHING_TYPES[idx])
                    
                    confidence = probs[0].max().item()
                    
                except Exception as e:
                    logger.error(f"CLIP analysis error: {e}")
        
        # Build description
        if colors and types:
            description = f"{colors[0]} {types[0]}"
        elif colors:
            description = f"{colors[0]} kiyim"
        elif types:
            description = types[0]
        else:
            description = "noma'lum kiyim"
        
        return ClothingInfo(
            colors=colors,
            types=types,
            description=description,
            confidence=confidence
        )
    
    def _detect_colors(self, image: np.ndarray) -> List[str]:
        """Dominant ranglarni aniqlash."""
        colors = []
        
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Color ranges in HSV
            color_ranges = {
                "qizil": [(0, 100, 100), (10, 255, 255)],
                "sariq": [(15, 100, 100), (35, 255, 255)],
                "yashil": [(35, 100, 100), (85, 255, 255)],
                "ko'k": [(85, 100, 100), (130, 255, 255)],
                "binafsha": [(130, 100, 100), (160, 255, 255)],
                "pushti": [(160, 100, 100), (180, 255, 255)],
            }
            
            # Check for black, white, gray (by saturation and value)
            mean_saturation = hsv[:, :, 1].mean()
            mean_value = hsv[:, :, 2].mean()
            
            if mean_value < 50:
                colors.append("qora")
            elif mean_value > 200 and mean_saturation < 50:
                colors.append("oq")
            elif mean_saturation < 50:
                colors.append("kulrang")
            else:
                # Check colored ranges
                total_pixels = image.shape[0] * image.shape[1]
                
                for color_name, (lower, upper) in color_ranges.items():
                    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                    ratio = cv2.countNonZero(mask) / total_pixels
                    
                    if ratio > 0.1:  # At least 10%
                        colors.append(color_name)
            
            if not colors:
                colors.append("rangli")
                
        except Exception as e:
            logger.error(f"Color detection error: {e}")
            colors = ["noma'lum"]
        
        return colors[:3]  # Max 3 colors
    
    def search_by_description(self, query: str, 
                              person_crops: List[np.ndarray]) -> List[dict]:
        """Natural language qidirish."""
        results = []
        
        if not CLIP_AVAILABLE or not person_crops:
            return results
        
        self._init_model()
        
        if not self.model or not self.processor:
            return results
        
        try:
            # Prepare all images
            rgb_images = [cv2.cvtColor(crop, cv2.COLOR_BGR2RGB) for crop in person_crops]
            
            # Process with CLIP
            inputs = self.processor(
                text=[query],
                images=rgb_images,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits_per_text  # (1, num_images)
                probs = logits.softmax(dim=1)
            
            # Rank all images
            scores = probs[0].tolist()
            
            for i, (crop, score) in enumerate(zip(person_crops, scores)):
                if score > 0.1:  # Threshold
                    results.append({
                        'index': i,
                        'score': score,
                        'crop': crop
                    })
            
            # Sort by score
            results = sorted(results, key=lambda x: x['score'], reverse=True)
            
        except Exception as e:
            logger.error(f"CLIP search error: {e}")
        
        return results
    
    def find_person_by_clothing(self, description: str, 
                                 frames: List[np.ndarray],
                                 person_detector=None) -> List[dict]:
        """Kiyim tavsifi bo'yicha odam topish."""
        results = []
        
        if person_detector is None:
            return results
        
        all_crops = []
        crop_info = []
        
        # Extract all persons from all frames
        for frame_idx, frame in enumerate(frames):
            detections = person_detector.detect(frame)
            
            for det in detections:
                if det.get('class') in ['person', 'odam']:
                    bbox = det.get('bbox', (0, 0, 0, 0))
                    x, y, w, h = bbox
                    
                    # Extract crop
                    crop = frame[y:y+h, x:x+w]
                    if crop.size > 0:
                        all_crops.append(crop)
                        crop_info.append({
                            'frame_idx': frame_idx,
                            'bbox': bbox
                        })
        
        if not all_crops:
            return results
        
        # Search by description
        matches = self.search_by_description(description, all_crops)
        
        for match in matches:
            idx = match['index']
            results.append({
                'frame_idx': crop_info[idx]['frame_idx'],
                'bbox': crop_info[idx]['bbox'],
                'score': match['score'],
                'crop': all_crops[idx]
            })
        
        return results
    
    def get_clothing_text(self, info: ClothingInfo, language: str = "uz") -> str:
        """Kiyim ma'lumotini matn formatida."""
        if language == "uz":
            colors = ", ".join(info.colors) if info.colors else "noma'lum rang"
            types = ", ".join(info.types) if info.types else "noma'lum kiyim"
            return f"Rang: {colors}\nKiyim: {types}"
        else:
            colors = ", ".join(info.colors) if info.colors else "unknown color"
            types = ", ".join(info.types) if info.types else "unknown clothing"
            return f"Color: {colors}\nClothing: {types}"


# Global instance
clothing_analyzer = ClothingAnalyzer()
