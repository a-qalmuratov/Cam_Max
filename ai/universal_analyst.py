"""
Universal AI Video Analyst
Super aqlli bot - HAR QANDAY savolga javob beradi.
10 ta smart feature bilan (6 asosiy + 4 advanced).
"""
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ai.gemini_ai import gemini_ai
from ai.detector import detector
from camera.video_recorder import video_recorder
from database.models import db
from utils.logger import logger

# ========== ADVANCED AI MODULES ==========
try:
    from ai.face_recognition_module import face_recognizer
    FACE_RECOGNITION_ENABLED = True
except ImportError:
    FACE_RECOGNITION_ENABLED = False
    logger.warning("Face recognition module not available")

try:
    from ai.plate_reader import plate_reader
    PLATE_READER_ENABLED = True
except ImportError:
    PLATE_READER_ENABLED = False
    logger.warning("Plate reader module not available")

try:
    from ai.anomaly_detector import anomaly_detector, AnomalyType, AlertLevel
    ANOMALY_DETECTOR_ENABLED = True
except ImportError:
    ANOMALY_DETECTOR_ENABLED = False
    logger.warning("Anomaly detector module not available")

try:
    from ai.clothing_analyzer import clothing_analyzer
    CLOTHING_ANALYZER_ENABLED = True
except ImportError:
    CLOTHING_ANALYZER_ENABLED = False
    logger.warning("Clothing analyzer module not available")

# ========== ADVANCED AI MODULES - PART 2 ==========
try:
    from ai.object_tracker import object_tracker
    OBJECT_TRACKER_ENABLED = True
except ImportError:
    OBJECT_TRACKER_ENABLED = False
    logger.warning("Object tracker module not available")

try:
    from ai.zone_monitor import zone_monitor, ZoneType
    ZONE_MONITOR_ENABLED = True
except ImportError:
    ZONE_MONITOR_ENABLED = False
    logger.warning("Zone monitor module not available")

try:
    from ai.auto_analyzer import auto_analyzer
    AUTO_ANALYZER_ENABLED = True
