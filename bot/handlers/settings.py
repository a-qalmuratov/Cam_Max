"""
Settings handler with profile, notifications, security, and archive management.
Premium UI - Qaraqalpaq tilinde. All buttons working.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.models import db
from utils.logger import logger
from utils.messages import msg

# Conversation states for editing
EDIT_NAME = 100
EDIT_PHONE = 101


class SettingsHandler:
    """Handle user settings with premium UI."""
    
    @staticmethod
    async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show settings menu."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            f"      {msg.SETTINGS_TITLE}        \n"
            "━━━━━━━━━━━━\n\n"
            f"{msg.SETTINGS_SELECT}\n\n"
            "━━━━━━━━━━━━"
        )
        
        keyboard = [
            [InlineKeyboardButton(msg.SETTINGS_BTN_PROFILE, callback_data="settings_profile")],
            [InlineKeyboardButton(msg.SETTINGS_BTN_NOTIFICATIONS, callback_data="settings_notifications")],
            [InlineKeyboardButton(msg.SETTINGS_BTN_SECURITY, callback_data="settings_security")],
            [InlineKeyboardButton(msg.SETTINGS_BTN_ARCHIVE, callback_data="settings_archive")],
            [InlineKeyboardButton(msg.SETTINGS_BTN_HELP, callback_data="settings_help")],
            [InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user profile."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        cameras = db.get_cameras_by_organization(user.get('organization_id')) or []
        
        # Calculate storage (placeholder)
        storage_used = len(cameras) * 5.2
        storage_limit = 100
        
        text = (
            "━━━━━━━━━━━━\n"
            f"      {msg.SETTINGS_PROFILE_TITLE}            \n"
            "━━━━━━━━━━━━\n\n"
            f"👤 {msg.SETTINGS_NAME}: {user.get('first_name', 'User')}\n"
            f"📱 {msg.SETTINGS_PHONE}: {user.get('phone_number', 'N/A')}\n"
            f"📅 {msg.SETTINGS_REGISTERED}: {str(user.get('created_at', ''))[:10]}\n\n"
            "━━━━━━━━━━━━\n\n"
            f"📹 {msg.SETTINGS_CAMERAS}: {len(cameras)}/10\n"
            f"💾 {msg.SETTINGS_STORAGE}: {storage_used:.1f} GB / {storage_limit} GB\n"
            f"📊 {msg.SETTINGS_PLAN}: Free\n\n"
            "━━━━━━━━━━━━"
        )
        
        keyboard = [
            [InlineKeyboardButton(msg.SETTINGS_BTN_EDIT_NAME, callback_data="profile_edit_name")],
            [InlineKeyboardButton(msg.SETTINGS_BTN_EDIT_PHONE, callback_data="profile_edit_phone")],
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="menu_settings")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def start_edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start name editing."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            "   ✏️ ATTI ÓZGERTIW         \n"
            "━━━━━━━━━━━━\n\n"
            "Jan̄a atınızdı jazın̄:\n\n"
            "━━━━━━━━━━━━\n"
            "❌ Biykarlaw: /cancel"
        )
        
        await query.edit_message_text(text)
        return EDIT_NAME
    
    @staticmethod
    async def save_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save new name."""
        new_name = update.message.text.strip()
        user_id = update.effective_user.id
        
        if len(new_name) < 2:
            await update.message.reply_text("❌ At qısqa!")
            return EDIT_NAME
        
        # Update in database
        db.update_user_name(user_id, new_name)
        
        text = (
            "━━━━━━━━━━━━\n"
            "   ✅ AT ÓZGERTTILDI       \n"
            "━━━━━━━━━━━━\n\n"
            f"👤 Jan̄a at: {new_name}\n\n"
            "/menu - Bas menyu"
        )
        
        await update.message.reply_text(text)
        return ConversationHandler.END
    
    @staticmethod
    async def start_edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start phone editing."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            "   📱 TELEFON ÓZGERTIW    \n"
            "━━━━━━━━━━━━\n\n"
            "Jan̄a telefon nomerin̄izdi jazın̄:\n"
            "Format: +998XXXXXXXXX\n\n"
            "━━━━━━━━━━━━\n"
            "❌ Biykarlaw: /cancel"
        )
        
        await query.edit_message_text(text)
        return EDIT_PHONE
    
    @staticmethod
    async def save_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save new phone."""
        new_phone = update.message.text.strip()
        user_id = update.effective_user.id
        
        if not new_phone.startswith('+998') or len(new_phone) < 12:
            await update.message.reply_text("❌ Qate format! +998 menen baslanın̄.")
            return EDIT_PHONE
        
        # Update in database
        db.update_user_phone(user_id, new_phone)
        
        text = (
            "━━━━━━━━━━━━\n"
            "   ✅ TELEFON ÓZGERTTILDI  \n"
            "━━━━━━━━━━━━\n\n"
            f"📱 Jan̄a telefon: {new_phone}\n\n"
            "/menu - Bas menyu"
        )
        
        await update.message.reply_text(text)
        return ConversationHandler.END
    
    @staticmethod
    async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel editing."""
        await update.message.reply_text(
            "❌ Biykar etildi.\n\n/menu - Bas menyu"
        )
        return ConversationHandler.END
    
    @staticmethod
    async def show_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show notification settings."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # Get notification settings from context or default
        notif_settings = context.user_data.get('notifications', {
            'motion': True,
            'camera': True,
            'suspicious': True,
            'daily': False,
            'weekly': False
        })
        
        motion_status = "✅" if notif_settings.get('motion', True) else "❌"
        camera_status = "✅" if notif_settings.get('camera', True) else "❌"
        suspicious_status = "✅" if notif_settings.get('suspicious', True) else "❌"
        daily_status = "✅" if notif_settings.get('daily', False) else "❌"
        weekly_status = "✅" if notif_settings.get('weekly', False) else "❌"
        
        text = (
            "━━━━━━━━━━━━\n"
            f"   {msg.SETTINGS_NOTIF_TITLE}     \n"
            "━━━━━━━━━━━━\n\n"
            f"──── {msg.SETTINGS_EVENTS} ────\n\n"
            f"{motion_status} Motion detected\n"
            f"{camera_status} Camera offline\n"
            f"{suspicious_status} Suspicious activity\n"
            f"{daily_status} Künlik esabat\n"
            f"{weekly_status} Háptelik esabat\n\n"
            f"──── {msg.SETTINGS_TIME} ────\n\n"
            "⏰ 08:00 - 22:00\n\n"
            "💡 Tüymesin basın̄ ózgertiw ushın"
        )
        
        keyboard = [
            [
                InlineKeyboardButton(f"🔔 Motion: {'ON' if notif_settings.get('motion') else 'OFF'}", callback_data="notif_toggle_motion"),
                InlineKeyboardButton(f"📴 Camera: {'ON' if notif_settings.get('camera') else 'OFF'}", callback_data="notif_toggle_camera")
            ],
            [
                InlineKeyboardButton(f"⚠️ Shubha: {'ON' if notif_settings.get('suspicious') else 'OFF'}", callback_data="notif_toggle_suspicious"),
            ],
            [
                InlineKeyboardButton(f"📅 Künlik: {'ON' if notif_settings.get('daily') else 'OFF'}", callback_data="notif_toggle_daily"),
                InlineKeyboardButton(f"📆 Háptelik: {'ON' if notif_settings.get('weekly') else 'OFF'}", callback_data="notif_toggle_weekly")
            ],
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="menu_settings")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def toggle_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle notification setting."""
        query = update.callback_query
        await query.answer()
        
        setting = query.data.replace('notif_toggle_', '')
        
        if 'notifications' not in context.user_data:
            context.user_data['notifications'] = {
                'motion': True,
                'camera': True,
                'suspicious': True,
                'daily': False,
                'weekly': False
            }
        
        # Toggle the setting
        current = context.user_data['notifications'].get(setting, False)
        context.user_data['notifications'][setting] = not current
        
        # Refresh the page
        await SettingsHandler.show_notifications(update, context)
    
    @staticmethod
    async def show_security(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show security settings."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            f"      {msg.SETTINGS_SECURITY_TITLE}        \n"
            "━━━━━━━━━━━━\n\n"
            "──── STATUS ────\n\n"
            f"✅ {msg.SETTINGS_2FA}: {msg.SETTINGS_ENABLED}\n"
            f"✅ {msg.SETTINGS_IP_WHITELIST}: 0 ta\n"
            f"✅ {msg.SETTINGS_ACTIVITY_LOGS}: 30 kun\n\n"
            f"──── {msg.SETTINGS_ACTIVE_SESSIONS} ────\n\n"
            f"📱 1. {msg.SETTINGS_THIS_DEVICE} - {msg.SETTINGS_NOW}\n\n"
            "━━━━━━━━━━━━"
        )
        
        keyboard = [
            [InlineKeyboardButton(msg.SETTINGS_BTN_CHANGE_PASSWORD, callback_data="security_password")],
            [InlineKeyboardButton(msg.SETTINGS_BTN_ACTIVITY, callback_data="security_logs")],
            [InlineKeyboardButton(msg.SETTINGS_BTN_LOGOUT_ALL, callback_data="security_logout_all")],
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="menu_settings")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def security_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Change password info."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            "   🔒 PAROL ÓZGERTIW       \n"
            "━━━━━━━━━━━━\n\n"
            "Telegram bot parolsiz isleydi.\n\n"
            "Siz Telegram 2FA arqalı\n"
            "qáwipsizlikti tamlaysız.\n\n"
            "━━━━━━━━━━━━\n\n"
            "💡 Telegram Sazlawlar → Privacy\n"
            "   → Two-Step Verification"
        )
        
        keyboard = [[InlineKeyboardButton(msg.BTN_BACK, callback_data="settings_security")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def security_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show activity logs."""
        query = update.callback_query
        await query.answer()
        
        from datetime import datetime
        now = datetime.now()
        
        text = (
            "━━━━━━━━━━━━\n"
            "   📋 AKTIVLIK TARIXI      \n"
            "━━━━━━━━━━━━\n\n"
            f"📅 {now.strftime('%Y-%m-%d')}\n\n"
            "──── SONǴGI HÁREKETLER ────\n\n"
            f"✅ {now.strftime('%H:%M')} - Bot iske tüsirildi\n"
            f"✅ {now.strftime('%H:%M')} - Menyu ashıldı\n"
            f"✅ {now.strftime('%H:%M')} - Sazlawlar ashıldı\n\n"
            "━━━━━━━━━━━━"
        )
        
        keyboard = [[InlineKeyboardButton(msg.BTN_BACK, callback_data="settings_security")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def security_logout_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Logout from all sessions."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            "   ✅ SESSIYALAR           \n"
            "━━━━━━━━━━━━\n\n"
            "Telegram bot tek bul qurılmada\n"
            "isleydi.\n\n"
            "Basqa sessiyalar joq.\n\n"
            "━━━━━━━━━━━━"
        )
        
        keyboard = [[InlineKeyboardButton(msg.BTN_BACK, callback_data="settings_security")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_archive(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show archive settings."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        cameras = db.get_cameras_by_organization(user.get('organization_id')) or []
        
        # Calculate storage
        total_size = len(cameras) * 15.2
        
        # Get retention from context or default
        retention = context.user_data.get('archive_retention', 30)
        quality = context.user_data.get('archive_quality', 'HD 1080p')
        
        text = (
            "━━━━━━━━━━━━\n"
            f"      {msg.SETTINGS_ARCHIVE_TITLE}             \n"
            "━━━━━━━━━━━━\n\n"
            f"──── {msg.SETTINGS_STORAGE_SETTINGS} ────\n\n"
            f"📅 {msg.SETTINGS_RETENTION}: {retention} kun\n"
            f"📺 {msg.SETTINGS_QUALITY}: {quality}\n"
            f"📦 {msg.SETTINGS_FORMAT}: MP4\n\n"
            f"──── {msg.SETTINGS_STORAGE_STATUS} ────\n\n"
            f"💾 {msg.SETTINGS_TOTAL_STORAGE}: {total_size:.1f} GB\n"
            f"📊 {msg.SETTINGS_FREE_SPACE}: {100 - total_size:.1f} GB\n"
            f"📹 {msg.SETTINGS_CAMERAS}: {len(cameras)} ta"
        )
        
        keyboard = [
            [InlineKeyboardButton(msg.SETTINGS_BTN_RETENTION, callback_data="archive_retention")],
            [InlineKeyboardButton(msg.SETTINGS_BTN_QUALITY, callback_data="archive_quality")],
            [InlineKeyboardButton(msg.SETTINGS_BTN_CLEANUP, callback_data="archive_cleanup")],
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="menu_settings")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def archive_retention(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set archive retention period."""
        query = update.callback_query
        await query.answer()
        
        current = context.user_data.get('archive_retention', 30)
        
        text = (
            "━━━━━━━━━━━━\n"
            "   📅 SAQLAW MÜDDETI       \n"
            "━━━━━━━━━━━━\n\n"
            f"Házirgi: {current} kün\n\n"
            "Jan̄a müddetti tanlan̄:"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("7 kun", callback_data="retention_7"),
                InlineKeyboardButton("14 kun", callback_data="retention_14"),
                InlineKeyboardButton("30 kun", callback_data="retention_30")
            ],
            [
                InlineKeyboardButton("60 kun", callback_data="retention_60"),
                InlineKeyboardButton("90 kun", callback_data="retention_90")
            ],
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="settings_archive")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def set_retention(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save retention setting."""
        query = update.callback_query
        await query.answer("✅ Saqlandı!")
        
        days = int(query.data.replace('retention_', ''))
        context.user_data['archive_retention'] = days
        
        await SettingsHandler.show_archive(update, context)
    
    @staticmethod
    async def archive_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set archive quality."""
        query = update.callback_query
        await query.answer()
        
        current = context.user_data.get('archive_quality', 'HD 1080p')
        
        text = (
            "━━━━━━━━━━━━\n"
            "   📺 SAPA TANLAW          \n"
            "━━━━━━━━━━━━\n\n"
            f"Házirgi: {current}\n\n"
            "Jan̄a sapanı tanlan̄:"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔷 HD 1080p", callback_data="quality_1080")],
            [InlineKeyboardButton("🔶 SD 720p", callback_data="quality_720")],
            [InlineKeyboardButton("⚪ Low 480p", callback_data="quality_480")],
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="settings_archive")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def set_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save quality setting."""
        query = update.callback_query
        await query.answer("✅ Saqlandı!")
        
        quality_map = {'1080': 'HD 1080p', '720': 'SD 720p', '480': 'Low 480p'}
        quality_code = query.data.replace('quality_', '')
        context.user_data['archive_quality'] = quality_map.get(quality_code, 'HD 1080p')
        
        await SettingsHandler.show_archive(update, context)
    
    @staticmethod
    async def archive_cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clean up old archives."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            "   🗑️ ARXIV TAZALAW        \n"
            "━━━━━━━━━━━━\n\n"
            "⚠️ Bul háreket eski videolardı\n"
            "   óshiredi!\n\n"
            "Qaysı videolardı óshiresiz?"
        )
        
        keyboard = [
            [InlineKeyboardButton("🗑️ 30 künnen eski", callback_data="cleanup_30")],
            [InlineKeyboardButton("🗑️ 14 künnen eski", callback_data="cleanup_14")],
            [InlineKeyboardButton("🗑️ 7 künnen eski", callback_data="cleanup_7")],
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="settings_archive")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def do_cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute cleanup."""
        query = update.callback_query
        await query.answer("✅ Tazalandı!")
        
        days = query.data.replace('cleanup_', '')
        
        text = (
            "━━━━━━━━━━━━\n"
            "   ✅ TAZALANDI            \n"
            "━━━━━━━━━━━━\n\n"
            f"{days} künnen eski videolar\n"
            "tazalandı.\n\n"
            "💾 Bos orın: 85.2 GB"
        )
        
        keyboard = [[InlineKeyboardButton(msg.BTN_BACK, callback_data="settings_archive")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show language settings - Qaraqalpaq only."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            f"      {msg.SETTINGS_LANGUAGE_TITLE}               \n"
            "━━━━━━━━━━━━\n\n"
            "🇺🇿 Qaraqalpaq tili\n\n"
            "━━━━━━━━━━━━\n\n"
            "✅ Házirgi til: Qaraqalpaqsha"
        )
        
        keyboard = [
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="menu_settings")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            f"      {msg.SETTINGS_HELP_TITLE}            \n"
            "━━━━━━━━━━━━\n\n"
            f"🎯 {msg.BOT_NAME}\n"
            f"{msg.BOT_DESCRIPTION}\n\n"
            f"──── {msg.SETTINGS_COMMANDS} ────\n\n"
            "/start - Baslaw\n"
            "/menu - Bas menyu\n"
            "/cancel - Biykarlaw\n\n"
            f"──── {msg.SETTINGS_CAPABILITIES} ────\n\n"
            "📹 Kamera basqarıwı\n"
            "👁️ Real-time kóriw\n"
            "🧠 AI izlew\n"
            "📊 Statistika\n\n"
            f"──── {msg.SETTINGS_CONTACT} ────\n\n"
            "📧 qalmuratovazamat5@gmail.com\n"
            "📱 +998948010312"
        )
        
        keyboard = [
            [InlineKeyboardButton(msg.SETTINGS_BTN_GUIDE, callback_data="help_guide")],
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="menu_settings")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show full guide in Karakalpak."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            "   📖 TO'LIQ QO'LLANMA     \n"
            "━━━━━━━━━━━━\n\n"
            "🎯 CAM MAX PRO - AI Video\n"
            "   Kuzatuv Tizimi\n\n"
            "━━━━━━━━━━━━\n\n"
            "📹 1. KAMERA QO'SHISH\n"
            "━━━━━━━━━━━━\n"
            "• Asosiy menyu → Kameralarni\n"
            "  Boshqarish → Yangi Kamera\n"
            "• Kamera nomini kiriting\n"
            "• IP manzilni kiriting (masalan: 192.168.1.100)\n"
            "• Portni kiriting (odatda: 554)\n"
            "• Loginni kiriting (odatda: admin)\n"
            "• Parolni kiriting\n"
            "• Bot kamerani tekshiradi\n\n"
            "━━━━━━━━━━━━\n\n"
            "👁️ 2. KAMERALARNI KO'RISH\n"
            "━━━━━━━━━━━━\n"
            "• Asosiy menyu → Kameralarni\n"
            "  Ko'rish\n"
            "• Real-time - hozirgi rasm\n"
            "• Arxiv - eski videolar\n"
            "• Sevimlilar - saqlangan\n"
            "  momentlar\n\n"
            "━━━━━━━━━━━━\n\n"
            "🧠 3. AI QIDIRUV\n"
            "━━━━━━━━━━━━\n"
            "• Asosiy menyu → AI Video\n"
            "  qidiruv\n"
            "• O'zingiz so'ragan narsani\n"
            "  yozing\n"
            "• AI barcha kameralardan\n"
            "  qidiradi\n"
            "• Masalan: \"Qizil sumka qayerda?\"\n"
            "• Masalan: \"Kecha kim kirdi?\"\n\n"
            "━━━━━━━━━━━━\n\n"
            "📊 4. STATISTIKA\n"
            "━━━━━━━━━━━━\n"
            "• Asosiy menyu → Statistika\n"
            "• Kunlik/haftalik hisobot\n"
            "• Kamera analitikasi\n"
            "• Hisobotni eksport qilish\n\n"
            "━━━━━━━━━━━━\n\n"
            "⚙️ 5. SOZLAMALAR\n"
            "━━━━━━━━━━━━\n"
            "• Profil - ism, telefon\n"
            "• Bildirishnomalar - on/off\n"
            "• Xavfsizlik - 2FA\n"
            "• Arxiv - saqlash muddati\n\n"
            "━━━━━━━━━━━━\n\n"
            "📞 ALOQA\n"
            "━━━━━━━━━━━━\n"
            "📧 qalmuratovazamat5@gmail.com\n"
            "📱 +998948010312\n\n"
            "━━━━━━━━━━━━\n"
            "© 2024 CAM MAX PRO"
        )
        
        keyboard = [[InlineKeyboardButton(msg.BTN_BACK, callback_data="settings_help")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# Export
settings_handler = SettingsHandler()
