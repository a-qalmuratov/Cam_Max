"""Analytics handler with real statistics."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.models import db
from database.v2_models import v2db
from camera.video_recorder import video_recorder
from datetime import datetime, timedelta
from utils.logger import logger
import os

class AnalyticsHandler:
    """Handle analytics and statistics display."""
    
    @staticmethod
    async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main analytics dashboard."""
        query = update.callback_query
        if query:
            await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        
        # Get statistics
        cameras = db.get_all_cameras()
        user_org_id = user.get('organization_id')
        user_cameras = [c for c in cameras if c.get('organization_id') == user_org_id]
        
        # Count active cameras
        active_cameras = sum(1 for c in user_cameras if c.get('status') == 'active')
        
        # Count recordings
        recording_count = sum(1 for cam_id in video_recorder.is_recording 
                             if video_recorder.is_recording.get(cam_id))
        
        # Get recent detections
        recent_detections = db.get_recent_detections(limit=10)
        detection_count = len(recent_detections)
        
        # Calculate storage usage
        storage_mb = 0
        try:
            from utils.config import CACHE_DIR
            recordings_dir = CACHE_DIR / 'recordings'
            if recordings_dir.exists():
                for f in recordings_dir.iterdir():
                    if f.is_file():
                        storage_mb += f.stat().st_size / (1024 * 1024)
        except:
            pass
        
        keyboard = [
            [InlineKeyboardButton("📹 Kameralar statistikasi", callback_data="stats_cameras")],
            [InlineKeyboardButton("🤖 AI aniqlashlar", callback_data="stats_detections")],
            [InlineKeyboardButton("💾 Saqlash holati", callback_data="stats_storage")],
            [InlineKeyboardButton("📈 Faollik grafigi", callback_data="stats_activity")],
            [InlineKeyboardButton("« Bas Menyu", callback_data="menu_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "╔═══════════════════════╗\n"
            "║   📊 STATISTIKA       ║\n"
            "╚═══════════════════════╝\n\n"
            f"📹 **Kameralar:** {len(user_cameras)} ta\n"
            f"   ├─ 🟢 Faol: {active_cameras}\n"
            f"   └─ 🔴 Nofaol: {len(user_cameras) - active_cameras}\n\n"
            f"🔴 **Yozuv:** {recording_count} ta kamerada\n\n"
            f"🤖 **AI aniqlashlar:** {detection_count} ta (so'nggi)\n\n"
            f"💾 **Saqlash:** {storage_mb:.1f} MB ishlatilgan\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Batafsil ko'rish uchun tanlan:"
        )
        
        if query:
            await query.edit_message_text(message, reply_markup=reply_markup)
        elif update.message:
            await update.message.reply_text(message, reply_markup=reply_markup)
    
    @staticmethod
    async def show_camera_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show camera statistics."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        cameras = db.get_all_cameras()
        user_org_id = user.get('organization_id')
        user_cameras = [c for c in cameras if c.get('organization_id') == user_org_id]
        
        message = "📹 **KAMERALAR STATISTIKASI**\n\n"
        
        for cam in user_cameras:
            status_icon = "🟢" if cam.get('status') == 'active' else "🔴"
            is_recording = video_recorder.is_recording.get(cam['id'], False)
            rec_icon = "⏺️" if is_recording else "⏹️"
            
            message += (
                f"{status_icon} **{cam['name']}**\n"
                f"   ├─ IP: `{cam['ip_address']}`\n"
                f"   ├─ Turi: {cam.get('camera_type', 'generic')}\n"
                f"   └─ Yozuv: {rec_icon} {'Yozilmoqda' if is_recording else 'Toxtatilgan'}\n\n"
            )
        
        if not user_cameras:
            message += "❌ Hech qanday kamera topilmadi.\n\nKamera qo'shish: /sozlash"
        
        keyboard = [[InlineKeyboardButton("« Orqaga", callback_data="menu_analytics")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    @staticmethod
    async def show_detection_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show AI detection statistics."""
        query = update.callback_query
        await query.answer()
        
        # Get recent detections
        detections = db.get_recent_detections(limit=50)
        
        # Count by type
        type_counts = {}
        for det in detections:
            obj_type = det.get('object_type', 'unknown')
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        message = "🤖 **AI ANIQLASHLAR**\n\n"
        
        if type_counts:
            message += "📊 **Taqsimlanishi:**\n"
            for obj_type, count in sorted(type_counts.items(), key=lambda x: -x[1])[:10]:
                bar_length = min(count, 10)
                bar = "█" * bar_length
                message += f"  {obj_type}: {bar} ({count})\n"
            
            message += f"\n📈 Jami: {len(detections)} ta aniqlash"
        else:
            message += "❌ Hali aniqlashlar yo'q.\n\nTest qilish: /ai_test"
        
        keyboard = [[InlineKeyboardButton("« Orqaga", callback_data="menu_analytics")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    @staticmethod
    async def show_storage_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show storage statistics."""
        query = update.callback_query
        await query.answer()
        
        storage_info = {
            'total_mb': 0,
            'video_count': 0,
            'oldest': None,
            'newest': None
        }
        
        try:
            from utils.config import CACHE_DIR
            recordings_dir = CACHE_DIR / 'recordings'
            if recordings_dir.exists():
                files = list(recordings_dir.glob('*.mp4'))
                storage_info['video_count'] = len(files)
                
                for f in files:
                    storage_info['total_mb'] += f.stat().st_size / (1024 * 1024)
                
                if files:
                    sorted_files = sorted(files, key=lambda x: x.stat().st_mtime)
                    oldest_time = datetime.fromtimestamp(sorted_files[0].stat().st_mtime)
                    newest_time = datetime.fromtimestamp(sorted_files[-1].stat().st_mtime)
                    storage_info['oldest'] = oldest_time.strftime('%Y-%m-%d %H:%M')
                    storage_info['newest'] = newest_time.strftime('%Y-%m-%d %H:%M')
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
        
        message = (
            "💾 **SAQLASH HOLATI**\n\n"
            f"📂 Video fayllar: {storage_info['video_count']} ta\n"
            f"📦 Hajmi: {storage_info['total_mb']:.1f} MB\n"
            f"📅 Eng eski: {storage_info['oldest'] or 'N/A'}\n"
            f"📅 Eng Jana: {storage_info['newest'] or 'N/A'}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🗑️ Tozalash: /cleanup_archives\n"
            f"⚙️ Saqlash muddati: 30 kun"
        )
        
        keyboard = [[InlineKeyboardButton("« Orqaga", callback_data="menu_analytics")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    @staticmethod
    async def show_activity_graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show activity graph (simplified text version)."""
        query = update.callback_query
        await query.answer()
        
        # Get last 7 days activity
        today = datetime.now().date()
        activity = {}
        
        for i in range(7):
            day = today - timedelta(days=i)
            activity[day.strftime('%a')] = 0
        
        # Count detections per day
        detections = db.get_recent_detections(limit=100)
        for det in detections:
            det_time = det.get('detected_at')
            if det_time:
                try:
                    det_date = datetime.fromisoformat(det_time).date()
                    day_name = det_date.strftime('%a')
                    if day_name in activity:
                        activity[day_name] += 1
                except:
                    pass
        
        message = "📈 **HAFTALIK FAOLLIK**\n\n"
        
        max_val = max(activity.values()) if activity.values() else 1
        for day, count in reversed(list(activity.items())):
            bar_length = int((count / max_val) * 10) if max_val > 0 else 0
            bar = "█" * bar_length + "░" * (10 - bar_length)
            message += f"{day}: {bar} {count}\n"
        
        message += f"\n📊 Jami: {sum(activity.values())} ta aniqlash"
        
        keyboard = [[InlineKeyboardButton("« Orqaga", callback_data="menu_analytics")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    @staticmethod
    async def handle_analytics_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle analytics sub-menu callbacks."""
        query = update.callback_query
        callback_data = query.data
        
        if callback_data == "stats_cameras":
            await AnalyticsHandler.show_camera_stats(update, context)
        elif callback_data == "stats_detections":
            await AnalyticsHandler.show_detection_stats(update, context)
        elif callback_data == "stats_storage":
            await AnalyticsHandler.show_storage_stats(update, context)
        elif callback_data == "stats_activity":
            await AnalyticsHandler.show_activity_graph(update, context)

analytics_handler = AnalyticsHandler()