except ImportError:
    AUTO_ANALYZER_ENABLED = False
    logger.warning("Auto analyzer module not available")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 1: Conversation Context - Kontekstni Eslab Qolish
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ConversationContext:
    """Suhbat kontekstini saqlash - oldingi savollarni eslaydi."""
    
    def __init__(self):
        self.contexts: Dict[int, dict] = {}  # user_id -> context
    
    def save_context(self, user_id: int, query: str, result: dict):
        """Oxirgi savol va javobni saqlash."""
        self.contexts[user_id] = {
            'last_query': query,
            'last_result': result,
            'last_camera': result.get('camera_id'),
            'last_time_range': result.get('time_range'),
            'last_objects': result.get('objects', []),
            'timestamp': datetime.now()
        }
    
    def get_context(self, user_id: int) -> Optional[dict]:
        """Oldingi kontekstni olish (10 minut ichida)."""
        ctx = self.contexts.get(user_id)
        if ctx and (datetime.now() - ctx['timestamp']).seconds < 600:
            return ctx
        return None
    
    def merge_with_context(self, user_id: int, new_query: dict) -> dict:
        """Yangi savolni oldingi kontekst bilan birlashtirish."""
        ctx = self.get_context(user_id)
        if not ctx:
            return new_query
        
        # Agar kamera ko'rsatilmagan bo'lsa - oldingiini ishlatish
        if not new_query.get('camera_id') and ctx.get('last_camera'):
            new_query['camera_id'] = ctx['last_camera']
        
        # "Oxirgi" yoki "u" kabi so'zlar uchun
        if new_query.get('refers_to_previous'):
            new_query['previous_result'] = ctx['last_result']
        
        return new_query


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 2: Typo Correction - Xatolikni Tuzatish
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TYPO_CORRECTION_PROMPT = '''
Foydalanuvchi savoli: "{query}"

Bu savolda yozuv xatolari bo'lishi mumkin. O'zbek/karakalpak tilida.
To'g'rilangan versiyasini qaytar.

Misol xatolar:
- "keca" → "kecha"
- "kledi" → "keldi"  
- "bgun" → "bugun"
- "mashna" → "mashina"
- "adam" → "odam"
- "oxrgi" → "oxirgi"
- "nchta" → "nechta"

JSON formatida javob ber:
{{
    "original": "{query}",
    "corrected": "to'g'rilangan versiya",
    "had_typos": true/false
}}

Faqat JSON qaytar.
'''


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 3: Smart Time Parser - Vaqtni Aqlli Tushunish
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SmartTimeParser:
    """Natural language vaqtni datetime'ga o'girish."""
    
    # Kun qismlari (start_hour, start_min, end_hour, end_min)
    TIME_OF_DAY = {
        'ertalab': (6, 0, 12, 0),
        'tushlik': (12, 0, 14, 0),
        'tushda': (12, 0, 14, 0),
        'kunduzi': (12, 0, 18, 0),
        'kechqurun': (18, 0, 23, 59),
        'kechasi': (22, 0, 6, 0),
        'tunda': (0, 0, 6, 0),
    }
    
    # Kun offsetlari
    DAY_OFFSETS = {
        'bugun': 0,
        'kecha': -1,
        "o'tgan kuni": -1,
        'uch kun oldin': -3,
        'bir hafta oldin': -7,
        'hafta oldin': -7,
    }
    
    WEEKDAYS = {
        'dushanba': 0, 'seshanba': 1, 'chorshanba': 2,
        'payshanba': 3, 'juma': 4, 'shanba': 5, 'yakshanba': 6
    }
    
    def parse(self, text: str) -> dict:
        """Natural language vaqtni parse qilish."""
        now = datetime.now()
        text_lower = text.lower()
        
        # "X soat/minut/kun oldin" pattern
        relative_match = re.search(r'(\d+)\s*(soat|minut|kun)\s*oldin', text_lower)
        if relative_match:
            amount = int(relative_match.group(1))
            unit = relative_match.group(2)
            if unit == 'soat':
                start = now - timedelta(hours=amount)
            elif unit == 'minut':
                start = now - timedelta(minutes=amount)
            elif unit == 'kun':
                start = now - timedelta(days=amount)
            else:
                start = now
            return {'start': start, 'end': now, 'text': text}
        
        # "O'tgan [weekday]" pattern
        weekday_match = re.search(r"o'tgan\s+(\w+)", text_lower)
        if weekday_match:
            day_name = weekday_match.group(1)
            if day_name in self.WEEKDAYS:
                target_weekday = self.WEEKDAYS[day_name]
                days_ago = (now.weekday() - target_weekday) % 7
                if days_ago == 0:
                    days_ago = 7  # Last week's same day
                target_date = now - timedelta(days=days_ago)
                return {
                    'start': target_date.replace(hour=0, minute=0, second=0),
                    'end': target_date.replace(hour=23, minute=59, second=59),
                    'text': text
                }
        
        # Day offset check (kecha, bugun, etc.)
        for pattern, offset in self.DAY_OFFSETS.items():
            if pattern in text_lower:
                target_date = now + timedelta(days=offset)
                
                # Check for time of day in same text
                for time_pattern, time_range in self.TIME_OF_DAY.items():
                    if time_pattern in text_lower:
                        return {
                            'start': target_date.replace(
                                hour=time_range[0], minute=time_range[1], second=0),
                            'end': target_date.replace(
                                hour=time_range[2], minute=time_range[3], second=59),
                            'text': text
                        }
                
                # Just the day, no specific time
                return {
                    'start': target_date.replace(hour=0, minute=0, second=0),
                    'end': target_date.replace(hour=23, minute=59, second=59),
                    'text': text
                }
        
        # Only time of day (assumes today)
        for pattern, time_range in self.TIME_OF_DAY.items():
            if pattern in text_lower:
                return {
                    'start': now.replace(hour=time_range[0], minute=time_range[1], second=0),
                    'end': now.replace(hour=time_range[2], minute=time_range[3], second=59),
                    'text': text
                }
        
        # Default: bugun (0:00 - now)
        return {
            'start': now.replace(hour=0, minute=0, second=0),
            'end': now,
            'text': text
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 4: Follow-up Suggestions - Ilgari Savollar
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class FollowUpSuggester:
    """Keyingi savollarni taklif qilish."""
    
    SUGGESTIONS = {
        'person': [
            ('📋 Kim?', 'followup:Bu odam kim?'),
            ('⏰ Qachon?', 'followup:Qachon keldi?'),
            ('🎬 Video', 'followup:Video ko\'rsat'),
        ],
        'car': [
            ('📋 Raqam', 'followup:Mashina raqami?'),
            ('⏰ Vaqt', 'followup:Qachon keldi?'),
            ('🎬 Video', 'followup:Video ko\'rsat'),
        ],
        'object': [
            ('📍 Qayerda?', 'followup:Aynan qayerda?'),
            ('👤 Kim?', 'followup:Kim olib ketdi?'),
            ('🎬 Video', 'followup:Video ko\'rsat'),
        ],
        'count': [
            ('📊 Ro\'yxat', 'followup:Hammasini ko\'rsat'),
            ('⏰ Vaqtlar', 'followup:Har birining vaqti'),
        ],
        'summary': [
            ('📹 Video', 'followup:Video ko\'rsat'),
            ('📊 Grafik', 'followup:Grafik ko\'rsat'),
        ],
        'general': [
            ('🔍 Batafsil', 'followup:Batafsil ma\'lumot'),
            ('🎬 Video', 'followup:Video ko\'rsat'),
        ]
    }
    
    def build_keyboard(self, result_type: str, context: dict = None) -> InlineKeyboardMarkup:
        """Telegram inline keyboard yaratish."""
        suggestions = self.SUGGESTIONS.get(result_type, self.SUGGESTIONS['general'])
        
        keyboard = []
        row = []
        for label, callback_data in suggestions:
            row.append(InlineKeyboardButton(text=label, callback_data=callback_data))
            if len(row) == 3:  # 3 ta per row
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        # Back to menu
        keyboard.append([InlineKeyboardButton("🏠 Menyu", callback_data="main_menu")])
        
        return InlineKeyboardMarkup(keyboard)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 5: Daily Summary - Tahlil Xulosasi
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DailyAnalyzer:
    """Kunlik tahlil xulosasi."""
    
    async def get_daily_summary(self, user_id: int, 
                                 date: datetime = None) -> dict:
        """Kunlik xulosa olish."""
        if date is None:
            date = datetime.now()
        
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Get user's cameras
        user = db.get_user(user_id)
        if not user:
            return self._empty_summary(date)
        
        org_id = user.get('organization_id')
        cameras = db.get_cameras_by_organization(org_id) if org_id else []
        
        summary = {
            'date': date.strftime('%Y-%m-%d'),
            'date_formatted': date.strftime('%d.%m.%Y'),
            'people': {'entered': 0, 'exited': 0},
            'vehicles': {'entered': 0, 'exited': 0},
            'peak_hours': [],
            'alerts': [],
            'total_events': 0,
            'cameras_count': len(cameras)
        }
        
        if not cameras:
            return summary
        
        # Analyze each camera
        hourly_activity = {h: 0 for h in range(24)}
        
        try:
            from database.v2_models import v2db
            
            for camera in cameras:
                events = v2db.get_detection_events(
                    camera_id=camera['id'],
                    start_time=start,
                    end_time=end
                )
                
                for event in events:
                    summary['total_events'] += 1
                    obj_type = str(event.get('object_type', '')).lower()
                    action = str(event.get('action', '')).lower()
                    
                    # Count people
                    if 'person' in obj_type or 'odam' in obj_type:
                        if 'kirdi' in action or 'enter' in action:
                            summary['people']['entered'] += 1
                        elif 'chiqdi' in action or 'exit' in action:
                            summary['people']['exited'] += 1
                    
                    # Count vehicles
                    if any(v in obj_type for v in ['car', 'mashina', 'vehicle', 'truck']):
                        if 'kirdi' in action or 'enter' in action:
                            summary['vehicles']['entered'] += 1
                        elif 'chiqdi' in action or 'exit' in action:
                            summary['vehicles']['exited'] += 1
                    
                    # Track hourly activity
                    event_time = event.get('timestamp')
                    if isinstance(event_time, datetime):
                        hourly_activity[event_time.hour] += 1
        except Exception as e:
            logger.warning(f"Error getting events: {e}")
        
        # Find peak hours
        if any(hourly_activity.values()):
            max_activity = max(hourly_activity.values())
            if max_activity > 0:
                peak_hours = [h for h, count in hourly_activity.items() 
                             if count == max_activity and count > 0]
                summary['peak_hours'] = [f"{h:02d}:00" for h in peak_hours[:3]]
        
        return summary
    
    def _empty_summary(self, date: datetime) -> dict:
        """Bo'sh xulosa."""
        return {
            'date': date.strftime('%Y-%m-%d'),
            'date_formatted': date.strftime('%d.%m.%Y'),
            'people': {'entered': 0, 'exited': 0},
            'vehicles': {'entered': 0, 'exited': 0},
            'peak_hours': [],
            'alerts': [],
            'total_events': 0,
            'cameras_count': 0
        }
    
    def format_summary(self, summary: dict) -> str:
        """Xulosa matnini formatlash."""
        text = f"📊 *{summary['date_formatted']} kunlik hisobot:*\n\n"
        
        text += f"👥 *Odamlar:* {summary['people']['entered']} kirdi, "
        text += f"{summary['people']['exited']} chiqdi\n"
        
        text += f"🚗 *Mashinalar:* {summary['vehicles']['entered']} keldi, "
        text += f"{summary['vehicles']['exited']} ketdi\n"
        
        if summary['peak_hours']:
            text += f"⏰ *Eng faol vaqt:* {', '.join(summary['peak_hours'])}\n"
        
        text += f"\n📈 *Jami hodisalar:* {summary['total_events']} ta"
        text += f"\n📹 *Kameralar:* {summary['cameras_count']} ta"
        
        return text


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE 6: User Profiler - Foydalanuvchi Profili
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class UserProfiler:
    """Foydalanuvchi profilini yaratish va saqlash."""
    
    def __init__(self):
        self.profiles: Dict[int, dict] = {}
    
    def update_profile(self, user_id: int, query: str, result: dict):
        """Har bir so'rovdan profil yangilash."""
        if user_id not in self.profiles:
            self.profiles[user_id] = {
                'favorite_cameras': {},
                'active_hours': {},
                'common_queries': {},
                'query_count': 0,
                'first_seen': datetime.now(),
                'last_seen': datetime.now()
            }
        
        profile = self.profiles[user_id]
        profile['query_count'] += 1
        profile['last_seen'] = datetime.now()
        
        # Track favorite camera
        camera_id = result.get('camera_id')
        if camera_id:
            profile['favorite_cameras'][camera_id] = \
                profile['favorite_cameras'].get(camera_id, 0) + 1
        
        # Track active hours
        hour = datetime.now().hour
        profile['active_hours'][hour] = \
            profile['active_hours'].get(hour, 0) + 1
        
        # Track query patterns
        query_type = result.get('result_type', 'general')
        profile['common_queries'][query_type] = \
            profile['common_queries'].get(query_type, 0) + 1
    
    def get_suggestions(self, user_id: int) -> dict:
        """Profilga asoslangan takliflar."""
        profile = self.profiles.get(user_id)
        if not profile:
            return {}
        
        suggestions = {}
        
        # Eng ko'p ishlatiladigan kamera
        if profile['favorite_cameras']:
            fav_camera = max(profile['favorite_cameras'], 
                           key=profile['favorite_cameras'].get)
            suggestions['default_camera'] = fav_camera
        
        # Eng faol vaqt
        if profile['active_hours']:
            peak_hour = max(profile['active_hours'],
                          key=profile['active_hours'].get)
            suggestions['peak_hour'] = peak_hour
        
        return suggestions
    
    def personalize_query(self, user_id: int, understanding: dict) -> dict:
        """So'rovni shaxsiylash."""
        suggestions = self.get_suggestions(user_id)
        
        # Agar kamera ko'rsatilmagan - default qo'yish
        if not understanding.get('camera_id') and suggestions.get('default_camera'):
            understanding['suggested_camera'] = suggestions['default_camera']
        
        return understanding


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QUERY CLASSIFICATION - Savol Klassifikatsiyasi
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLASSIFICATION_PROMPT = '''
Sen video kuzatuv tizimi AI yordamchisisan.

SAVOL: "{query}"

Bu savol video kuzatuv/kameraga tegishlimi?
Faqat JSON formatida javob ber.

KAMERA SAVOLLAR (can_answer=true):
- Odam/mashina/ob'ekt qidirish
- Kim kirdi/chiqdi/keldi/ketdi
- Nima bo'ldi (hodisalar)
- Qachon keldi/ketdi
- Nechta odam/mashina
- Biror narsa/odam topish
- Kuzatuv/monitoring

BOSHQA SAVOLLAR (can_answer=false):
- Ob-havo
- Matematika
- Umumiy savol
- Tavsiyalar
- Yangiliklar
- Siyosat
- Sport

{{
    "can_answer": true yoki false,
    "category": "camera" yoki "weather" yoki "math" yoki "general" yoki "other",
    "reason": "qisqa izoh"
}}
'''

UNDERSTANDING_PROMPT = '''
Sen video kuzatuv tizimi AI yordamchisisan.

SAVOL: "{query}"
{context_info}

Bu savolni tahlil qil va JSON formatida javob ber:
{{
    "intent": "find/count/check/describe/summary",
    "target": "person/car/object/event",
    "target_description": "batafsil ta'rif (qizil sumka, baland odam, etc.)",
    "action": "enter/exit/stay/move/any",
    "time_text": "vaqt haqidagi so'zlar (kecha, ertalab, 2 soat oldin)",
    "quantity": "first/last/all/count",
    "refers_to_previous": true/false,
    "is_daily_summary": true/false
}}

Faqat JSON qaytar.
'''


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN CLASS - Universal Video Analyst
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class UniversalVideoAnalyst:
    """Universal AI - har qanday savolga aqlli javob beradi."""
    
    def __init__(self):
        self.gemini = gemini_ai
        self.detector = detector
        self.video_recorder = video_recorder
        
        # 6 ta smart feature
        self.context = ConversationContext()
        self.time_parser = SmartTimeParser()
        self.followup = FollowUpSuggester()
        self.daily_analyzer = DailyAnalyzer()
        self.profiler = UserProfiler()
    
    async def answer_question(self, query: str, user_id: int, 
                               camera_id: int = None) -> dict:
        """HAR QANDAY savolga aqlli javob beradi."""
        
        try:
            # Step 1: Typo tuzatish
            corrected_query, had_typos = await self._correct_typos(query)
            
            # Step 2: Savol klassifikatsiyasi - kameraga tegishlimi?
            classification = await self._classify_query(corrected_query)
            
            if not classification.get('can_answer', False):
                return {
                    'success': False,
                    'answer': self._get_polite_rejection(classification),
                    'evidence': None,
                    'keyboard': None,
                    'had_typos': had_typos,
                    'corrected_query': corrected_query if had_typos else None
                }
            
            # Step 3: Kontekst olish
            prev_context = self.context.get_context(user_id)
            context_info = ""
            if prev_context:
                context_info = f"\nOLDINGI SAVOL: {prev_context.get('last_query', '')}"
            
            # Step 4: Savolni tushunish
            understanding = await self._understand_query(corrected_query, context_info)
            
            # Step 5: Kontekst bilan birlashtirish
            understanding = self.context.merge_with_context(user_id, understanding)
            
            # Step 6: User profili bilan shaxsiylash
            understanding = self.profiler.personalize_query(user_id, understanding)
            
            # Step 7: Vaqtni aqlli parse qilish
            time_text = understanding.get('time_text', '')
            if time_text:
                understanding['time_range'] = self.time_parser.parse(time_text)
            else:
                # Default: bugun
                understanding['time_range'] = self.time_parser.parse('bugun')
            
            # Step 8: "Bugun nima bo'ldi?" - daily summary
            if understanding.get('is_daily_summary') or understanding.get('intent') == 'summary':
                summary = await self.daily_analyzer.get_daily_summary(user_id)
                answer_text = self.daily_analyzer.format_summary(summary)
                
                # Typo eslatmasi
                if had_typos:
                    answer_text = f"_({corrected_query} - tushundim)_\n\n" + answer_text
                
                return {
                    'success': True,
                    'answer': answer_text,
                    'evidence': None,
                    'keyboard': self.followup.build_keyboard('summary'),
                    'result_type': 'summary',
                    'had_typos': had_typos
                }
            
            # Step 9: Video tahlil (TODO: implement full video analysis)
            # Hozircha database'dan qidiramiz
            result = await self._search_events(user_id, understanding)
            
            # Step 10: Javob yaratish
            answer_text = await self._generate_response(result, corrected_query, understanding)
            
            # Typo eslatmasi
            if had_typos:
                answer_text = f"_({corrected_query} - tushundim)_\n\n" + answer_text
            
            # Step 11: Kontekstni saqlash
            self.context.save_context(user_id, corrected_query, {
                'camera_id': result.get('camera_id'),
                'time_range': understanding.get('time_range'),
                'objects': result.get('objects', []),
                'result_type': result.get('result_type', 'general')
            })
            
            # Step 12: Profilni yangilash
            self.profiler.update_profile(user_id, corrected_query, result)
            
            # Step 13: Keyboard
            result_type = result.get('result_type', 'general')
            keyboard = self.followup.build_keyboard(result_type)
            
            return {
                'success': result.get('found', False),
                'answer': answer_text,
                'evidence': result.get('evidence'),
                'keyboard': keyboard,
                'result_type': result_type,
                'had_typos': had_typos
            }
            
        except Exception as e:
            logger.error(f"Error in answer_question: {e}")
            return {
                'success': False,
                'answer': "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
                'evidence': None,
                'keyboard': None
            }
    
    async def _correct_typos(self, query: str) -> Tuple[str, bool]:
        """Typo'larni tuzatish."""
        try:
            prompt = TYPO_CORRECTION_PROMPT.format(query=query)
            response = self.gemini.chat(0, prompt)
            
            if response and response.get('text'):
                # Extract JSON from response
                text = response['text']
                # Find JSON in response
                json_match = re.search(r'\{[^{}]+\}', text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    corrected = result.get('corrected', query)
                    had_typos = result.get('had_typos', False)
                    return corrected, had_typos
            
            return query, False
        except Exception as e:
            logger.warning(f"Typo correction failed: {e}")
            return query, False
    
    async def _classify_query(self, query: str) -> dict:
        """Savol kameraga tegishlimi?"""
        try:
            prompt = CLASSIFICATION_PROMPT.format(query=query)
            response = self.gemini.chat(0, prompt)
            
            if response and response.get('text'):
                text = response['text']
                json_match = re.search(r'\{[^{}]+\}', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            # Default: try to answer
            return {'can_answer': True, 'category': 'camera'}
        except Exception as e:
            logger.warning(f"Classification failed: {e}")
            return {'can_answer': True, 'category': 'camera'}
    
    async def _understand_query(self, query: str, context_info: str = "") -> dict:
        """Savolni tushunish."""
        try:
            prompt = UNDERSTANDING_PROMPT.format(query=query, context_info=context_info)
            response = self.gemini.chat(0, prompt)
            
            if response and response.get('text'):
                text = response['text']
                json_match = re.search(r'\{[^{}]+\}', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {'intent': 'find', 'target': 'any'}
        except Exception as e:
            logger.warning(f"Understanding failed: {e}")
            return {'intent': 'find', 'target': 'any'}
    
    async def _search_events(self, user_id: int, understanding: dict) -> dict:
        """Database'dan hodisalarni qidirish."""
        try:
            user = db.get_user(user_id)
            if not user:
                return {'found': False, 'reason': 'Foydalanuvchi topilmadi'}
            
            org_id = user.get('organization_id')
            cameras = db.get_cameras_by_organization(org_id) if org_id else []
            
            if not cameras:
                return {'found': False, 'reason': 'Sizda hali kamera yo\'q'}
            
            time_range = understanding.get('time_range', {})
            start_time = time_range.get('start', datetime.now().replace(hour=0, minute=0))
            end_time = time_range.get('end', datetime.now())
            
            all_events = []
            
            try:
                from database.v2_models import v2db
                
                for camera in cameras:
                    events = v2db.get_detection_events(
                        camera_id=camera['id'],
                        start_time=start_time,
                        end_time=end_time
                    )
                    for event in events:
                        event['camera_name'] = camera.get('name', f"Kamera {camera['id']}")
                        all_events.append(event)
            except Exception as e:
                logger.warning(f"Error fetching events: {e}")
            
            if not all_events:
                return {
                    'found': False, 
                    'reason': 'Bu vaqt oralig\'ida hodisa topilmadi',
                    'result_type': 'general'
                }
            
            # Filter by target type
            target = understanding.get('target', 'any')
            if target != 'any':
                filtered = []
                for event in all_events:
                    obj_type = str(event.get('object_type', '')).lower()
                    if target == 'person' and ('person' in obj_type or 'odam' in obj_type):
                        filtered.append(event)
                    elif target == 'car' and any(v in obj_type for v in ['car', 'mashina', 'vehicle']):
                        filtered.append(event)
                    else:
                        filtered.append(event)
                all_events = filtered if filtered else all_events
            
            # Apply quantity filter
            quantity = understanding.get('quantity', 'all')
            result_type = 'general'
            
            if quantity == 'last' and all_events:
                # Sort by timestamp descending
                sorted_events = sorted(all_events, 
                                       key=lambda x: x.get('timestamp', datetime.min), 
                                       reverse=True)
                return {
                    'found': True,
                    'events': [sorted_events[0]],
                    'single_event': sorted_events[0],
                    'result_type': 'person' if target == 'person' else 'general'
                }
            
            elif quantity == 'first' and all_events:
                sorted_events = sorted(all_events, 
                                       key=lambda x: x.get('timestamp', datetime.max))
                return {
                    'found': True,
                    'events': [sorted_events[0]],
                    'single_event': sorted_events[0],
                    'result_type': 'person' if target == 'person' else 'general'
                }
            
            elif quantity == 'count':
                return {
                    'found': True,
                    'count': len(all_events),
                    'events': all_events,
                    'result_type': 'count'
                }
            
            return {
                'found': True,
                'events': all_events,
                'count': len(all_events),
                'result_type': 'general'
            }
            
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return {'found': False, 'reason': 'Qidirishda xatolik'}
    
    async def _generate_response(self, result: dict, query: str, understanding: dict) -> str:
        """Javob yaratish."""
        if not result.get('found'):
            reason = result.get('reason', 'Hech narsa topilmadi')
            return f"❌ {reason}"
        
        # Count response
        if result.get('result_type') == 'count':
            count = result.get('count', 0)
            target = understanding.get('target', 'hodisa')
            target_name = {
                'person': 'odam',
                'car': 'mashina',
                'object': 'ob\'ekt'
            }.get(target, 'hodisa')
            
            time_range = understanding.get('time_range', {})
            time_text = time_range.get('text', 'bugun')
            
            return f"📊 *{time_text.capitalize()}* {count} ta {target_name} aniqlandi."
        
        # Single event response
        if result.get('single_event'):
            event = result['single_event']
            timestamp = event.get('timestamp')
            camera_name = event.get('camera_name', 'Kamera')
            obj_type = event.get('object_type', 'Ob\'ekt')
            
            time_str = timestamp.strftime('%H:%M') if isinstance(timestamp, datetime) else str(timestamp)
            date_str = timestamp.strftime('%d.%m.%Y') if isinstance(timestamp, datetime) else ''
            
            quantity = understanding.get('quantity', '')
            if quantity == 'last':
                prefix = "📹 *Oxirgi*"
            elif quantity == 'first':
                prefix = "📹 *Birinchi*"
            else:
                prefix = "📹"
            
            return (
                f"{prefix} {obj_type} - *{camera_name}*\n"
                f"⏰ Vaqt: *{time_str}* ({date_str})"
            )
        
        # Multiple events
        events = result.get('events', [])
        if events:
            count = len(events)
            return f"📊 *{count} ta hodisa* topildi.\n\nBatafsil ko'rish uchun tugmani bosing."
        
        return "✅ Qidiruv yakunlandi."
    
    def _get_polite_rejection(self, classification: dict) -> str:
        """Iltifotli rad javob."""
        category = classification.get('category', 'other')
        
        responses = {
            'weather': (
                "😊 Men *Cam Max* - video kuzatuv yordamchisiman.\n\n"
                "Ob-havo haqida ma'lumot bera olmayman.\n\n"
                "📹 *Kameralar haqida so'rang:*\n"
                "• Kecha kim keldi?\n"
                "• Bugun nechta odam kirdi?\n"
                "• Mashina bormi?"
            ),
            'math': (
                "😊 Matematika savollariga javob bera olmayman.\n\n"
                "📹 *Kameralar va video qidiruv - mening soham!*\n\n"
                "Masalan: _Kecha oxirgi kim ketdi?_"
            ),
            'general': (
                "😊 Men *Cam Max* - video kuzatuv AI yordamchisiman.\n\n"
                "Bu savolga javob bera olmayman.\n\n"
                "📹 *Masalan so'rang:*\n"
                "• Kecha kim keldi?\n"
                "• Bugun nechta odam kirdi?\n"
                "• Mashina qachon ketdi?"
            ),
            'other': (
                "😊 Bu savolga javob bera olmayman.\n\n"
                "📹 Men video kuzatuv yordamchisiman.\n"
                "Kameralaringiz haqida so'rang!"
            )
        }
        
        return responses.get(category, responses['other'])
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ADVANCED FEATURE 7: Face Recognition - Yuzni Tanish
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def identify_face(self, user_id: int, frame) -> dict:
        """Frame'dagi yuzlarni aniqlash."""
        if not FACE_RECOGNITION_ENABLED:
            return {'success': False, 'error': 'Yuz tanish moduli yuklanmagan'}
        
        try:
            results = face_recognizer.identify_person(user_id, frame)
            
            if results:
                known = [r for r in results if r['known']]
                unknown = [r for r in results if not r['known']]
                
                text = f"👤 *{len(results)} ta yuz topildi:*\n\n"
                
                for r in known:
                    text += f"✅ *{r['name']}* ({r['confidence']*100:.0f}%)\n"
                
                if unknown:
                    text += f"❓ Notanish: {len(unknown)} kishi\n"
                
                return {
                    'success': True,
                    'answer': text,
                    'faces': results,
                    'keyboard': self._get_face_keyboard()
                }
            else:
                return {
                    'success': True,
                    'answer': "😕 Yuz topilmadi",
                    'faces': []
                }
        except Exception as e:
            logger.error(f"Face identification error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def add_face(self, user_id: int, name: str, frame, 
                       category: str = "known") -> dict:
        """Yangi yuzni qo'shish."""
        if not FACE_RECOGNITION_ENABLED:
            return {'success': False, 'error': 'Yuz tanish moduli yuklanmagan'}
        
        try:
            success = face_recognizer.add_known_face(user_id, name, frame, category)
            
            if success:
                return {
                    'success': True,
                    'answer': f"✅ *{name}* muvaffaqiyatli qo'shildi!\n\nEndi bu odamni taniy olaman."
                }
            else:
                return {
                    'success': False,
                    'answer': "❌ Yuz topilmadi yoki saqlab bo'lmadi."
                }
        except Exception as e:
            logger.error(f"Add face error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_face_keyboard(self) -> InlineKeyboardMarkup:
        """Yuz uchun keyboard."""
        keyboard = [
            [InlineKeyboardButton("➕ Yuz qo'shish", callback_data="face_add")],
            [InlineKeyboardButton("📋 Ro'yxat", callback_data="face_list")],
            [InlineKeyboardButton("🏠 Menyu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ADVANCED FEATURE 8: License Plate OCR - Avtomobil Raqami
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def read_plates(self, frame) -> dict:
        """Frame'dan raqamlarni o'qish."""
        if not PLATE_READER_ENABLED:
            return {'success': False, 'error': 'Raqam o\'qish moduli yuklanmagan'}
        
        try:
            results = plate_reader.process_frame(frame)
            
            if results:
                text = f"🚗 *{len(results)} ta raqam topildi:*\n\n"
                
                for r in results:
                    status = "✅" if r['is_valid'] else "⚠️"
                    text += f"{status} *{r['text']}* ({r['confidence']*100:.0f}%)\n"
                
                return {
                    'success': True,
                    'answer': text,
                    'plates': results
                }
            else:
                return {
                    'success': True,
                    'answer': "😕 Raqam topilmadi",
                    'plates': []
                }
        except Exception as e:
            logger.error(f"Plate reading error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def search_by_plate(self, plate_number: str) -> dict:
        """Raqam bo'yicha qidirish."""
        if not PLATE_READER_ENABLED:
            return {'success': False, 'error': 'Raqam o\'qish moduli yuklanmagan'}
        
        try:
            results = plate_reader.search_by_plate(plate_number)
            
            if results:
                text = f"🚗 *{plate_number}* - *{len(results)} ta natija:*\n\n"
                
                for r in results[:5]:  # Max 5 ta
                    text += f"📅 {r['timestamp'][:16]} - Kamera {r['camera_id']}\n"
                
                return {
                    'success': True,
                    'answer': text,
                    'results': results
                }
            else:
                return {
                    'success': True,
                    'answer': f"❌ *{plate_number}* topilmadi"
                }
        except Exception as e:
            logger.error(f"Plate search error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ADVANCED FEATURE 9: Anomaly Detection - Shubhali Harakat
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def check_anomalies(self, camera_id: int = None) -> dict:
        """Shubhali harakatlarni tekshirish."""
        if not ANOMALY_DETECTOR_ENABLED:
            return {'success': False, 'error': 'Anomal harakat moduli yuklanmagan'}
        
        try:
            alerts = anomaly_detector.get_recent_alerts(24, camera_id)
            summary = anomaly_detector.get_alert_summary(camera_id)
            
            if alerts:
                text = f"🚨 *Oxirgi 24 soat:* {summary['total']} ta alert\n\n"
                
                if summary['critical'] > 0:
                    text += f"🔴 Kritik: {summary['critical']} ta\n"
                if summary['warning'] > 0:
                    text += f"🟡 Ogohlantirish: {summary['warning']} ta\n"
                
                text += "\n*Oxirgi hodisalar:*\n"
                for alert in alerts[:5]:
                    icon = "🔴" if alert.level == AlertLevel.CRITICAL else "🟡"
                    text += f"{icon} {alert.description}\n"
                
                return {
                    'success': True,
                    'answer': text,
                    'alerts': alerts,
                    'summary': summary
                }
            else:
                return {
                    'success': True,
                    'answer': "✅ Hech qanday shubhali harakat yo'q.",
                    'alerts': []
                }
        except Exception as e:
            logger.error(f"Anomaly check error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def analyze_for_anomalies(self, detections: list, 
                                     camera_id: int = None) -> list:
        """Deteksiyalarni anomal harakat uchun tahlil qilish."""
        if not ANOMALY_DETECTOR_ENABLED:
            return []
        
        try:
            anomalies = anomaly_detector.analyze_frame(detections, camera_id)
            return anomalies
        except Exception as e:
            logger.error(f"Anomaly analysis error: {e}")
            return []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ADVANCED FEATURE 10: Clothing Recognition - Kiyim Tahlili
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def analyze_clothing(self, person_crop) -> dict:
        """Kiyimni tahlil qilish."""
        if not CLOTHING_ANALYZER_ENABLED:
            return {'success': False, 'error': 'Kiyim tahlil moduli yuklanmagan'}
        
        try:
            info = clothing_analyzer.analyze_clothing(person_crop)
            
            text = (
                f"👕 *Kiyim tahlili:*\n\n"
                f"🎨 Rang: *{', '.join(info.colors)}*\n"
                f"👔 Tur: *{', '.join(info.types) if info.types else 'aniqlanmadi'}*\n"
                f"📝 Tavsif: _{info.description}_"
            )
            
            return {
                'success': True,
                'answer': text,
                'info': info
            }
        except Exception as e:
            logger.error(f"Clothing analysis error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def search_by_clothing(self, description: str, 
                                  frames: list) -> dict:
        """Kiyim tavsifi bo'yicha qidirish."""
        if not CLOTHING_ANALYZER_ENABLED:
            return {'success': False, 'error': 'Kiyim tahlil moduli yuklanmagan'}
        
        try:
            # First detect persons
            person_crops = []
            for frame in frames:
                detections = self.detector.detect(frame)
                for det in detections:
                    if det.class_name in ['person', 'odam']:
                        x, y, w, h = det.bbox
                        crop = frame[y:y+h, x:x+w]
                        if crop.size > 0:
                            person_crops.append(crop)
            
            if not person_crops:
                return {
                    'success': True,
                    'answer': "❌ Hech qanday odam topilmadi"
                }
            
            # Search by description
            results = clothing_analyzer.search_by_description(description, person_crops)
            
            if results:
                text = f"👕 *'{description}'* bo'yicha {len(results)} ta natija:\n\n"
                
                for i, r in enumerate(results[:3], 1):
                    text += f"{i}. Moslik: {r['score']*100:.0f}%\n"
                
                return {
                    'success': True,
                    'answer': text,
                    'results': results
                }
            else:
                return {
                    'success': True,
                    'answer': f"❌ '{description}' ga mos odam topilmadi"
                }
        except Exception as e:
            logger.error(f"Clothing search error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ADVANCED FEATURE 11: Multi-Object Tracking
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def update_tracking(self, detections: list, 
                               camera_id: int = None) -> dict:
        """Kuzatuvni yangilash."""
        if not OBJECT_TRACKER_ENABLED:
            return {'success': False, 'error': 'Tracking moduli yuklanmagan'}
        
        try:
            tracks = object_tracker.update(detections, camera_id)
            active = object_tracker.get_active_tracks()
            summary = object_tracker.get_summary()
            
            text = f"🔄 *Tracking:* {len(active)} ta aktiv ob'ekt\n"
            
            for track in active[:5]:
                text += f"  • ID:{track.track_id} {track.class_name} ({track.duration:.0f}s)\n"
            
            return {
                'success': True,
                'answer': text,
                'tracks': tracks,
                'summary': summary
            }
        except Exception as e:
            logger.error(f"Tracking error: {e}")
            return {'success': False, 'error': str(e)}
    
    def draw_tracks_on_frame(self, frame, show_path: bool = True) -> any:
        """Trackni frame ustiga chizish."""
        if not OBJECT_TRACKER_ENABLED:
            return frame
        return object_tracker.draw_tracks(frame, show_path)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ADVANCED FEATURE 12: Zone Monitoring
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def create_zone(self, name: str, zone_type: str,
                          points: list, camera_id: int, 
                          user_id: int) -> dict:
        """Yangi hudud yaratish."""
        if not ZONE_MONITOR_ENABLED:
            return {'success': False, 'error': 'Zone moduli yuklanmagan'}
        
        try:
            zt = ZoneType(zone_type)
            zone = zone_monitor.create_zone(name, zt, points, camera_id, user_id)
            
            return {
                'success': True,
                'answer': f"✅ *{name}* hududi yaratildi (ID: {zone.zone_id})",
                'zone': zone.to_dict()
            }
        except Exception as e:
            logger.error(f"Create zone error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_zone_summary(self, user_id: int) -> dict:
        """Hududlar xulosasi."""
        if not ZONE_MONITOR_ENABLED:
            return {'success': False, 'error': 'Zone moduli yuklanmagan'}
        
        try:
            summary = zone_monitor.get_summary(user_id)
            zones = zone_monitor.get_zones(user_id)
            
            text = f"🗺️ *Hududlar:* {summary['total_zones']} ta\n\n"
            
            for zone in zones:
                icon = "🔴" if zone.zone_type.value == 'restricted' else "🟢"
                text += f"{icon} *{zone.name}*: {zone.current_count} odam\n"
            
            if summary['intrusions'] > 0:
                text += f"\n⚠️ Buzilishlar: {summary['intrusions']} ta"
            
            return {
                'success': True,
                'answer': text,
                'summary': summary
            }
        except Exception as e:
            logger.error(f"Zone summary error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def check_zone_events(self, user_id: int) -> dict:
        """Hudud hodisalarini tekshirish."""
        if not ZONE_MONITOR_ENABLED:
            return {'success': False, 'error': 'Zone moduli yuklanmagan'}
        
        try:
            events = zone_monitor.get_recent_events(24, user_id=user_id)
            
            if events:
                text = f"🚨 *Oxirgi 24 soat:* {len(events)} ta hodisa\n\n"
                
                for e in events[:5]:
                    icon = "🔴" if e.alert_type.value == 'intrusion' else "🟡"
                    text += f"{icon} {e.description}\n"
                
                return {
                    'success': True,
                    'answer': text,
                    'events': [{'type': e.alert_type.value, 'desc': e.description} for e in events]
                }
            else:
                return {
                    'success': True,
                    'answer': "✅ Hech qanday hodisa yo'q."
                }
        except Exception as e:
            logger.error(f"Zone events error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ADVANCED FEATURE 13: Auto Analysis
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def enable_auto_reports(self, user_id: int, hour: int = 8) -> dict:
        """Avtomatik hisobotni yoqish."""
        if not AUTO_ANALYZER_ENABLED:
            return {'success': False, 'error': 'Auto analyzer moduli yuklanmagan'}
        
        try:
            auto_analyzer.schedule_daily_report(user_id, hour)
            
            return {
                'success': True,
                'answer': f"✅ Kunlik hisobot har kuni soat *{hour}:00* da yuboriladi."
            }
        except Exception as e:
            logger.error(f"Enable auto reports error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_quick_summary(self, user_id: int) -> dict:
        """Tezkor xulosa olish."""
        if not AUTO_ANALYZER_ENABLED:
            return {'success': False, 'error': 'Auto analyzer moduli yuklanmagan'}
        
        try:
            text = await auto_analyzer.generate_quick_summary(user_id)
            return {
                'success': True,
                'answer': text
            }
        except Exception as e:
            logger.error(f"Quick summary error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def generate_report(self, user_id: int) -> dict:
        """Hisobot yaratish."""
        if not AUTO_ANALYZER_ENABLED:
            return {'success': False, 'error': 'Auto analyzer moduli yuklanmagan'}
        
        try:
            report = await auto_analyzer.generate_daily_report(user_id)
            text = auto_analyzer.format_daily_report(report)
            
            return {
                'success': True,
                'answer': text,
                'report': {
                    'people': report.people_count,
                    'vehicles': report.vehicle_count,
                    'events': report.total_events,
                    'anomalies': report.anomalies_count
                }
            }
        except Exception as e:
            logger.error(f"Generate report error: {e}")
            return {'success': False, 'error': str(e)}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Status Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_features_status(self) -> dict:
        """Barcha AI featurelarning holati."""
        return {
            'basic_features': {
                'context_memory': True,
                'typo_correction': True,
                'smart_time': True,
                'followup_suggestions': True,
                'daily_summary': True,
                'user_profiler': True
            },
            'advanced_features': {
                'face_recognition': FACE_RECOGNITION_ENABLED,
                'plate_reader': PLATE_READER_ENABLED,
                'anomaly_detector': ANOMALY_DETECTOR_ENABLED,
                'clothing_analyzer': CLOTHING_ANALYZER_ENABLED,
                'object_tracker': OBJECT_TRACKER_ENABLED,
                'zone_monitor': ZONE_MONITOR_ENABLED,
                'auto_analyzer': AUTO_ANALYZER_ENABLED
            },
            'total_features': 13
        }


# Global instance
universal_analyst = UniversalVideoAnalyst()


