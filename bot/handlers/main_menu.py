"""
Main menu system with premium inline keyboard UI.
Uses central language file for all texts.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.models import db
from utils.logger import logger
from utils.messages import msg


class MainMenuHandler:
    """Handle main menu navigation with premium UI."""
    
    @staticmethod
    async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu with inline keyboard."""
        user_id = update.effective_user.id
        
        # Get user from database
        user = db.get_user(user_id)
        if not user:
            text = (
                "❌ Siz ro'yxatdan o'tmagansiz!\n\n"
                "Ro'yxatdan o'tish: /start"
            )
            if update.message:
                await update.message.reply_text(text)
            elif update.callback_query:
                await update.callback_query.edit_message_text(text)
            return
        
        # Get camera count for user
        cameras = db.get_cameras_by_organization(user.get('organization_id', 0))
        camera_count = len(cameras) if cameras else 0
        active_cameras = sum(1 for c in cameras if c.get('status') == 'active') if cameras else 0
        
        # Build menu keyboard
        keyboard = [
            [InlineKeyboardButton(msg.MENU_BTN_CAMERAS, callback_data="menu_cameras")],
            [InlineKeyboardButton(msg.MENU_BTN_VIEW, callback_data="menu_view")],
            [InlineKeyboardButton(msg.MENU_BTN_AI, callback_data="menu_ai")],
            [InlineKeyboardButton(msg.MENU_BTN_STATS, callback_data="menu_stats")],
            [InlineKeyboardButton(msg.MENU_BTN_SETTINGS, callback_data="menu_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Build menu text
        menu_text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃       {msg.MENU_TITLE}      ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"👤 {user.get('first_name', 'User')}\n"
            f"📱 {user.get('phone_number', 'N/A')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📹 {msg.MENU_CAMERAS_COUNT}: {active_cameras}/{camera_count}\n"
            f"💾 Status: {msg.STATUS_ACTIVE}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⬇️ {msg.MENU_SELECT_ACTION}"
        )
        
        # Send or edit message
        if update.message:
            await update.message.reply_text(menu_text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
    
    @staticmethod
    async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle menu button callbacks."""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        try:
            if callback_data == "menu_main":
                await MainMenuHandler.show_main_menu(update, context)
            
            elif callback_data == "menu_cameras":
                from bot.handlers.camera_management import CameraManagementHandler
                await CameraManagementHandler.show_camera_list(update, context)
            
            elif callback_data == "menu_view":
                from bot.handlers.video_view import VideoViewHandler
                await VideoViewHandler.show_view_menu(update, context)
            
            elif callback_data == "menu_ai":
                from bot.handlers.ai_search import AISearchHandler
                await AISearchHandler.show_search_menu(update, context)
            
            elif callback_data == "menu_stats":
                from bot.handlers.statistics import StatisticsHandler
                await StatisticsHandler.show_stats(update, context)
            
            elif callback_data == "menu_settings":
                from bot.handlers.settings import SettingsHandler
                await SettingsHandler.show_settings(update, context)
            
            else:
                logger.warning(f"Unknown callback: {callback_data}")
                await query.edit_message_text(f"{msg.ERROR_GENERAL}")
                
        except Exception as e:
            logger.error(f"Menu callback error: {e}")
            keyboard = [[InlineKeyboardButton(msg.BTN_MAIN_MENU, callback_data="menu_main")]]
            await query.edit_message_text(
                f"{msg.ERROR_GENERAL}\n\n{str(e)}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )


# Export handler instance
main_menu_handler = MainMenuHandler()
