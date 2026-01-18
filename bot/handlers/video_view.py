"""
Video viewing system with real-time and archive playback.
Production-ready with proper camera connection and access control.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, timedelta
from database.models import db
from camera.stream_manager import stream_manager
from utils.logger import logger
from utils.access_control import access_control, time_helper
import io
import os
import cv2

# Conversation states
TIME_RANGE_INPUT = 1


class VideoViewHandler:
    """Handle video viewing with premium UI."""
    
    @staticmethod
    async def show_view_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show video viewing menu."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            "     👁️ VIDEO KO'RISH      \n"
            "━━━━━━━━━━━━\n\n"
            "Rejimni tanlan:\n\n"
            "━━━━━━━━━━━━"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔴 Real-time Ko'rish", callback_data="view_realtime")],
            [InlineKeyboardButton("📅 Vaqt Bo'yicha Ko'rish", callback_data="view_archive")],
            [InlineKeyboardButton("⭐ Sevimli Momentlar", callback_data="view_bookmarks")],
            [InlineKeyboardButton("📥 Yuklab Olish", callback_data="view_download")],
            [InlineKeyboardButton("« Bas Menyu", callback_data="menu_main")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_realtime_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show camera selection for real-time viewing."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        cameras = db.get_cameras_by_organization(user.get('organization_id', 0)) or []
        
        if not cameras:
            text = (
                "━━━━━━━━━━━━\n"
                "      🔴 REAL-TIME         \n"
                "━━━━━━━━━━━━\n\n"
                "📭 Kamera joq!\n\n"
                "Avval kamera qo'shing."
            )
            keyboard = [[InlineKeyboardButton("« Orqaga", callback_data="menu_view")]]
        else:
            text = (
                "━━━━━━━━━━━━\n"
                "      🔴 REAL-TIME         \n"
                "━━━━━━━━━━━━\n\n"
                "Kamerani tanlan:\n\n"
                "━━━━━━━━━━━━"
            )
            
            keyboard = []
            for cam in cameras:
                status_icon = "🟢" if cam.get('status') == 'active' else "🔴"
                btn_text = f"{status_icon} {cam['name']}"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"realtime_{cam['id']}")])
            
            keyboard.append([InlineKeyboardButton("« Orqaga", callback_data="menu_view")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def capture_realtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Capture and send real-time snapshot from camera."""
        query = update.callback_query
        await query.answer("📸 Suwret alinmoqda...")
        
        camera_id = int(query.data.split('_')[-1])
        user_id = update.effective_user.id
        
        # ACCESS CONTROL CHECK
        has_access, error_msg = access_control.check_camera_access(user_id, camera_id)
        if not has_access:
            await query.edit_message_text(error_msg)
            return
        
        camera = db.get_camera(camera_id)
        
        # Show loading message
        await query.edit_message_text(
            f"━━━━━━━━━━━━\n"
            f"   📸 {camera['name'][:18]:<18} \n"
            f"━━━━━━━━━━━━\n\n"
            f"⏳ Kameraga ulanilmoqda...\n"
            f"📍 {camera['ip_address']}:{camera['port']}"
        )
        
        try:
            # Get or create camera connection
            cam_client = stream_manager.get_or_connect_camera(camera_id)
            
            if cam_client is None:
                # Camera not in manager, try to add and connect
                cam_client = stream_manager.add_camera(camera_id)
                if cam_client:
                    cam_client.connect()
            
            if cam_client is None or not cam_client.is_connected:
                text = (
                    f"━━━━━━━━━━━━\n"
                    f"   ❌ ULANISH XATOSI       \n"
                    f"━━━━━━━━━━━━\n\n"
                    f"📹 {camera['name']}\n"
                    f"📍 {camera['ip_address']}:{camera['port']}\n\n"
                    f"━━━━━━━━━━━━\n\n"
                    f"❌ Kameraga ulanib bo'lmadi!\n\n"
                    f"Tekshiring:\n"
                    f"• IP manzil to'g'rimi?\n"
                    f"• Login/parol to'g'rimi?\n"
                    f"• Kamera tarmoqda ishlayaptimi?\n"
                    f"• Port (554) to'g'rimi?"
                )
                keyboard = [
                    [InlineKeyboardButton("🔄 Qayta Urinish", callback_data=f"realtime_{camera_id}")],
                    [InlineKeyboardButton("⚙️ Sazlawlar", callback_data=f"cam_detail_{camera_id}")],
                    [InlineKeyboardButton("« Kameralar", callback_data="view_realtime")]
                ]
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                return
            
            # Capture frame
            frame = cam_client.get_frame()
            
            if frame is None:
                # Try to reconnect and capture again
                cam_client.reconnect()
                frame = cam_client.get_frame()
            
            if frame is None:
                raise Exception("Kameradan rasm olib bo'lmadi")
            
            # Encode frame to JPEG
            success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            if not success:
                raise Exception("Rasm kodlash xatosi")
            
            # Send photo
            photo_bytes = io.BytesIO(buffer.tobytes())
            photo_bytes.name = f"{camera['name']}_snapshot.jpg"
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Get camera info
            cam_info = cam_client.get_info()
            resolution = f"{cam_info.get('width', '?')}x{cam_info.get('height', '?')}"
            
            caption = (
                f"📹 {camera['name']}\n"
                f"⏰ {timestamp}\n"
                f"📍 {camera['ip_address']}\n"
                f"📊 {resolution}"
            )
            
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=photo_bytes,
                caption=caption
            )
            
            # Update camera status to active
            db.update_camera_status(camera_id, 'active')
            
            # Show success with refresh button
            text = (
                f"━━━━━━━━━━━━\n"
                f"   ✅ RASM YUBORILDI       \n"
                f"━━━━━━━━━━━━\n\n"
                f"📹 {camera['name']}\n"
                f"⏰ {timestamp}\n"
                f"📊 {resolution}"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔄 Janalash", callback_data=f"realtime_{camera_id}")],
                [InlineKeyboardButton("⭐ Saqlash", callback_data=f"bookmark_save_{camera_id}")],
                [InlineKeyboardButton("« Kameralar", callback_data="view_realtime")]
            ]
            
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            
        except Exception as e:
            logger.error(f"Realtime capture error: {e}")
            
            # Update camera status to inactive
            db.update_camera_status(camera_id, 'inactive')
            
            text = (
                f"━━━━━━━━━━━━\n"
                f"   ❌ XATOLIK              \n"
                f"━━━━━━━━━━━━\n\n"
                f"📹 {camera['name']}\n\n"
                f"❌ {str(e)}\n\n"
                f"━━━━━━━━━━━━\n\n"
                f"💡 Maslahat:\n"
                f"• Kamera IP ni tekshiring\n"
                f"• Login/parolni tekshiring\n"
                f"• Tarmoq ulanishini tekshiring"
            )
            keyboard = [
                [InlineKeyboardButton("🔄 Qayta Urinish", callback_data=f"realtime_{camera_id}")],
                [InlineKeyboardButton("« Orqaga", callback_data="view_realtime")]
            ]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_archive_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show quick time selection for archive viewing."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            "     📅 VAQT TANLASH       \n"
            "━━━━━━━━━━━━\n\n"
            "Tezkor tanlov:\n\n"
            "━━━━━━━━━━━━"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("⏱️ 10 daqiqa", callback_data="archive_10min"),
                InlineKeyboardButton("⏰ 1 soat", callback_data="archive_1hour")
            ],
            [
                InlineKeyboardButton("📆 Bugun", callback_data="archive_today"),
                InlineKeyboardButton("📆 Kecha", callback_data="archive_yesterday")
            ],
            [InlineKeyboardButton("✍️ Aniq vaqt kiriting", callback_data="archive_custom")],
            [InlineKeyboardButton("« Orqaga", callback_data="menu_view")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def handle_quick_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quick time selection."""
        query = update.callback_query
        await query.answer()
        
        time_type = query.data.replace('archive_', '')
        now = datetime.now()
        
        if time_type == '10min':
            start_time = now - timedelta(minutes=10)
            end_time = now
            label = "So'nggi 10 daqiqa"
        elif time_type == '1hour':
            start_time = now - timedelta(hours=1)
            end_time = now
            label = "So'nggi 1 soat"
        elif time_type == 'today':
            start_time = now.replace(hour=0, minute=0, second=0)
            end_time = now
            label = "Bugun"
        elif time_type == 'yesterday':
            yesterday = now - timedelta(days=1)
            start_time = yesterday.replace(hour=0, minute=0, second=0)
            end_time = yesterday.replace(hour=23, minute=59, second=59)
            label = "Kecha"
        else:
            return
        
        # Store time range
        context.user_data['archive_start'] = start_time
        context.user_data['archive_end'] = end_time
        context.user_data['archive_label'] = label
        
        # Show camera selection
        await VideoViewHandler.show_archive_cameras(update, context)
    
    @staticmethod
    async def show_archive_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show camera selection for archive viewing."""
        query = update.callback_query
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        cameras = db.get_cameras_by_organization(user.get('organization_id', 0)) or []
        
        start_time = context.user_data.get('archive_start')
        end_time = context.user_data.get('archive_end')
        label = context.user_data.get('archive_label', '')
        
        text = (
            "━━━━━━━━━━━━\n"
            "     📹 KAMERA TANLASH     \n"
            "━━━━━━━━━━━━\n\n"
            f"📅 {label}\n"
            f"⏰ {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\n\n"
            "━━━━━━━━━━━━"
        )
        
        keyboard = []
        for cam in cameras:
            btn_text = f"📹 {cam['name']}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"archive_cam_{cam['id']}")])
        
        keyboard.append([InlineKeyboardButton("« Vaqt Tanlash", callback_data="view_archive")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def extract_archive_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Extract and send video from archive."""
        query = update.callback_query
        await query.answer()
        
        camera_id = int(query.data.split('_')[-1])
        camera = db.get_camera(camera_id)
        
        start_time = context.user_data.get('archive_start')
        end_time = context.user_data.get('archive_end')
        label = context.user_data.get('archive_label', '')
        
        # Show processing message
        await query.edit_message_text(
            f"━━━━━━━━━━━━\n"
            f"   ⏳ TAYYORLANMOQDA       \n"
            f"━━━━━━━━━━━━\n\n"
            f"📹 {camera['name']}\n"
            f"📅 {label}\n\n"
            f"⏳ Video qayta ishlanmoqda..."
        )
        
        try:
            # Try to extract video from archive
            from camera.video_recorder import video_recorder
            
            video_path = video_recorder.extract_clip(camera_id, start_time, end_time)
            
            if video_path and os.path.exists(video_path):
                # Send video
                with open(video_path, 'rb') as video_file:
                    await context.bot.send_video(
                        chat_id=query.message.chat_id,
                        video=video_file,
                        caption=f"📹 {camera['name']}\n📅 {label}",
                        supports_streaming=True
                    )
                
                text = (
                    f"━━━━━━━━━━━━\n"
                    f"   ✅ VIDEO YUBORILDI      \n"
                    f"━━━━━━━━━━━━\n\n"
                    f"📹 {camera['name']}\n"
                    f"📅 {label}"
                )
            else:
                text = (
                    f"━━━━━━━━━━━━\n"
                    f"   📭 ARXIV BO'SH          \n"
                    f"━━━━━━━━━━━━\n\n"
                    f"📹 {camera['name']}\n"
                    f"📅 {label}\n\n"
                    f"Bul waqıt aralıǵında video joq.\n\n"
                    f"💡 Video yozish uchun kamerani\n"
                    f"   ON holatiga o'tkazing."
                )
            
            keyboard = [
                [InlineKeyboardButton("📅 Boshqa Vaqt", callback_data="view_archive")],
                [InlineKeyboardButton("« Bas Menyu", callback_data="menu_main")]
            ]
            
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            
        except Exception as e:
            logger.error(f"Archive extract error: {e}")
            text = (
                f"━━━━━━━━━━━━\n"
                f"   ❌ XATOLIK              \n"
                f"━━━━━━━━━━━━\n\n"
                f"{str(e)}"
            )
            keyboard = [[InlineKeyboardButton("« Orqaga", callback_data="view_archive")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_bookmarks(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show saved bookmarks from database."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # Get bookmarks from database
        bookmarks = db.get_bookmarks(user_id)
        
        if not bookmarks:
            text = (
                "━━━━━━━━━━━━\n"
                "     ⭐ QIZIQLILAR         \n"
                "━━━━━━━━━━━━\n\n"
                "📭 Saqlangan momentler joq.\n\n"
                "Real-time koriwde ⭐ Saqlaw\n"
                "tuymesin basin."
            )
            keyboard = [[InlineKeyboardButton("« Arqaga", callback_data="menu_view")]]
        else:
            text = (
                "━━━━━━━━━━━━\n"
                "     ⭐ QIZIQLILAR         \n"
                "━━━━━━━━━━━━\n\n"
                f"📊 Jami: {len(bookmarks)} ta\n\n"
                "━━━━━━━━━━━━\n"
            )
            
            keyboard = []
            for bm in bookmarks[:10]:  # Limit to 10
                camera_name = bm.get('camera_name', 'Kamera')
                timestamp = str(bm.get('timestamp', ''))[:16]
                btn_text = f"📹 {camera_name} - {timestamp}"
                keyboard.append([
                    InlineKeyboardButton(btn_text, callback_data=f"bookmark_view_{bm['id']}"),
                    InlineKeyboardButton("🗑️", callback_data=f"bookmark_delete_{bm['id']}")
                ])
            
            keyboard.append([InlineKeyboardButton("« Arqaga", callback_data="menu_view")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def save_bookmark(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save current moment as bookmark."""
        query = update.callback_query
        await query.answer("⭐ Saqlanmoqda...")
        
        camera_id = int(query.data.split('_')[-1])
        user_id = update.effective_user.id
        
        # ACCESS CONTROL CHECK
        has_access, error_msg = access_control.check_camera_access(user_id, camera_id)
        if not has_access:
            await query.edit_message_text(error_msg)
            return
        
        camera = db.get_camera(camera_id)
        if not camera:
            await query.edit_message_text("❌ Kamera tabilmadi!")
            return
        
        # Save bookmark with UTC timestamp (standardized)
        utc_now = time_helper.now_utc()
        timestamp = utc_now.strftime('%Y-%m-%d %H:%M:%S')
        display_time = time_helper.format_for_display(utc_now)
        name = f"{camera['name']} - {display_time[:10]}"
        
        db.add_bookmark(
            user_id=user_id,
            camera_id=camera_id,
            timestamp=timestamp,
            name=name
        )
        
        text = (
            "━━━━━━━━━━━━\n"
            "   ⭐ SAQLANDI             \n"
            "━━━━━━━━━━━━\n\n"
            f"📹 {camera['name']}\n"
            f"⏰ {timestamp}\n\n"
            "Qiziqlilar boliminde kore alasiz."
        )
        
        keyboard = [
            [InlineKeyboardButton("⭐ Qiziqlilar", callback_data="view_bookmarks")],
            [InlineKeyboardButton("🔄 Jana Suwret", callback_data=f"realtime_{camera_id}")],
            [InlineKeyboardButton("« Arqaga", callback_data="view_realtime")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def delete_bookmark(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Delete a bookmark."""
        query = update.callback_query
        
        bookmark_id = int(query.data.split('_')[-1])
        user_id = update.effective_user.id
        
        deleted = db.delete_bookmark(bookmark_id, user_id)
        
        if deleted:
            await query.answer("🗑️ Oshirildi!")
        else:
            await query.answer("❌ Qatelik!")
        
        # Refresh bookmarks list
        await VideoViewHandler.show_bookmarks(update, context)
    
    @staticmethod
    async def view_bookmark(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View bookmark details."""
        query = update.callback_query
        await query.answer()
        
        bookmark_id = int(query.data.split('_')[-1])
        user_id = update.effective_user.id
        
        # Get bookmark details
        bookmarks = db.get_bookmarks(user_id)
        bookmark = next((b for b in bookmarks if b['id'] == bookmark_id), None)
        
        if not bookmark:
            await query.edit_message_text("❌ Bookmark tabilmadi!")
            return
        
        text = (
            "━━━━━━━━━━━━\n"
            "   ⭐ QIZIQLIQ            \n"
            "━━━━━━━━━━━━\n\n"
            f"📹 Kamera: {bookmark.get('camera_name', 'N/A')}\n"
            f"⏰ Waqit: {bookmark.get('timestamp', 'N/A')}\n"
            f"📅 Saqlandi: {str(bookmark.get('created_at', ''))[:10]}\n"
        )
        
        camera_id = bookmark.get('camera_id')
        keyboard = [
            [InlineKeyboardButton("📹 Kamerani Kor", callback_data=f"realtime_{camera_id}")],
            [InlineKeyboardButton("🗑️ O'shir", callback_data=f"bookmark_delete_{bookmark_id}")],
            [InlineKeyboardButton("« Qiziqlilar", callback_data="view_bookmarks")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_custom_time_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show custom time input prompt."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            "   ✍️ ANIQ WAQT           \n"
            "━━━━━━━━━━━━\n\n"
            "Waqt oralig'in jazin:\n\n"
            "Format: SAAT:MINUT - SAAT:MINUT\n"
            "Misal: 09:00 - 12:00\n\n"
            "━━━━━━━━━━━━\n"
            "❌ Biykarlaw: /cancel"
        )
        
        await query.edit_message_text(text)
        return TIME_RANGE_INPUT
    
    @staticmethod
    async def handle_custom_time_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle custom time range input."""
        text = update.message.text.strip()
        
        try:
            # Parse time range like "09:00 - 12:00"
            parts = text.replace(' ', '').split('-')
            if len(parts) != 2:
                raise ValueError("Qate format")
            
            start_str, end_str = parts
            
            now = datetime.now()
            start_time = datetime.strptime(start_str, '%H:%M').replace(
                year=now.year, month=now.month, day=now.day
            )
            end_time = datetime.strptime(end_str, '%H:%M').replace(
                year=now.year, month=now.month, day=now.day
            )
            
            context.user_data['archive_start'] = start_time
            context.user_data['archive_end'] = end_time
            context.user_data['archive_label'] = f"{start_str} - {end_str}"
            
            # Show camera selection
            user_id = update.effective_user.id
            user = db.get_user(user_id)
            cameras = db.get_cameras_by_organization(user.get('organization_id', 0)) or []
            
            text = (
                "━━━━━━━━━━━━\n"
                "     📹 KAMERA TANLAW     \n"
                "━━━━━━━━━━━━\n\n"
                f"📅 {start_str} - {end_str}\n\n"
                "━━━━━━━━━━━━"
            )
            
            keyboard = []
            for cam in cameras:
                btn_text = f"📹 {cam['name']}"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"archive_cam_{cam['id']}")])
            
            keyboard.append([InlineKeyboardButton("« Arqaga", callback_data="view_archive")])
            
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            return ConversationHandler.END
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Qate format!\n\n"
                f"To'g'ri format: 09:00 - 12:00\n\n"
                "/cancel - Biykarlaw"
            )
            return TIME_RANGE_INPUT
    
    @staticmethod
    async def show_download_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show download options."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            "     📥 JUKLEP ALIW       \n"
            "━━━━━━━━━━━━\n\n"
            "Video juklep aliw ushin avval\n"
            "📅 Waqt boyinsha koriw arqali\n"
            "kerikli videoni tanlan."
        )
        
        keyboard = [
            [InlineKeyboardButton("📅 Waqt Tanlaw", callback_data="view_archive")],
            [InlineKeyboardButton("« Arqaga", callback_data="menu_view")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# Conversation states export
CUSTOM_TIME_INPUT = TIME_RANGE_INPUT

# Export
video_view_handler = VideoViewHandler()

