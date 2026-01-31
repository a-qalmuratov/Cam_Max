"""
Uzbek NLP Query Parser for video search.
Extracts objects, colors, time, cameras, and actions from natural language.
"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from utils.logger import logger


class UzbekDictionary:
    """Uzbek language dictionary for NLP."""
    
    # Objects
    OBJECTS = {
        'sumka': ['sumka', 'xalta', 'portfel', 'bag', 'backpack'],
        'telefon': ['telefon', 'mobil', 'smartfon', 'phone'],
        'noutbuk': ['noutbuk', 'kompyuter', 'laptop', 'computer'],
        'mashina': ['mashina', 'avtomobil', 'car', 'avto'],
        'odam': ['odam', 'kishi', 'shaxs', 'person', 'inson'],
        'ayol': ['ayol', 'xotin', 'woman', 'qiz'],
        'erkak': ['erkak', 'yigit', 'man', 'bola'],
        'bola': ['bola', 'farzand', 'child', 'kid'],
        'stakan': ['stakan', 'chashka', 'kofe', 'cup', 'glass'],
        'kalit': ['kalit', 'key', 'keys'],
        'karta': ['karta', 'card', 'kredit'],
        'pul': ['pul', 'naqd', 'money', 'cash'],
        'quti': ['quti', 'korobka', 'box', 'package'],
        'velosiped': ['velosiped', 'bike', 'bicycle'],
    }
    
    # Colors
    COLORS = {
        'qizil': ['qizil', 'red', 'qirmizi'],
        'ko\'k': ['kok', "ko'k", 'blue', 'moviy'],
        'yashil': ['yashil', 'green'],
        'sariq': ['sariq', 'yellow'],
        'oq': ['oq', 'white', 'oppoq'],
        'qora': ['qora', 'black'],
        'kulrang': ['kulrang', 'gray', 'grey'],
        'jigarrang': ['jigarrang', 'brown', 'qo\'ng\'ir'],
        'pushti': ['pushti', 'pink'],
        'binafsha': ['binafsha', 'purple', 'siyoh'],
    }
    
    # Actions
    ACTIONS = {
        'oldi': ['oldi', 'olgan', 'olish', 'took', 'grab'],
        'qoydi': ['qoydi', "qo'ydi", 'qo\'ygan', 'put', 'place'],
        'kirdi': ['kirdi', 'kirgan', 'enter', 'came'],
        'chiqdi': ['chiqdi', 'chiqgan', 'exit', 'left'],
        'yurdi': ['yurdi', 'yurgan', 'walk', 'walking'],
        'yugurdi': ['yugurdi', 'run', 'running'],
        'o\'tirdi': ['otirdi', "o'tirdi", 'sit', 'sitting'],
        'turdi': ['turdi', 'stand', 'standing'],
        'gaplashdi': ['gaplashdi', 'talk', 'speaking'],
        'qaradi': ['qaradi', 'look', 'looking'],
    }
    
    # Time expressions
    TIME_EXPRESSIONS = {
        'bugun': ['bugun', 'today', 'shu kun'],
        'kecha': ['kecha', 'yesterday', 'o\'tgan kun'],
        'ertaga': ['ertaga', 'tomorrow'],
        'ertalab': ['ertalab', 'morning', 'tong'],
        'tushda': ['tushda', 'tush', 'noon', 'peshin'],
        'kechqurun': ['kechqurun', 'kech', 'evening'],
        'tunda': ['tunda', 'tun', 'night'],
        'hozir': ['hozir', 'now', 'ayni paytda'],
        'soat': ['soat', 'hour', 'o\'clock'],
        'daqiqa': ['daqiqa', 'minute', 'min'],
    }
    
    # Location/Camera keywords
    LOCATIONS = {
        'kirish': ['kirish', 'entrance', 'eshik'],
        'chiqish': ['chiqish', 'exit', 'tashqari'],
        'kassa': ['kassa', 'cashier', 'tolov'],
        'zal': ['zal', 'hall', 'xona'],
        'koridor': ['koridor', 'corridor', 'yo\'lak'],
        'oshxona': ['oshxona', 'kitchen'],
        'ofis': ['ofis', 'office', 'kabinet'],
        'ombor': ['ombor', 'warehouse', 'sklad'],
        'parking': ['parking', 'avtoturargoh'],
    }


class QueryParser:
    """Parse natural language queries to structured search parameters."""
    
    def __init__(self):
        self.dict = UzbekDictionary()
    
    def parse(self, query: str) -> Dict[str, Any]:
        """Parse query and extract search parameters."""
        query_lower = query.lower()
        
        result = {
            'original_query': query,
            'objects': self._extract_objects(query_lower),
            'colors': self._extract_colors(query_lower),
            'actions': self._extract_actions(query_lower),
            'time_range': self._extract_time_range(query_lower),
            'cameras': self._extract_cameras(query_lower),
            'locations': self._extract_locations(query_lower),
            'confidence': 0.0,
            'missing_params': []
        }
        
        # Calculate confidence
        result['confidence'] = self._calculate_confidence(result)
        
        # Identify missing params
        result['missing_params'] = self._get_missing_params(result)
        
        return result
    
    def _extract_objects(self, query: str) -> List[str]:
        """Extract objects from query."""
        found = []
        for obj_key, variants in self.dict.OBJECTS.items():
            for variant in variants:
                if variant in query:
                    if obj_key not in found:
                        found.append(obj_key)
                    break
        return found
    
    def _extract_colors(self, query: str) -> List[str]:
        """Extract colors from query."""
        found = []
        for color_key, variants in self.dict.COLORS.items():
            for variant in variants:
                if variant in query:
                    if color_key not in found:
                        found.append(color_key)
                    break
        return found
    
    def _extract_actions(self, query: str) -> List[str]:
        """Extract actions from query."""
        found = []
        for action_key, variants in self.dict.ACTIONS.items():
            for variant in variants:
                if variant in query:
                    if action_key not in found:
                        found.append(action_key)
                    break
        return found
    
    def _extract_time_range(self, query: str) -> Dict[str, datetime]:
        """Extract time range from query."""
        now = datetime.now()
        result = {'start': now - timedelta(hours=24), 'end': now, 'label': "So'nggi 24 soat"}
        
        # Check for specific time expressions
        if 'bugun' in query:
            result['start'] = now.replace(hour=0, minute=0, second=0)
            result['label'] = 'Bugun'
        elif 'kecha' in query:
            yesterday = now - timedelta(days=1)
            result['start'] = yesterday.replace(hour=0, minute=0, second=0)
            result['end'] = yesterday.replace(hour=23, minute=59, second=59)
            result['label'] = 'Kecha'
        
        # Check for time of day
        if 'ertalab' in query:
            result['start'] = result['start'].replace(hour=6, minute=0)
            result['end'] = result['start'].replace(hour=12, minute=0)
            result['label'] += ' ertalab'
        elif 'tushda' in query or 'tush' in query:
            result['start'] = result['start'].replace(hour=11, minute=0)
            result['end'] = result['start'].replace(hour=15, minute=0)
            result['label'] += ' tushda'
        elif 'kechqurun' in query or 'kech' in query:
            result['start'] = result['start'].replace(hour=17, minute=0)
            result['end'] = result['start'].replace(hour=23, minute=0)
            result['label'] += ' kechqurun'
        
        # Check for specific hour
        hour_match = re.search(r'(\d{1,2})\s*(soat|:)', query)
        if hour_match:
            hour = int(hour_match.group(1))
            if 0 <= hour <= 23:
                result['start'] = result['start'].replace(hour=hour, minute=0)
                result['end'] = result['start'].replace(hour=hour, minute=59)
                result['label'] = f"{hour}:00 atrofida"
        
        return result
    
    def _extract_cameras(self, query: str) -> List[int]:
        """Extract camera IDs from query."""
        cameras = []
        
        # Match patterns like "1-kamera", "kamera 2", "2-chi kamera"
        patterns = [
            r'(\d+)\s*-?\s*kamera',
            r'kamera\s*(\d+)',
            r'(\d+)\s*-?\s*chi\s*kamera',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                cam_id = int(match)
                if cam_id not in cameras:
                    cameras.append(cam_id)
        
        return cameras
    
    def _extract_locations(self, query: str) -> List[str]:
        """Extract locations from query."""
        found = []
        for loc_key, variants in self.dict.LOCATIONS.items():
            for variant in variants:
                if variant in query:
                    if loc_key not in found:
                        found.append(loc_key)
                    break
        return found
    
    def _calculate_confidence(self, params: Dict) -> float:
        """Calculate confidence score for parsed query."""
        score = 0.0
        
        if params['objects']:
            score += 0.25
        if params['colors']:
            score += 0.15
        if params['actions']:
            score += 0.20
        if params['cameras'] or params['locations']:
            score += 0.25
        if params['time_range'].get('label') != "So'nggi 24 soat":
            score += 0.15
        
        return min(score, 1.0)
    
    def _get_missing_params(self, params: Dict) -> List[str]:
        """Identify missing important parameters."""
        missing = []
        
        if not params['cameras'] and not params['locations']:
            missing.append('camera')
        if not params['objects'] and not params['actions']:
            missing.append('object_or_action')
        
        return missing
    
    def generate_followup_question(self, params: Dict) -> Optional[str]:
        """Generate follow-up question for missing parameters."""
        missing = params.get('missing_params', [])
        
        if 'camera' in missing:
            return "❓ Qaysi kamerada qidirish kerak?\n\nMasalan: 1-kamera, Kassa, Kirish"
        
        if 'object_or_action' in missing:
            return "❓ Nimani qidiryapsiz?\n\nMasalan: qizil sumka, odam kirdi, mashina keldi"
        
        return None


# Global instance
query_parser = QueryParser()
