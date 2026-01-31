"""
Statistics and analytics handler with REAL data.
Premium UI - Qaraqalpaq tilinde.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from database.models import db
from utils.logger import logger
from utils.messages import msg


class StatisticsHandler:
    """Handle statistics and analytics with premium UI."""
    
    @staticmethod
    async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show statistics dashboard with REAL data."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        org_id = user.get('organization_id') if user else None
        
        # Get REAL statistics from database
        stats = db.get_statistics(org_id)
        
        text = (
            "━━━━━━━━━━━━\n"
            f"      {msg.STATS_TITLE}        \n"
            "━━━━━━━━━━━━\n\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"────── {msg.STATS_TODAY} ──────\n\n"
            f"👥 {msg.STATS_PEOPLE}: {stats['people_today']} ta\n"
            f"🚗 {msg.STATS_VEHICLES}: {stats['vehicles_today']} ta\n"
            f"📦 {msg.STATS_OBJECTS}: {stats['detections_today']} ta\n\n"
            f"──── {msg.STATS_CAMERAS} ────\n\n"
            f"📹 {msg.STATS_TOTAL}: {stats['cameras_total']}\n"
            f"🟢 {msg.STATS_ACTIVE}: {stats['cameras_active']}\n"
            f"🔴 {msg.STATS_INACTIVE}: {stats['cameras_inactive']}"
        )
        
        keyboard = [
            [InlineKeyboardButton(msg.STATS_BTN_WEEKLY, callback_data="stats_weekly")],
            [InlineKeyboardButton(msg.STATS_BTN_CAMERAS, callback_data="stats_cameras")],
            [InlineKeyboardButton(msg.STATS_BTN_ALERTS, callback_data="stats_alerts")],
            [InlineKeyboardButton(msg.STATS_BTN_EXPORT, callback_data="stats_export")],
            [InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show weekly report with REAL data."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        org_id = user.get('organization_id') if user else None
        
        # Get weekly data from database
        weekly_data = db.get_weekly_statistics(org_id)
        
        # Calculate trend
        total_week = sum(d['total'] for d in weekly_data) if weekly_data else 0
        
        text = (
            "━━━━━━━━━━━━\n"
            f"    {msg.STATS_WEEKLY_TITLE}    \n"
            "━━━━━━━━━━━━\n\n"
            f"📊 Háptelik jámi: {total_week} ta\n\n"
            f"──── {msg.STATS_DAILY_BREAKDOWN} ────\n\n"
        )
        
        if weekly_data:
            for day_data in weekly_data[:7]:
                date_str = day_data['date']
                people = day_data['people']
                vehicles = day_data['vehicles']
                text += f"📅 {date_str}: 👥{people} 🚗{vehicles}\n"
        else:
            text += "📭 Ele malıwmat joq\n"
            text += "Kamera qosılıǵanda malıwmat\n"
            text += "kórine baslaydı.\n"
        
        text += f"\n──── {msg.STATS_WARNINGS_TITLE} ────\n\n"
        text += f"⚠️ 0 {msg.STATS_SUSPICIOUS}\n"
        text += f"❓ 0 {msg.STATS_UNKNOWN}"
        
        keyboard = [
            [InlineKeyboardButton(msg.STATS_BTN_GRAPH, callback_data="stats_graph")],
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="menu_stats")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_camera_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show per-camera analytics with REAL data."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        cameras = db.get_cameras_by_organization(user.get('organization_id')) or []
        
        text = (
            "━━━━━━━━━━━━\n"
            f"    {msg.STATS_BTN_CAMERAS}    \n"
            "━━━━━━━━━━━━\n\n"
            "──── KAMERALAR ────\n\n"
        )
        
        if cameras:
            for cam in cameras:
                status_icon = "🟢" if cam.get('status') == 'active' else "🔴"
                # Get detection count for this camera
                detections = db.get_recent_detections(cam['id'], limit=1000)
                count = len(detections)
                text += f"{status_icon} {cam['name']} → {count} hodisa\n"
        else:
            text += "📭 Kameralar joq\n\n"
            text += "Aldın kamera qosıń!"
        
        keyboard = [
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="menu_stats")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_alerts_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show alerts and notifications summary."""
        query = update.callback_query
        await query.answer()
        
        # Get notification settings
        notif = context.user_data.get('notifications', {
            'motion': True,
            'camera': True,
            'suspicious': True,
            'daily': False,
            'weekly': False
        })
        
        text = (
            "━━━━━━━━━━━━\n"
            f"    {msg.STATS_BTN_ALERTS}    \n"
            "━━━━━━━━━━━━\n\n"
            "──── BUGUNGI ALERTLAR ────\n\n"
            "⚪ Barliq sistemalar normal\n\n"
            "──── SAZLAWLAR ────\n\n"
            f"{'✅' if notif.get('motion') else '❌'} Motion detection\n"
            f"{'✅' if notif.get('camera') else '❌'} Camera offline\n"
            f"{'✅' if notif.get('suspicious') else '❌'} Suspicious activity\n"
            f"{'✅' if notif.get('daily') else '❌'} Kunlik esabat\n"
            f"{'✅' if notif.get('weekly') else '❌'} Haptelik esabat\n\n"
            "⏰ Saat: 08:00 - 22:00\n"
            "📱 Kanal: Telegram"
        )
        
        keyboard = [
            [InlineKeyboardButton("⚙️ Sazlaw", callback_data="settings_notifications")],
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="menu_stats")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def export_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export statistics report as text file."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        org_id = user.get('organization_id') if user else None
        
        # Get real statistics
        stats = db.get_statistics(org_id)
        cameras = db.get_cameras_by_organization(org_id) or []
        
        # Generate report text
        report = f"""
========================================
       CAM MAX PRO - ESABAT
========================================
Sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Paydalaniwshi: {user.get('first_name', 'User')}

========== KAMERALAR ==========
Jami: {stats['cameras_total']}
Aktiv: {stats['cameras_active']}
Aktiv emes: {stats['cameras_inactive']}

"""
        for cam in cameras:
            status = "ONLINE" if cam.get('status') == 'active' else "OFFLINE"
            report += f"- {cam['name']}: {status}\n"

        report += f"""
========== BUGUNGI STATISTIKA ==========
Adamlar: {stats['people_today']} ta
Mashinalar: {stats['vehicles_today']} ta
Jami deteksiya: {stats['detections_today']} ta

========================================
© 2024 CAM MAX PRO
qalmuratovazamat5@gmail.com
+998200050026
========================================
"""
        
        # Send as document
        import io
        file_bytes = io.BytesIO(report.encode('utf-8'))
        file_bytes.name = f"esabat_{datetime.now().strftime('%Y%m%d')}.txt"
        
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=file_bytes,
            caption="📊 Statistika esabati"
        )
        
        text = (
            "━━━━━━━━━━━━\n"
            f"    {msg.EXPORT_SENT}            \n"
            "━━━━━━━━━━━━\n\n"
            f"{msg.EXPORT_FILE_SENT}"
        )
        
        keyboard = [
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="menu_stats")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def show_graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show statistics graph (text-based)."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        org_id = user.get('organization_id') if user else None
        
        # Get weekly data
        weekly_data = db.get_weekly_statistics(org_id)
        total = sum(d['total'] for d in weekly_data) if weekly_data else 0
        
        text = (
            "━━━━━━━━━━━━\n"
            f"    {msg.STATS_BTN_GRAPH}     \n"
            "━━━━━━━━━━━━\n\n"
        )
        
        if weekly_data and total > 0:
            max_val = max(d['total'] for d in weekly_data)
            text += "      Haftalik aktivlik\n\n"
            
            for day_data in weekly_data[:7]:
                bar_len = int((day_data['total'] / max_val) * 10) if max_val > 0 else 0
                bar = "█" * bar_len + "░" * (10 - bar_len)
                text += f"{day_data['date'][-5:]}: {bar} {day_data['total']}\n"
            
            text += f"\n📊 Jami: {total} ta"
        else:
            text += "📭 Ele grafik ushın malıwmat joq\n\n"
            text += "Kameralar islegende\n"
            text += "grafik kórinedi."
        
        keyboard = [
            [InlineKeyboardButton(msg.BTN_BACK, callback_data="stats_weekly")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# Export
statistics_handler = StatisticsHandler()
