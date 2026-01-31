"""Recording management handler."""
from telegram import Update
from telegram.ext import ContextTypes
from database.models import db
from camera.video_recorder import video_recorder
from utils.logger import logger

class RecordingHandler:
    """Handle video recording management."""
    
    @staticmethod
    async def start_recording_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start recording on all cameras."""
        cameras = db.get_all_cameras()
        
        if not cameras:
            await update.message.reply_text(
                "❌ Hech qanday kamera sozlanmagan."
            )
            return
        
        await update.message.reply_text(
            f"📹 {len(cameras)} ta kamerada yozuv boshlanmoqda..."
        )
        
        for camera in cameras:
            try:
                video_recorder.start_recording(camera['id'])
            except Exception as e:
                logger.error(f"Error starting recording for camera {camera['id']}: {e}")
        
        await update.message.reply_text(
            f"✅ Barcha kameralarda yozuv boshlandi!\n\n"
            f"📊 Yozuvlar:\n"
            f"- Davomiyligi: 10 daqiqalik segmentlar\n"
            f"- Saqlash: 30 kun\n"
            f"- To'xtatish: /stop_recording"
        )
    
    @staticmethod
    async def stop_recording_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop recording on all cameras."""
        cameras = db.get_all_cameras()
        
        for camera in cameras:
            video_recorder.stop_recording(camera['id'])
        
        await update.message.reply_text(
            "⏹️ Barcha kameralarda yozuv to'xtatildi."
        )
    
    @staticmethod
    async def recording_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show recording status."""
        cameras = db.get_all_cameras()
        
        message = "📹 **YOZUV HOLATI**\n\n"
        
        for camera in cameras:
            is_recording = video_recorder.is_recording.get(camera['id'], False)
            status_icon = "🔴" if is_recording else "⚫️"
            status_text = "Yozilmoqda" if is_recording else "To'xtagan"
            
            message += f"{status_icon} **{camera['name']}**: {status_text}\n"
        
        message += (
            f"\n💾 Arxiv: `recordings/` papkada\n"
            f"🗑️ Tozalash: /cleanup_archives"
        )
        
        await update.message.reply_text(message)

# Export
recording_handler = RecordingHandler()
