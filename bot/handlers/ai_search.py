"""
Real AI Search handler with Gemini integration.
Premium conversational AI that understands any question.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.models import db
from camera.stream_manager import stream_manager
from utils.logger import logger
from ai.gemini_ai import gemini_ai
import cv2
import io

# Conversation states
AI_CONVERSATION = 1


class AISearchHandler:
    """Handle AI search with real Gemini AI conversations."""
    
    @staticmethod
    async def show_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show AI search menu."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # Clear previous conversation
        gemini_ai.clear_history(user_id)
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃    🧠 AI YORDAMCHI        ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "🤖 Salom! Men sizning AI yordamchingizman.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💬 Menga istalgan savolingizni bering:\n\n"
            "📝 Misollar:\n"
            "• \"Stol ustidagi qizil sumka qayerda?\"\n"
            "• \"Kecha kim kirdi?\"\n"
            "• \"1-kamerada hozir nima bor?\"\n"
            "• \"Oq ko'ylakli odam qayerga ketdi?\"\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 Agar ma'lumot yetarli bo'lmasa,\n"
            "   men sizdan so'rab olaman!"
        )
        
        keyboard = [[InlineKeyboardButton("« Asosiy Menyu", callback_data="menu_main")]]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        
        return AI_CONVERSATION
    
    @staticmethod
    async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any user message with real AI."""
        message_text = update.message.text.strip()
        user_id = update.effective_user.id
        
        # Show thinking message
        thinking_msg = await update.message.reply_text(
            "🤔 O'ylayapman..."
        )
        
        try:
            # Get AI response
            ai_response = gemini_ai.chat(user_id, message_text)
            
            if not ai_response['success']:
                await thinking_msg.edit_text(ai_response['text'])
                return AI_CONVERSATION
            
            # Check action type
            action = ai_response.get('action')
            
            if action == 'search':
                # Execute search in archive
                result = await AISearchHandler._execute_archive_search(
                    update, context, ai_response.get('params', {}), thinking_msg
                )
                return AI_CONVERSATION
                
            elif action == 'live_search':
                # Search in current camera views
                result = await AISearchHandler._execute_live_search(
                    update, context, ai_response.get('params', {}), thinking_msg
                )
                return AI_CONVERSATION
                
            elif action == 'ask':
                # AI is asking for more info
                question = ai_response.get('question', ai_response['text'])
                
                text = (
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃    🤖 AI SAVOLI           ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    f"{ai_response['text']}\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "💬 Javobingizni yozing:"
                )
                
                await thinking_msg.edit_text(text)
                return AI_CONVERSATION
            
            else:
                # Regular AI response
                text = (
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃    🤖 AI JAVOB            ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    f"{ai_response['text']}\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "💬 Boshqa savol bering yoki /menu"
                )
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Yangi Savol", callback_data="menu_ai")],
                    [InlineKeyboardButton("« Asosiy Menyu", callback_data="menu_main")]
                ]
                
                await thinking_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                return AI_CONVERSATION
                
        except Exception as e:
            logger.error(f"AI handler error: {e}")
            await thinking_msg.edit_text(f"❌ Xatolik: {str(e)}")
            return AI_CONVERSATION
    
    @staticmethod
    async def _execute_live_search(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        params: dict,
        msg
    ):
        """Search for object in current camera views."""
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        
        if not user:
            await msg.edit_text("❌ Foydalanuvchi topilmadi!")
            return
        
        cameras = db.get_cameras_by_organization(user.get('organization_id')) or []
        
        if not cameras:
            await msg.edit_text("❌ Kameralar yo'q! Avval kamera qo'shing.")
            return
        
        # What to search for
        search_query = params.get('object', '') or params.get('query', 'ob\'ekt')
        if params.get('color'):
            search_query = f"{params['color']} {search_query}"
        
        await msg.edit_text(
            f"🔍 Barcha kameralarda qidirilmoqda:\n"
            f"🎯 \"{search_query}\"\n\n"
            f"⏳ Iltimos kuting..."
        )
        
        results = []
        
        for camera in cameras:
            camera_id = camera['id']
            camera_name = camera['name']
            
            try:
                # Get camera client with proper connection
                cam_client = stream_manager.get_or_connect_camera(camera_id)
                
                if cam_client is None or not cam_client.is_connected:
                    logger.warning(f"Camera {camera_name} not available for AI search")
                    continue
                
                # Capture frame
                frame = cam_client.get_frame()
                
                if frame is None:
                    # Try reconnect
                    cam_client.reconnect()
                    frame = cam_client.get_frame()
                
                if frame is None:
                    continue
                
                # Encode to JPEG
                success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
                if not success:
                    continue
                
                image_data = buffer.tobytes()
                
                # Analyze with AI
                analysis = gemini_ai.analyze_image(image_data, search_query)
                
                if analysis['found']:
                    results.append({
                        'camera_id': camera_id,
                        'camera_name': camera_name,
                        'description': analysis['text'],
                        'image_data': image_data
                    })
                    
            except Exception as e:
                logger.error(f"Live search error for camera {camera_id}: {e}")
                continue
        
        # Show results
        if results:
            text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃    ✅ TOPILDI!            ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"🎯 \"{search_query}\"\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            )
            
            for r in results:
                text += f"📹 {r['camera_name']}:\n"
                text += f"{r['description'][:200]}\n\n"
                
                # Send the image
                photo_bytes = io.BytesIO(r['image_data'])
                photo_bytes.name = f"{r['camera_name']}_snapshot.jpg"
                
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo_bytes,
                    caption=f"📹 {r['camera_name']}\n🎯 {search_query}"
                )
            
            keyboard = [
                [InlineKeyboardButton("🔄 Qayta Qidirish", callback_data="menu_ai")],
                [InlineKeyboardButton("« Asosiy Menyu", callback_data="menu_main")]
            ]
            
            await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            
        else:
            text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃    📭 TOPILMADI          ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"🎯 \"{search_query}\"\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"❌ {len(cameras)} ta kamerada tekshirildi,\n"
                "   hech qayerida topilmadi.\n\n"
                "💡 Boshqa so'rov bilan urinib ko'ring\n"
                "   yoki video arxivda qidiring."
            )
            
            keyboard = [
                [InlineKeyboardButton("📅 Arxivda Qidirish", callback_data="view_archive")],
                [InlineKeyboardButton("🔄 Qayta Qidirish", callback_data="menu_ai")],
                [InlineKeyboardButton("« Asosiy Menyu", callback_data="menu_main")]
            ]
            
            await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def _execute_archive_search(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: dict,
        msg
    ):
        """Search in video archive."""
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        
        if not user:
            await msg.edit_text("❌ Foydalanuvchi topilmadi!")
            return
        
        # Build search description
        search_query = params.get('object', 'ob\'ekt')
        if params.get('color'):
            search_query = f"{params['color']} {search_query}"
        
        time_range = params.get('time', 'bugun')
        camera = params.get('camera', 'barcha kameralar')
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃    🔍 ARXIV QIDIRUVI      ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"🎯 Qidiruv: \"{search_query}\"\n"
            f"📅 Vaqt: {time_range}\n"
            f"📹 Kamera: {camera}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ Video arxiv tizimi hali to'liq ishga\n"
            "   tushirilmagan. Hozircha real-time\n"
            "   kameralarda qidirishingiz mumkin.\n\n"
            "💡 \"Hozir qayerda?\" deb so'rang\n"
            "   real-time qidirish uchun."
        )
        
        keyboard = [
            [InlineKeyboardButton("🔴 Real-time Qidirish", callback_data="menu_ai")],
            [InlineKeyboardButton("« Asosiy Menyu", callback_data="menu_main")]
        ]
        
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def handle_clarification(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle clarification - redirects to main handler."""
        return await AISearchHandler.handle_query(update, context)
    
    @staticmethod
    async def view_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View video evidence."""
        query = update.callback_query
        await query.answer("🔜 Video arxiv tez orada!")
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃    📹 VIDEO               ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "🔜 Video arxiv tizimi tez orada\n"
            "   to'liq ishga tushiriladi."
        )
        
        keyboard = [[InlineKeyboardButton("« Orqaga", callback_data="menu_ai")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel AI conversation."""
        user_id = update.effective_user.id
        gemini_ai.clear_history(user_id)
        
        await update.message.reply_text(
            "❌ AI suhbat tugatildi.\n\n"
            "/menu - Asosiy menyu"
        )
        return ConversationHandler.END


# Export states
AI_QUERY_INPUT = AI_CONVERSATION
AI_CLARIFICATION = AI_CONVERSATION

# Export
ai_search_handler = AISearchHandler()
