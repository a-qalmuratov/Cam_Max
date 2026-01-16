"""
AI Search Engine for video archives.
Combines NLP parsing, object detection, and result ranking.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from database.models import db
from utils.logger import logger


class SearchEngine:
    """AI-powered video search engine."""
    
    def __init__(self):
        self.last_search_context = {}
    
    def search(self, query: str, user_id: int, context: Dict = None) -> Dict[str, Any]:
        """
        Execute search query.
        
        Returns:
            {
                'success': bool,
                'query_params': parsed parameters,
                'results': list of matches,
                'timeline': event timeline,
                'confidence': search confidence,
                'needs_clarification': bool,
                'clarification_question': optional question
            }
        """
        from nlp.uzbek_parser import query_parser
        
        start_time = datetime.now()
        
        # Parse query
        params = query_parser.parse(query)
        
        # Merge with context if provided
        if context:
            params = self._merge_context(params, context)
        
        # Check if we need clarification
        if params['confidence'] < 0.3 or params['missing_params']:
            followup = query_parser.generate_followup_question(params)
            if followup:
                return {
                    'success': False,
                    'query_params': params,
                    'results': [],
                    'timeline': [],
                    'confidence': params['confidence'],
                    'needs_clarification': True,
                    'clarification_question': followup
                }
        
        # Get user's cameras
        user = db.get_user(user_id)
        org_id = user.get('organization_id') if user else None
        cameras = db.get_cameras_by_organization(org_id) if org_id else []
        
        # Filter cameras if specified
        if params['cameras']:
            cameras = [c for c in cameras if c['id'] in params['cameras']]
        elif params['locations']:
            # Match by location keywords in camera name
            cameras = [c for c in cameras if any(
                loc in c['name'].lower() for loc in params['locations']
            )]
        
        # Execute search
        results = self._execute_search(params, cameras)
        
        # Build timeline
        timeline = self._build_timeline(results)
        
        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            'success': True,
            'query_params': params,
            'results': results,
            'timeline': timeline,
            'confidence': params['confidence'],
            'needs_clarification': False,
            'clarification_question': None,
            'response_time_ms': round(response_time)
        }
    
    def _merge_context(self, params: Dict, context: Dict) -> Dict:
        """Merge new params with previous context."""
        merged = params.copy()
        
        # Add missing camera from context
        if not merged['cameras'] and context.get('cameras'):
            merged['cameras'] = context['cameras']
            merged['missing_params'] = [p for p in merged['missing_params'] if p != 'camera']
        
        # Add missing objects from context
        if not merged['objects'] and context.get('objects'):
            merged['objects'] = context['objects']
        
        # Recalculate confidence
        score = 0.0
        if merged['objects']:
            score += 0.25
        if merged['colors']:
            score += 0.15
        if merged['actions']:
            score += 0.20
        if merged['cameras'] or merged['locations']:
            score += 0.25
        
        merged['confidence'] = min(score + 0.15, 1.0)
        
        return merged
    
    def _execute_search(self, params: Dict, cameras: List[Dict]) -> List[Dict]:
        """Execute search in detection events."""
        results = []
        
        # Get time range
        time_range = params.get('time_range', {})
        start_time = time_range.get('start', datetime.now() - timedelta(hours=24))
        end_time = time_range.get('end', datetime.now())
        
        # Search objects in database
        objects_to_find = params.get('objects', [])
        colors_to_find = params.get('colors', [])
        
        for camera in cameras:
            try:
                # Get detection events for this camera in time range
                from database.v2_models import v2db
                events = v2db.get_detection_events(
                    camera_id=camera['id'],
                    start_time=start_time,
                    end_time=end_time
                )
                
                # Filter by objects and colors
                for event in events:
                    match_score = 0.0
                    
                    # Check object match
                    event_object = event.get('object_type', '').lower()
                    if objects_to_find:
                        if any(obj in event_object for obj in objects_to_find):
                            match_score += 0.5
                    
                    # Check color match
                    event_color = event.get('object_color', '').lower()
                    if colors_to_find:
                        if any(color in event_color for color in colors_to_find):
                            match_score += 0.3
                    
                    # Check action match
                    event_action = event.get('action', '').lower()
                    if params.get('actions'):
                        if any(act in event_action for act in params['actions']):
                            match_score += 0.2
                    
                    if match_score > 0:
                        results.append({
                            'camera_id': camera['id'],
                            'camera_name': camera['name'],
                            'timestamp': event.get('timestamp'),
                            'object_type': event_object,
                            'object_color': event_color,
                            'action': event_action,
                            'confidence': event.get('confidence', 0.0),
                            'match_score': match_score,
                            'person_id': event.get('person_id'),
                            'video_path': event.get('video_path'),
                            'snapshot_path': event.get('snapshot_path')
                        })
            except Exception as e:
                logger.error(f"Search error for camera {camera['id']}: {e}")
        
        # Sort by match score and timestamp
        results.sort(key=lambda x: (-x['match_score'], x.get('timestamp', '')))
        
        return results[:20]  # Limit to top 20 results
    
    def _build_timeline(self, results: List[Dict]) -> List[Dict]:
        """Build event timeline from results."""
        timeline = []
        
        # Group by person_id if available
        person_events = {}
        for r in results:
            person_id = r.get('person_id', 'unknown')
            if person_id not in person_events:
                person_events[person_id] = []
            person_events[person_id].append(r)
        
        # Build timeline for each person
        for person_id, events in person_events.items():
            events.sort(key=lambda x: x.get('timestamp', ''))
            
            for i, event in enumerate(events):
                timestamp = event.get('timestamp', '')
                if isinstance(timestamp, datetime):
                    time_str = timestamp.strftime('%H:%M:%S')
                else:
                    time_str = str(timestamp)[:8] if timestamp else ''
                
                # Determine action description
                action = event.get('action', '')
                obj = event.get('object_type', '')
                color = event.get('object_color', '')
                camera = event.get('camera_name', '')
                
                if action == 'kirdi':
                    desc = f"Kirdi ({camera})"
                elif action == 'chiqdi':
                    desc = f"Chiqdi ({camera})"
                elif action == 'oldi' and obj:
                    color_str = f"{color} " if color else ""
                    desc = f"{color_str}{obj} oldi"
                elif action == 'qoydi' and obj:
                    desc = f"{obj} qo'ydi"
                else:
                    desc = f"{action or 'Hodisa'} - {camera}"
                
                timeline.append({
                    'time': time_str,
                    'description': desc,
                    'person_id': person_id,
                    'camera': camera,
                    'event_type': action or 'detection'
                })
        
        # Sort timeline by time
        timeline.sort(key=lambda x: x['time'])
        
        return timeline
    
    def get_evidence(self, result: Dict) -> Dict[str, Any]:
        """Get evidence package for a search result."""
        evidence = {
            'videos': [],
            'screenshots': [],
            'timeline': [],
            'description_uz': ''
        }
        
        # Get video clip if available
        if result.get('video_path'):
            evidence['videos'].append(result['video_path'])
        
        # Get screenshot if available  
        if result.get('snapshot_path'):
            evidence['screenshots'].append(result['snapshot_path'])
        
        # Build description
        timestamp = result.get('timestamp', '')
        if isinstance(timestamp, datetime):
            time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = str(timestamp) if timestamp else 'Noma\'lum vaqt'
        
        camera = result.get('camera_name', 'Noma\'lum kamera')
        obj = result.get('object_type', '')
        color = result.get('object_color', '')
        action = result.get('action', '')
        
        desc_parts = []
        desc_parts.append(f"📹 Kamera: {camera}")
        desc_parts.append(f"⏰ Vaqt: {time_str}")
        
        if obj:
            color_str = f"{color} " if color else ""
            desc_parts.append(f"🎯 Object: {color_str}{obj}")
        
        if action:
            desc_parts.append(f"⚡ Harakat: {action}")
        
        evidence['description_uz'] = "\n".join(desc_parts)
        
        return evidence


# Global instance
search_engine = SearchEngine()
