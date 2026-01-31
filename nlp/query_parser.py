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
        """Parse time references with proper timezone handling (Asia/Tashkent -> UTC)."""
        try:
            from utils.access_control import time_helper
            return time_helper.parse_uzbek_time_phrase(query)
        except ImportError:
            # Fallback if access_control not available
            pass
        
        # Fallback to local time (not timezone-aware)
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
        
        # SECURITY: Filter results by user's organization
        try:
            from utils.access_control import access_control
            results = access_control.filter_results_by_org(user_id, results, 'camera_id')
            logger.info(f"Filtered to {len(results)} results for user {user_id}")
        except Exception as e:
            logger.warning(f"Could not filter by org: {e}")
        
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
        """Search detection events matching parameters - REAL DB SEARCH."""
        from database.models import db
        
        results = []
        logger.info(f"Searching events with params: {params}")
        
        try:
            # Get time range
            time_range = params.get('time_range')
            if time_range:
                start_time, end_time = time_range
            else:
                # Default last 24 hours
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=24)
            
            # Get camera filter
            camera_id = params.get('camera')
            
            # Get object type filter
            object_type = params.get('object_en')  # English version for DB
            
            # Get all recent detections
            if camera_id:
                detections = db.get_recent_detections(camera_id=camera_id, limit=100)
            else:
                detections = db.get_recent_detections(limit=100)
            
            # Make sure start/end times are naive for comparison with naive DB times
            # OR make DB times aware. We'll strip timezone for comparison.
            start_naive = start_time.replace(tzinfo=None) if start_time.tzinfo else start_time
            end_naive = end_time.replace(tzinfo=None) if end_time.tzinfo else end_time
            
            # Filter by time and object type
            for det in detections:
                det_time_str = det.get('detected_at')
                if det_time_str:
                    try:
                        # Parse DB datetime (may be naive or have timezone)
                        det_time_str_clean = det_time_str.replace('Z', '+00:00')
                        if '+' in det_time_str_clean or '-' in det_time_str_clean[10:]:
                            # Has timezone info
                            det_time = datetime.fromisoformat(det_time_str_clean)
                            det_time = det_time.replace(tzinfo=None)  # Strip for comparison
                        else:
                            # Naive datetime from DB (assume UTC)
                            det_time = datetime.fromisoformat(det_time_str_clean)
                        
                        if start_naive <= det_time <= end_naive:
                            # Filter by object type if specified
                            if object_type:
                                if det.get('object_type', '').lower() == object_type.lower():
                                    results.append({
                                        'camera_id': det.get('camera_id'),
                                        'timestamp': det_time_str,
                                        'object_type': det.get('object_type'),
                                        'confidence': det.get('confidence'),
                                        'image_path': det.get('image_path'),
                                        'description_uzbek': f"{det.get('object_type')} aniqlandi"
                                    })
                            else:
                                results.append({
                                    'camera_id': det.get('camera_id'),
                                    'timestamp': det_time_str,
                                    'object_type': det.get('object_type'),
                                    'confidence': det.get('confidence'),
                                    'image_path': det.get('image_path'),
                                    'description_uzbek': f"{det.get('object_type')} aniqlandi"
                                })
                    except Exception as e:
                        logger.warning(f"Time parse error for '{det_time_str}': {e}")
                        continue
            
            logger.info(f"Found {len(results)} matching events")
            
        except Exception as e:
            logger.error(f"Search error: {e}")
        
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
