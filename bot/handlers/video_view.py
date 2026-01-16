"""
Video viewing system with real-time and archive playback.
Production-ready with proper camera connection handling.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, timedelta
from database.models import db
from camera.stream_manager import stream_manager
from utils.logger import logger
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
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃     👁️ VIDEO KO'RISH      ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "Rejimni tanlang:\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔴 Real-time Ko'rish", callback_data="view_realtime")],
            [InlineKeyboardButton("📅 Vaqt Bo'yicha Ko'rish", callback_data="view_archive")],
            [InlineKeyboardButton("⭐ Sevimli Momentlar", callback_data="view_bookmarks")],
            [InlineKeyboardButton("📥 Yuklab Olish", callback_data="view_download")],
            [InlineKeyboardButton("« Asosiy Menyu", callback_data="menu_main")]
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
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃      🔴 REAL-TIME         ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "📭 Kamera yo'q!\n\n"
                "Avval kamera qo'shing."
            )
            keyboard = [[InlineKeyboardButton("« Orqaga", callback_data="menu_view")]]
        else:
            text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃      🔴 REAL-TIME         ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "Kamerani tanlang:\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━"
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
        await query.answer()
        
        camera_id = int(query.data.split('_')[-1])
        camera = db.get_camera(camera_id)
        
        if not camera:
            await query.edit_message_text("❌ Kamera topilmadi!")
            return
        
        # Verify ownership
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        if camera.get('organization_id') != user.get('organization_id'):
            await query.edit_message_text("❌ Bu kamera sizga tegishli emas!")
            return
        
        # Show loading message
        await query.edit_message_text(
            f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃   📸 {camera['name'][:18]:<18} ┃\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
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
                    f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    f"┃   ❌ ULANISH XATOSI       ┃\n"
                    f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    f"📹 {camera['name']}\n"
                    f"📍 {camera['ip_address']}:{camera['port']}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"❌ Kameraga ulanib bo'lmadi!\n\n"
                    f"Tekshiring:\n"
                    f"• IP manzil to'g'rimi?\n"
                    f"• Login/parol to'g'rimi?\n"
                    f"• Kamera tarmoqda ishlayaptimi?\n"
                    f"• Port (554) to'g'rimi?"
                )
                keyboard = [
                    [InlineKeyboardButton("🔄 Qayta Urinish", callback_data=f"realtime_{camera_id}")],
                    [InlineKeyboardButton("⚙️ Sozlamalar", callback_data=f"cam_detail_{camera_id}")],
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
                f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                f"┃   ✅ RASM YUBORILDI       ┃\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"📹 {camera['name']}\n"
                f"⏰ {timestamp}\n"
                f"📊 {resolution}"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔄 Yangilash", callback_data=f"realtime_{camera_id}")],
                [InlineKeyboardButton("⭐ Saqlash", callback_data=f"bookmark_save_{camera_id}")],
                [InlineKeyboardButton("« Kameralar", callback_data="view_realtime")]
            ]
            
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            
        except Exception as e:
            logger.error(f"Realtime capture error: {e}")
            
            # Update camera status to inactive
            db.update_camera_status(camera_id, 'inactive')
            
            text = (
                f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                f"┃   ❌ XATOLIK              ┃\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"📹 {camera['name']}\n\n"
                f"❌ {str(e)}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
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
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃     📅 VAQT TANLASH       ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "Tezkor tanlov:\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━"
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
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃     📹 KAMERA TANLASH     ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"📅 {label}\n"
            f"⏰ {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━"
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
            f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃   ⏳ TAYYORLANMOQDA       ┃\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
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
                    f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    f"┃   ✅ VIDEO YUBORILDI      ┃\n"
                    f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    f"📹 {camera['name']}\n"
                    f"📅 {label}"
                )
            else:
                text = (
                    f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    f"┃   📭 ARXIV BO'SH          ┃\n"
                    f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    f"📹 {camera['name']}\n"
                    f"📅 {label}\n\n"
                    f"Bu vaqt oralig'ida video yo'q.\n\n"
                    f"💡 Video yozish uchun kamerani\n"
                    f"   ON holatiga o'tkazing."
                )
            
            keyboard = [
                [InlineKeyboardButton("📅 Boshqa Vaqt", callback_data="view_archive")],
                [InlineKeyboardButton("« Asosiy Menyu", callback_data="menu_main")]
            ]
            
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            
        except Exception as e:
            logger.error(f"Archive extract error: {e}")
            text = (
                f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                f"┃   ❌ XATOLIK              ┃\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"{str(e)}"
            )
            keyboard = [[InlineKeyboardButton("« Orqaga", callback_data="view_archive")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_bookmarks(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show saved bookmarks."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # Get bookmarks from database (placeholder)
        bookmarks = []  # TODO: Implement bookmark storage
        
        if not bookmarks:
            text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃     ⭐ SEVIMLILAR         ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "📭 Saqlangan momentlar yo'q.\n\n"
                "Real-time ko'rishda ⭐ Saqlash\n"
                "tugmasini bosing."
            )
            keyboard = [[InlineKeyboardButton("« Orqaga", callback_data="menu_view")]]
        else:
            text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃     ⭐ SEVIMLILAR         ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            )
            
            keyboard = []
            for bm in bookmarks:
                btn_text = f"📹 {bm['timestamp']} - {bm['camera_name']}"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"bookmark_{bm['id']}")])
            
            keyboard.append([InlineKeyboardButton("« Orqaga", callback_data="menu_view")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_download_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show download options."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃     📥 YUKLAB OLISH       ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "Video yuklab olish uchun avval\n"
            "📅 Vaqt bo'yicha ko'rish orqali\n"
            "kerakli videoni tanlang."
        )
        
        keyboard = [
            [InlineKeyboardButton("📅 Vaqt Tanlash", callback_data="view_archive")],
            [InlineKeyboardButton("« Orqaga", callback_data="menu_view")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# Export
video_view_handler = VideoViewHandler()
