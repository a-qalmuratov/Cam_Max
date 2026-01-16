"""Natural Language Query processing for Uzbek."""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.logger import logger

class UzbekQueryParser:
    """Parse Uzbek natural language queries."""
    
    # Keywords
    CAMERA_KEYWORDS = ['kamera', 'kameradan', 'kamerada']
    TIME_KEYWORDS = {
        'bugun': 0,
        'kecha': 1,
        'ertalab': 'morning',
        'tushdan keyin': 'afternoon',
        'kechқurun': 'evening'
    }
    
    COLORS = {
        'qizil': 'red',
        'qora': 'black',
        'oq': 'white',
        'ko\'k': 'blue',
        'yashil': 'green',
        'sariq': 'yellow'
    }
    
    OBJECTS = {
        'sumka': 'handbag',
        'telefon': 'cell phone',
        'noutbuk': 'laptop',
        'rукzak': 'backpack',
        'kitob': 'book',
        'butilka': 'bottle',
        'stakan': 'cup'
    }
    
    ACTIONS = {
        'oldi': 'took',
        'qo\'ydi': 'placed',
        'o\'tdi': 'passed',
        'kirdi': 'entered',
        'chiqdi': 'exited',
        'yaqinlashdi': 'approached'
    }
    
    def parse(self, query: str) -> Dict:
        """
        Parse Uzbek query into structured format.
        
        Example:
        "3-kamera qaragan xonadagi stolda qizil sumka bor edi uni kim oldi?"
        
        Returns:
        {
            'camera': 3,
            'location': 'stol',
            'object': {'type': 'sumka', 'color': 'qizil'},
            'action': 'oldi',
            'time_range': (start, end)
        }
        """
        query = query.lower()
        result = {}
        
        # Extract camera number
        camera_match = re.search(r'(\d+)[-\s]?kamera', query)
        if camera_match:
            result['camera'] = int(camera_match.group(1))
        
        # Extract color
        for uz_color, en_color in self.COLORS.items():
            if uz_color in query:
                result['color'] = uz_color
                break
        
        # Extract object
        for uz_obj, en_obj in self.OBJECTS.items():
            if uz_obj in query:
                result['object'] = uz_obj
                result['object_en'] = en_obj
                break
        
        # Extract action
        for uz_action, en_action in self.ACTIONS.items():
            if uz_action in query:
                result['action'] = uz_action
                result['action_en'] = en_action
                break
        
        # Extract time
        result['time_range'] = self._parse_time(query)
        
        # Extract location keywords
        if 'stolda' in query or 'stol' in query:
            result['location'] = 'stol'
        elif 'polda' in query:
            result['location'] = 'pol'
        elif 'kassa' in query:
            result['location'] = 'kassa'
        
        logger.info(f"Parsed query: {result}")
        return result
    
    def _parse_time(self, query: str) -> Tuple[datetime, datetime]:
        """Parse time references."""
        now = datetime.now()
        
        if 'bugun' in query:
            start = now.replace(hour=0, minute=0, second=0)
            end = now
            if 'ertalab' in query:
                start = now.replace(hour=6, minute=0)
                end = now.replace(hour=12, minute=0)
            elif 'tushdan keyin' in query:
                start = now.replace(hour=12, minute=0)
                end = now.replace(hour=18, minute=0)
            elif 'kechqurun' in query:
                start = now.replace(hour=18, minute=0)
                end = now
        elif 'kecha' in query:
            yesterday = now - timedelta(days=1)
            start = yesterday.replace(hour=0, minute=0, second=0)
            end = yesterday.replace(hour=23, minute=59, second=59)
        else:
            # Default: last 24 hours
            start = now - timedelta(hours=24)
            end = now
        
        return (start, end)

class VideoSearchEngine:
    """Search video archives based on queries."""
    
    def __init__(self):
        self.parser = UzbekQueryParser()
    
    def search(self, query: str, user_id: int) -> Dict:
        """
        Search for events matching query.
        
        Returns:
        {
            'query_params': {...},
            'results': [...],
            'evidence': {...}
        }
        """
        start_time = datetime.now()
        
        # Parse query
        params = self.parser.parse(query)
        
        # Search database
        results = self._search_events(params)
        
        # Build evidence
        evidence = self._build_evidence(results, params)
        
        # Log query
        response_time = int((datetime.now() - start_time).total_seconds() * 1000)
        from database.v2_models import v2db
        v2db.add_query(
            user_id=user_id,
            query_text=query,
            query_params=params,
            results_count=len(results),
            response_time_ms=response_time
        )
        
        return {
            'query_params': params,
            'results': results,
            'evidence': evidence,
            'response_time_ms': response_time
        }
    
    def _search_events(self, params: Dict) -> List[Dict]:
        """Search detection events matching parameters."""
        # This is simplified - in production, use proper SQL queries
        from database.v2_models import v2db
        
        results = []
        
        # For now, return placeholder
        # TODO: Implement actual database search
        logger.info(f"Searching events with params: {params}")
        
        return results
    
    def _build_evidence(self, results: List[Dict], params: Dict) -> Dict:
        """Build evidence package with videos and screenshots."""
        evidence = {
            'timeline': [],
            'videos': [],
            'screenshots': [],
            'description_uz': ''
        }
        
        # Build timeline
        if results:
            for result in results:
                evidence['timeline'].append({
                    'time': result.get('timestamp'),
                    'description': result.get('description_uzbek')
                })
        
        # Build Uzbek description
        if params.get('object'):
            color = params.get('color', '')
            obj = params.get('object')
            action = params.get('action', 'topildi')
            
            evidence['description_uz'] = f"{color} {obj} {action}"
        
        return evidence

# Global search engine
search_engine = VideoSearchEngine()
