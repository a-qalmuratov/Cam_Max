"""
Real AI Integration using Google Gemini API.
Provides intelligent conversational understanding and camera analysis.
"""
import os
import base64
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests

from utils.logger import logger
from utils.config import GEMINI_API_KEY


class GeminiAI:
    """Google Gemini AI for intelligent conversations."""
    
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.conversation_history: Dict[int, List[Dict]] = {}
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the AI."""
        return """Sen Cam Max - AI video kuzatuv tizimi yordamchisisan. 
        
VAZIFANG:
1. Foydalanuvchi so'rovlarini tushunish
2. Kerakli ma'lumotlarni so'rash (kamera, vaqt, ob'ekt)
3. Video arxivdan qidirish natijalarini taqdim etish
4. Real-time kameralarda ob'ektlarni topish

QOIDALAR:
- Har doim O'ZBEK tilida javob ber
- Qisqa va aniq bo'l
- Emoji ishlatishni unutma
- Agar ma'lumot yetarli bo'lmasa, SO'RA
- Agar ob'ekt/odam topilsa, aniq vaqt va kamerani ko'rsat

SAVOLLARNI TAHLIL QILISH:
Foydalanuvchi so'rovidan quyidagilarni ajrat:
- object: qidirilayotgan narsa (sumka, telefon, odam, mashina, etc.)
- color: rang (qizil, oq, qora, etc.)  
- location: joy (zal, kassa, kirish, etc.)
- time: vaqt (bugun, kecha, ertalab, etc.)
- action: harakat (oldi, qo'ydi, kirdi, chiqdi)
- camera: kamera (1-kamera, 2-kamera, etc.)

Agar muhim ma'lumot yo'q bo'lsa, so'ra. Masalan:
- Kamera aniq bo'lmasa: "Qaysi kamerada qidirish kerak?"
- Vaqt aniq bo'lmasa: "Qachon? Bugunmi yoki kecha?"
- Ob'ekt aniq bo'lmasa: "Nimani qidiryapsiz?"

JAVOB FORMATI:
Agar qidirish kerak bo'lsa, JSON formatida qaytarishni ham qo'sh:
```json
{"action": "search", "params": {...}}
```

Agar so'rash kerak bo'lsa:
```json
{"action": "ask", "question": "..."}
```

Agar hozirgi kameralarda qidirish kerak:
```json
{"action": "live_search", "params": {...}}
```
"""
    
    def chat(self, user_id: int, message: str, image_data: bytes = None) -> Dict[str, Any]:
        """
        Chat with AI.
        
        Args:
            user_id: Telegram user ID
            message: User message
            image_data: Optional image bytes for analysis
            
        Returns:
            AI response with action and text
        """
        if not self.api_key:
            return {
                'success': False,
                'text': "❌ AI API kaliti sozlanmagan. .env fayliga GEMINI_API_KEY qo'shing.",
                'action': None
            }
        
        # Get conversation history
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        history = self.conversation_history[user_id]
        
        # Build request
        contents = []
        
        # Add system prompt as first message
        contents.append({
            "role": "user",
            "parts": [{"text": f"[SYSTEM]: {self._get_system_prompt()}"}]
        })
        contents.append({
            "role": "model", 
            "parts": [{"text": "Tushundim. Men Cam Max AI yordamchisiman. O'zbek tilida javob beraman va foydalanuvchiga video qidiruvda yordam beraman."}]
        })
        
        # Add conversation history
        for msg in history[-10:]:  # Last 10 messages
            contents.append(msg)
        
        # Add current message
        current_parts = [{"text": message}]
        
        # Add image if provided
        if image_data:
            base64_image = base64.b64encode(image_data).decode('utf-8')
            current_parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": base64_image
                }
            })
        
        contents.append({
            "role": "user",
            "parts": current_parts
        })
        
        try:
            # Make API request
            response = requests.post(
                f"{self.API_URL}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": contents,
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 1024
                    }
                },
                timeout=30
            )
            
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                
                # Import messages untuk error details
                from utils.messages import msg
                
                # Detailed error based on status code
                if response.status_code == 404:
                    error_text = f"{msg.AI_ERROR_404_TITLE}\n\n{msg.AI_ERROR_404_WHAT}\n\n{msg.AI_ERROR_404_WHY}\n\n{msg.AI_ERROR_404_FIX}"
                elif response.status_code == 429:
                    error_text = f"{msg.AI_ERROR_429_TITLE}\n\n{msg.AI_ERROR_429_WHAT}\n\n{msg.AI_ERROR_429_WHY}\n\n{msg.AI_ERROR_429_FIX}"
                elif response.status_code == 500 or response.status_code >= 500:
                    error_text = f"{msg.AI_ERROR_500_TITLE}\n\n{msg.AI_ERROR_500_WHAT}\n\n{msg.AI_ERROR_500_WHY}\n\n{msg.AI_ERROR_500_FIX}"
                elif response.status_code == 401 or response.status_code == 403:
                    error_text = f"{msg.AI_ERROR_AUTH_TITLE}\n\n{msg.AI_ERROR_AUTH_WHAT}\n\n{msg.AI_ERROR_AUTH_WHY}\n\n{msg.AI_ERROR_AUTH_FIX}"
                else:
                    error_text = f"{msg.AI_ERROR_UNKNOWN_TITLE}\n\n{msg.AI_ERROR_UNKNOWN_WHAT}\n\n{msg.AI_ERROR_UNKNOWN_WHY}\n\n{msg.AI_ERROR_UNKNOWN_FIX}\n\n📝 Texnik maǵlıw: HTTP {response.status_code}"
                
                return {
                    'success': False,
                    'text': error_text,
                    'action': None,
                    'show_main_menu': True  # Flag to show main menu button
                }

            
            result = response.json()
            
            # Extract text
            ai_text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Save to history
            history.append({
                "role": "user",
                "parts": [{"text": message}]
            })
            history.append({
                "role": "model",
                "parts": [{"text": ai_text}]
            })
            
            # Parse action from response
            action_data = self._parse_action(ai_text)
            
            # Clean text (remove JSON blocks)
            clean_text = re.sub(r'```json\n.*?\n```', '', ai_text, flags=re.DOTALL).strip()
            
            return {
                'success': True,
                'text': clean_text,
                'action': action_data.get('action'),
                'params': action_data.get('params', {}),
                'question': action_data.get('question')
            }
            
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return {
                'success': False,
                'text': f"❌ AI xatosi: {str(e)}",
                'action': None
            }
    
    def _parse_action(self, text: str) -> Dict[str, Any]:
        """Parse action from AI response."""
        try:
            # Find JSON block
            json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error in AI response: {e}")
        except Exception as e:
            logger.warning(f"Action parse error: {e}")
        
        return {}
    
    def analyze_image(self, image_data: bytes, query: str) -> Dict[str, Any]:
        """
        Analyze image with AI.
        
        Args:
            image_data: JPEG image bytes
            query: What to look for
            
        Returns:
            Analysis result
        """
        if not self.api_key:
            return {
                'success': False,
                'text': "❌ AI API kaliti sozlanmagan.",
                'found': False
            }
        
        prompt = f"""Bu kamera rasmini tahlil qil.

TOPISH KERAK: {query}

Agar ko'rsatilgan narsa/odam rasmda bo'lsa:
1. TOPILDI deb ayt
2. Qayerda joylashganini ta'rifla (o'ng, chap, markaz, etc.)
3. Rangini, o'lchamini ta'rifla

Agar topilmasa, TOPILMADI deb ayt.

O'zbek tilida javob ber."""

        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            response = requests.post(
                f"{self.API_URL}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": base64_image
                                }
                            }
                        ]
                    }],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 512
                    }
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'text': f"❌ Tahlil xatosi: {response.status_code}",
                    'found': False
                }
            
            result = response.json()
            ai_text = result['candidates'][0]['content']['parts'][0]['text']
            
            found = 'topildi' in ai_text.lower() and 'topilmadi' not in ai_text.lower()
            
            return {
                'success': True,
                'text': ai_text,
                'found': found
            }
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {
                'success': False,
                'text': f"❌ Xatolik: {str(e)}",
                'found': False
            }
    
    def clear_history(self, user_id: int):
        """Clear conversation history for user."""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]


# Global instance
gemini_ai = GeminiAI()
