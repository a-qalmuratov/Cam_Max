"""
Real AI Search handler with Gemini integration.
Premium conversational AI - Qaraqalpaq tilinde.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.models import db
from camera.stream_manager import stream_manager
from utils.logger import logger
from utils.messages import msg
from ai.gemini_ai import gemini_ai
import cv2
import io
import os

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
            "━━━━━━━━━━━━\n"
            f"    {msg.AI_TITLE}        \n"
            "━━━━━━━━━━━━\n\n"
            f"{msg.AI_GREETING}\n\n"
            "━━━━━━━━━━━━\n\n"
            f"{msg.AI_ASK_ANYTHING}\n\n"
            f"{msg.AI_EXAMPLES}\n"
            f"• {msg.AI_EXAMPLE1}\n"
            f"• {msg.AI_EXAMPLE2}\n\n"
            "━━━━━━━━━━━━\n\n"
            f"{msg.AI_HINT}"
        )
        
        keyboard = [[InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")]]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        
        return AI_CONVERSATION
    
    @staticmethod
    async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any user message with SUPER AQLLI AI."""
        message_text = update.message.text.strip()
        user_id = update.effective_user.id
        
        # Show thinking message
        thinking_msg = await update.message.reply_text(
            "🧠 *Savolingizni tahlil qilyapman...*",
            parse_mode='Markdown'
        )
        
        try:
            # ========== UNIVERSAL AI ANALYST ==========
            # Use smart AI with 6 features:
            # 1. Context memory
            # 2. Typo correction
            # 3. Smart time parsing
            # 4. Follow-up suggestions
            # 5. Daily summary
            # 6. User profiling
            
            from ai.universal_analyst import universal_analyst
            
            result = await universal_analyst.answer_question(
                query=message_text,
                user_id=user_id
            )
            
            if result['success']:
                # Success - send response with keyboard
                if result.get('evidence') and result['evidence'].get('video_path'):
                    # Has video evidence
                    try:
                        await thinking_msg.delete()
                        video_path = result['evidence']['video_path']
                        with open(video_path, 'rb') as video_file:
                            await update.message.reply_video(
                                video=video_file,
                                caption=result['answer'],
                                parse_mode='Markdown',
                                reply_markup=result.get('keyboard')
                            )
                    except Exception as e:
                        logger.warning(f"Could not send video: {e}")
                        await thinking_msg.edit_text(
                            result['answer'],
                            parse_mode='Markdown',
                            reply_markup=result.get('keyboard')
                        )
                elif result.get('evidence') and result['evidence'].get('screenshot'):
                    # Has screenshot
                    try:
                        await thinking_msg.delete()
                        await update.message.reply_photo(
                            photo=io.BytesIO(result['evidence']['screenshot']),
                            caption=result['answer'],
                            parse_mode='Markdown',
                            reply_markup=result.get('keyboard')
                        )
                    except Exception as e:
                        logger.warning(f"Could not send screenshot: {e}")
                        await thinking_msg.edit_text(
                            result['answer'],
                            parse_mode='Markdown',
                            reply_markup=result.get('keyboard')
                        )
                else:
                    # Text only response
                    await thinking_msg.edit_text(
                        result['answer'],
                        parse_mode='Markdown',
                        reply_markup=result.get('keyboard')
                    )
            else:
                # Not camera related or error - show polite rejection
                await thinking_msg.edit_text(
                    result['answer'],
                    parse_mode='Markdown',
                    reply_markup=result.get('keyboard')
                )
            
            return AI_CONVERSATION
            
        except Exception as e:
            logger.error(f"Universal AI error: {e}")
            
            # Fallback to original Gemini handler
            try:
                ai_response = gemini_ai.chat(user_id, message_text)
                
                if not ai_response['success']:
                    keyboard = []
                    if ai_response.get('show_main_menu', False):
                        keyboard = [[InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")]]
                    if keyboard:
                        await thinking_msg.edit_text(ai_response['text'], reply_markup=InlineKeyboardMarkup(keyboard))
                    else:
                        await thinking_msg.edit_text(ai_response['text'])
                    return AI_CONVERSATION
                
                # Check action type
                action = ai_response.get('action')
                
                if action == 'search':
                    await AISearchHandler._execute_archive_search(
                        update, context, ai_response.get('params', {}), thinking_msg
                    )
                    return AI_CONVERSATION
                    
                elif action == 'live_search':
                    await AISearchHandler._execute_live_search(
                        update, context, ai_response.get('params', {}), thinking_msg
                    )
                    return AI_CONVERSATION
                    
                elif action == 'ask':
                    text = (
                        "━━━━━━━━━━━━\n"
                        f"    {msg.AI_QUESTION_TITLE}           \n"
                        "━━━━━━━━━━━━\n\n"
                        f"{ai_response['text']}\n\n"
                        "━━━━━━━━━━━━\n"
                        f"{msg.AI_WRITE_ANSWER}"
                    )
                    await thinking_msg.edit_text(text)
                    return AI_CONVERSATION
                
                else:
                    text = (
                        "━━━━━━━━━━━━\n"
                        f"    {msg.AI_ANSWER_TITLE}            \n"
                        "━━━━━━━━━━━━\n\n"
                        f"{ai_response['text']}\n\n"
                        "━━━━━━━━━━━━\n"
                        f"{msg.AI_ASK_MORE}"
                    )
                    keyboard = [
                        [InlineKeyboardButton(msg.AI_BTN_NEW_QUESTION, callback_data="menu_ai")],
                        [InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")]
                    ]
                    await thinking_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                    return AI_CONVERSATION
                    
            except Exception as e2:
                logger.error(f"Fallback AI error: {e2}")
                await thinking_msg.edit_text(f"❌ Xatolik: {str(e2)}")
                return AI_CONVERSATION
    
    @staticmethod
    async def _execute_live_search(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        params: dict,
        thinking_msg
    ):
        """Search for object in current camera views."""
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        
        if not user:
            await thinking_msg.edit_text(msg.ERROR_USER_NOT_FOUND)
            return
        
        cameras = db.get_cameras_by_organization(user.get('organization_id')) or []
        
        if not cameras:
            await thinking_msg.edit_text(f"{msg.ERROR_CAMERA_NOT_FOUND} Avval kamera qosin.")
            return
        
        # What to search for
        search_query = params.get('object', '') or params.get('query', "ob'ekt")
        if params.get('color'):
            search_query = f"{params['color']} {search_query}"
        
        await thinking_msg.edit_text(
            f"{msg.AI_SEARCHING}\n"
            f"🎯 \"{search_query}\"\n\n"
            f"{msg.AI_PLEASE_WAIT}"
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
                "━━━━━━━━━━━━\n"
                f"    {msg.AI_FOUND}            \n"
                "━━━━━━━━━━━━\n\n"
                f"🎯 \"{search_query}\"\n\n"
                "━━━━━━━━━━━━\n\n"
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
                [InlineKeyboardButton(msg.AI_BTN_SEARCH_AGAIN, callback_data="menu_ai")],
                [InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")]
            ]
            
            await thinking_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            
        else:
            text = (
                "━━━━━━━━━━━━\n"
                f"    {msg.AI_NOT_FOUND}          \n"
                "━━━━━━━━━━━━\n\n"
                f"🎯 \"{search_query}\"\n\n"
                "━━━━━━━━━━━━\n\n"
                f"❌ {len(cameras)} {msg.AI_CAMERAS_CHECKED},\n"
                "   hech qayerinde tabilmadi.\n\n"
                f"{msg.AI_TRY_ANOTHER}"
            )
            
            keyboard = [
                [InlineKeyboardButton(msg.AI_BTN_SEARCH_ARCHIVE, callback_data="view_archive")],
                [InlineKeyboardButton(msg.AI_BTN_SEARCH_AGAIN, callback_data="menu_ai")],
                [InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")]
            ]
            
            await thinking_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def _execute_archive_search(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        params: dict,
        thinking_msg
    ):
        """Search in video archive."""
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        
        if not user:
            await thinking_msg.edit_text(msg.ERROR_USER_NOT_FOUND)
            return
        
        # Build search description
        search_query = params.get('object', "ob'ekt")
        if params.get('color'):
            search_query = f"{params['color']} {search_query}"
        
        time_range = params.get('time', 'bugun')
        camera = params.get('camera', 'barliq kameralar')
        
        text = (
            "━━━━━━━━━━━━\n"
            f"    {msg.AI_ARCHIVE_TITLE}      \n"
            "━━━━━━━━━━━━\n\n"
            f"🎯 Izlew: \"{search_query}\"\n"
            f"📅 Waqit: {time_range}\n"
            f"📹 Kamera: {camera}\n\n"
            "⏳ DB'dan qidirilmoqda...\n"
        )
        
        await thinking_msg.edit_text(text)
        
        # REAL DB SEARCH using nlp/query_parser.py
        try:
            from nlp.query_parser import search_engine
            
            # Build search query string from params
            query_str = ""
            if params.get('camera'):
                query_str += f"{params['camera']}-kamera "
            if params.get('color'):
                query_str += f"{params['color']} "
            if params.get('object'):
                query_str += f"{params['object']} "
            if params.get('action'):
                query_str += f"{params['action']} "
            if params.get('time'):
                query_str += params['time']
            
            if not query_str.strip():
                query_str = "bugun"
            
            # Execute REAL search
            search_result = search_engine.search(query_str, user_id)
            results = search_result.get('results', [])
            
            if results:
                # Show results
                text = (
                    "━━━━━━━━━━━━\n"
                    f"    ✅ NATIJALAR            \n"
                    "━━━━━━━━━━━━\n\n"
                    f"🎯 \"{search_query}\" - {len(results)} ta topildi\n\n"
                )
                
                # Show top 5 results
                for i, result in enumerate(results[:5]):
                    cam_id = result.get('camera_id', '?')
                    timestamp = result.get('timestamp', 'N/A')
                    obj_type = result.get('object_type', 'N/A')
                    text += f"📍 {i+1}. Kamera {cam_id} - {timestamp}\n"
                    text += f"   └ {obj_type}\n\n"
                
                if len(results) > 5:
                    text += f"... va yana {len(results) - 5} ta\n\n"
                
                text += "━━━━━━━━━━━━"
                
                # Save results to context for view_video
                context.user_data['ai_search_results'] = results
                
                keyboard = [
                    [InlineKeyboardButton("📹 Birinchi natijani ko'rish", callback_data="ai_view_video_0")],
                    [InlineKeyboardButton(msg.AI_BTN_SEARCH_AGAIN, callback_data="menu_ai")],
                    [InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")]
                ]
            else:
                # No results
                text = (
                    "━━━━━━━━━━━━\n"
                    f"    ❌ TOPILMADI           \n"
                    "━━━━━━━━━━━━\n\n"
                    f"🎯 \"{search_query}\" - topilmadi\n\n"
                    "💡 Tavsiyalar:\n"
                    "• Waqit oralig'ini kengaytin\n"
                    "• Boshqa kamerani sinab ko'rin\n"
                    "• Realtime qidiruvni ishlatin\n\n"
                    "━━━━━━━━━━━━"
                )
                
                keyboard = [
                    [InlineKeyboardButton(msg.AI_BTN_REALTIME_SEARCH, callback_data="menu_ai")],
                    [InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")]
                ]
            
        except Exception as e:
            logger.error(f"Archive search error: {e}")
            text = (
                "━━━━━━━━━━━━\n"
                f"    ❌ XATOLIK             \n"
                "━━━━━━━━━━━━\n\n"
                f"Qidiruv xatosi: {str(e)}\n\n"
                "Realtime qidiruvni sinab ko'rin."
            )
            
            keyboard = [
                [InlineKeyboardButton(msg.AI_BTN_REALTIME_SEARCH, callback_data="menu_ai")],
                [InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")]
            ]
        
        await thinking_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def handle_clarification(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle clarification - redirects to main handler."""
        return await AISearchHandler.handle_query(update, context)
    
    @staticmethod
    async def view_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View video evidence from search results."""
        query = update.callback_query
        await query.answer("📹 Yuklanmoqda...")
        
        # Get result index from callback data (e.g., "ai_view_video_0")
        try:
            index = int(query.data.split('_')[-1])
        except:
            index = 0
        
        # Get saved results from context
        results = context.user_data.get('ai_search_results', [])
        
        if not results or index >= len(results):
            text = (
                "━━━━━━━━━━━━\n"
                "    ❌ XATOLIK             \n"
                "━━━━━━━━━━━━\n\n"
                "Natijalar topilmadi.\n"
                "Qayta qidiring."
            )
            keyboard = [[InlineKeyboardButton(msg.BTN_BACK, callback_data="menu_ai")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        # Get specific result
        result = results[index]
        camera_id = result.get('camera_id', '?')
        timestamp = result.get('timestamp', 'N/A')
        obj_type = result.get('object_type', 'N/A')
        confidence = result.get('confidence', 0)
        image_path = result.get('image_path')
        
        # Format timestamp for display
        try:
            from utils.access_control import time_helper
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            display_time = time_helper.format_for_display(dt)
        except:
            display_time = timestamp
        
        text = (
            "━━━━━━━━━━━━\n"
            "    📹 DETECTION TAFSILATI  \n"
            "━━━━━━━━━━━━\n\n"
            f"📍 Kamera: {camera_id}\n"
            f"⏰ Waqit: {display_time}\n"
            f"🎯 Ob'ekt: {obj_type}\n"
            f"📊 Aniqlik: {confidence:.0%}\n\n"
            "━━━━━━━━━━━━\n\n"
        )
        
        # Add navigation if multiple results
        nav_buttons = []
        if index > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"ai_view_video_{index-1}"))
        if index < len(results) - 1:
            nav_buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"ai_view_video_{index+1}"))
        
        keyboard = []
        if nav_buttons:
            keyboard.append(nav_buttons)
        keyboard.append([InlineKeyboardButton("🔍 Natijalar", callback_data="menu_ai")])
        keyboard.append([InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")])
        
        # Send image if available
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as photo:
                    await query.message.reply_photo(
                        photo=photo,
                        caption=text
                    )
                await query.delete_message()
            except Exception as e:
                logger.warning(f"Could not send image: {e}")
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            text += "⚠️ Suwret tabilmadi (arxiv o'chirilgan)\n"
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def handle_followup(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle follow-up button clicks from smart AI."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # Extract follow-up query from callback data
        # Format: "followup:Query text"
        callback_data = query.data
        if not callback_data.startswith('followup:'):
            return
        
        followup_query = callback_data.replace('followup:', '')
        
        # Send thinking message
        await query.edit_message_text("🧠 *Tahlil qilyapman...*", parse_mode='Markdown')
        
        try:
            from ai.universal_analyst import universal_analyst
            
            result = await universal_analyst.answer_question(
                query=followup_query,
                user_id=user_id
            )
            
            if result.get('evidence') and result['evidence'].get('video_path'):
                try:
                    await query.delete_message()
                    video_path = result['evidence']['video_path']
                    with open(video_path, 'rb') as video_file:
                        await context.bot.send_video(
                            chat_id=update.effective_chat.id,
                            video=video_file,
                            caption=result['answer'],
                            parse_mode='Markdown',
                            reply_markup=result.get('keyboard')
                        )
                except Exception as e:
                    logger.warning(f"Could not send video: {e}")
                    await query.edit_message_text(
                        result['answer'],
                        parse_mode='Markdown',
                        reply_markup=result.get('keyboard')
                    )
            else:
                await query.edit_message_text(
                    result['answer'],
                    parse_mode='Markdown',
                    reply_markup=result.get('keyboard')
                )
                
        except Exception as e:
            logger.error(f"Follow-up error: {e}")
            await query.edit_message_text(f"❌ Xatolik: {str(e)}")
    
    @staticmethod
    async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel AI conversation."""
        user_id = update.effective_user.id
        gemini_ai.clear_history(user_id)
        
        await update.message.reply_text(
            f"{msg.AI_CANCELLED}\n\n"
            "/menu - Tiykargi menyu"
        )
        return ConversationHandler.END


# Export states
AI_QUERY_INPUT = AI_CONVERSATION
AI_CLARIFICATION = AI_CONVERSATION

# Export
ai_search_handler = AISearchHandler()
