"""
Export handler for video and data export.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.models import db
from utils.logger import logger
import os


class ExportHandler:
    """Handle video and data exports."""
    
    @staticmethod
    async def show_export_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show export options menu."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃     📥 EXPORT             ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "Eksport turini tanlan:\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        keyboard = [
            [InlineKeyboardButton("📹 Video Eksport", callback_data="export_video")],
            [InlineKeyboardButton("📊 Statistika Eksport", callback_data="export_stats")],
            [InlineKeyboardButton("📋 Hodisalar Ro'yxati", callback_data="export_events")],
            [InlineKeyboardButton("« Bas Menyu", callback_data="menu_main")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def export_video_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show video export options."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃    📹 VIDEO EKSPORT      ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "━━━━ FORMAT ━━━━\n\n"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📹 MP4", callback_data="export_format_mp4"),
                InlineKeyboardButton("🎬 AVI", callback_data="export_format_avi")
            ],
            [InlineKeyboardButton("« Orqaga", callback_data="export_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def export_format_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle format selection."""
        query = update.callback_query
        await query.answer()
        
        format_type = query.data.split('_')[-1].upper()
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃    📹 VIDEO EKSPORT      ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"📦 Format: {format_type}\n\n"
            "━━━━ SIFAT ━━━━\n\n"
        )
        
        context.user_data['export_format'] = format_type
        
        keyboard = [
            [
                InlineKeyboardButton("🔷 HD 1080p", callback_data="export_quality_1080"),
                InlineKeyboardButton("🔶 SD 720p", callback_data="export_quality_720")
            ],
            [InlineKeyboardButton("⚪ Low 480p", callback_data="export_quality_480")],
            [InlineKeyboardButton("« Orqaga", callback_data="export_video")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def export_quality_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quality selection and start export."""
        query = update.callback_query
        await query.answer()
        
        quality = query.data.split('_')[-1]
        format_type = context.user_data.get('export_format', 'MP4')
        
        quality_labels = {'1080': 'HD 1080p', '720': 'SD 720p', '480': 'Low 480p'}
        quality_label = quality_labels.get(quality, quality)
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃    ⏳ TAYYORLANMOQDA      ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"📦 Format: {format_type}\n"
            f"📺 Sifat: {quality_label}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ Video eksport tizimi hozircha\n"
            "   ishlab chiqilmoqda.\n\n"
            "💡 Hozircha individual video ko'rish\n"
            "   orqali yuklab olishingiz mumkin."
        )
        
        keyboard = [
            [InlineKeyboardButton("📅 Video Ko'rish", callback_data="menu_view")],
            [InlineKeyboardButton("« Eksport Menyu", callback_data="export_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def export_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export statistics as text."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        cameras = db.get_cameras_by_organization(user.get('organization_id')) or []
        
        # Build stats text
        from datetime import datetime
        now = datetime.now()
        
        stats_text = f"""
📊 CAM MAX STATISTIKA HISOBOTI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Sana: {now.strftime('%Y-%m-%d %H:%M')}
👤 Foydalanuvchi: {user.get('first_name', 'User')}

━━━━ KAMERALAR ━━━━

📹 Jami kameralar: {len(cameras)}
🟢 Faol: {sum(1 for c in cameras if c.get('status') == 'active')}
🔴 O'chirilgan: {sum(1 for c in cameras if c.get('status') != 'active')}

━━━━ KAMERA RO'YXATI ━━━━
"""
        
        for i, cam in enumerate(cameras, 1):
            status = "🟢" if cam.get('status') == 'active' else "🔴"
            stats_text += f"\n{i}. {status} {cam['name']}"
            stats_text += f"\n   IP: {cam['ip_address']}:{cam['port']}"
        
        if not cameras:
            stats_text += "\n📭 Kameralar yo'q"
        
        stats_text += """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 CAM MAX - AI Video Kuzatuv
"""
        
        # Send as document
        import io
        file_content = stats_text.encode('utf-8')
        file = io.BytesIO(file_content)
        file.name = f"cammax_stats_{now.strftime('%Y%m%d_%H%M')}.txt"
        
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=file,
            caption="📊 Statistika hisoboti"
        )
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃    ✅ YUBORILDI          ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "📊 Statistika fayli yuborildi!"
        )
        
        keyboard = [[InlineKeyboardButton("« Eksport Menyu", callback_data="export_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def export_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export events list."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃    📋 HODISALAR          ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "⚠️ Hodisalar ro'yxati AI qidiruv\n"
            "   orqali avtomatik to'planadi.\n\n"
            "💡 Qidiruv natijalarini saqlash\n"
            "   uchun 💾 Saqlash tugmasini\n"
            "   bosing."
        )
        
        keyboard = [
            [InlineKeyboardButton("🧠 AI Qidiruv", callback_data="menu_ai")],
            [InlineKeyboardButton("« Eksport Menyu", callback_data="export_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# Export
export_handler = ExportHandler()
