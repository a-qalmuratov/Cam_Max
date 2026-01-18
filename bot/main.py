"""Main Telegram bot application - Premium Version with AI."""
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from utils.config import BOT_TOKEN
from utils.logger import logger

# Import handlers
from bot.handlers.registration import (
    RegistrationHandler,
    REGISTRATION_NAME,
    REGISTRATION_PHONE,
    VERIFICATION_CODE
)
from bot.handlers.main_menu import MainMenuHandler
from bot.handlers.camera_management import (
    CameraManagementHandler,
    CAM_NAME,
    CAM_IP,
    CAM_PORT,
    CAM_USERNAME,
    CAM_PASSWORD
)
from bot.handlers.video_view import VideoViewHandler, TIME_RANGE_INPUT
from bot.handlers.ai_search import (
    AISearchHandler,
    AI_QUERY_INPUT,
    AI_CLARIFICATION
)
from bot.handlers.statistics import StatisticsHandler
from bot.handlers.settings import SettingsHandler, EDIT_NAME, EDIT_PHONE
from bot.handlers.quick_actions import QuickActionsHandler
from bot.handlers.export_handler import ExportHandler
from bot.handlers.voice_handler import VoiceHandler
from bot.handlers.analytics import AnalyticsHandler

# Import utilities
from camera.stream_manager import stream_manager


def main():
    """Start the bot."""
    logger.info("🚀 Starting Cam_Max Bot (Premium AI Version)...")
    
    # Check BOT_TOKEN before starting
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found! Create .env file from .env.example")
        raise ValueError("BOT_TOKEN is required to start the bot")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # =====================================================
    # REGISTRATION CONVERSATION HANDLER
    # =====================================================
    registration_conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', RegistrationHandler.start_registration)
        ],
        states={
            REGISTRATION_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, RegistrationHandler.get_name)
            ],
            REGISTRATION_PHONE: [
                MessageHandler((filters.TEXT | filters.CONTACT) & ~filters.COMMAND, RegistrationHandler.get_phone)
            ],
            VERIFICATION_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, RegistrationHandler.verify_code)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', RegistrationHandler.cancel_registration)
        ]
    )
    
    # =====================================================
    # CAMERA WIZARD CONVERSATION HANDLER
    # =====================================================
    camera_wizard_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(CameraManagementHandler.start_add_camera, pattern='^cam_add$')
        ],
        states={
            CAM_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, CameraManagementHandler.get_camera_name)
            ],
            CAM_IP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, CameraManagementHandler.get_camera_ip)
            ],
            CAM_PORT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, CameraManagementHandler.get_camera_port)
            ],
            CAM_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, CameraManagementHandler.get_camera_username)
            ],
            CAM_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, CameraManagementHandler.get_camera_password)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', CameraManagementHandler.cancel_wizard)
        ]
    )
    
    # =====================================================
    # AI SEARCH CONVERSATION HANDLER
    # =====================================================
    
    # Global cancel handler for conversations
    async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel any conversation and return to main menu."""
        user_id = update.effective_user.id
        context.user_data.clear()
        await update.message.reply_text(
            "❌ Biykarlandy.\n\n/menu - Bas menyu"
        )
        return ConversationHandler.END
    
    ai_search_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(AISearchHandler.show_search_menu, pattern='^menu_ai$')
        ],
        states={
            AI_QUERY_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, AISearchHandler.handle_query)
            ],
            AI_CLARIFICATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, AISearchHandler.handle_clarification)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_conversation),
            CommandHandler('start', cancel_conversation),
            CommandHandler('menu', cancel_conversation)
        ],
        per_message=False,
        conversation_timeout=300  # 5 minutes timeout
    )
    
    # =====================================================
    # ARCHIVE CUSTOM TIME CONVERSATION HANDLER
    # =====================================================
    archive_custom_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(VideoViewHandler.show_custom_time_input, pattern='^archive_custom$')
        ],
        states={
            TIME_RANGE_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, VideoViewHandler.handle_custom_time_input)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_conversation),
            CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern='^view_archive$')
        ],
        per_message=False,
        conversation_timeout=300
    )
    
    # =====================================================
    # PROFILE EDIT CONVERSATION HANDLER
    # =====================================================
    profile_name_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(SettingsHandler.start_edit_name, pattern='^profile_edit_name$')
        ],
        states={
            EDIT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, SettingsHandler.save_name)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', SettingsHandler.cancel_edit)
        ]
    )
    
    profile_phone_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(SettingsHandler.start_edit_phone, pattern='^profile_edit_phone$')
        ],
        states={
            EDIT_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, SettingsHandler.save_phone)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', SettingsHandler.cancel_edit)
        ]
    )
    
    # =====================================================
    # ADD HANDLERS (Order matters!)
    # =====================================================
    
    # Conversation handlers first
    application.add_handler(registration_conv)
    application.add_handler(camera_wizard_conv)
    application.add_handler(ai_search_conv)
    application.add_handler(archive_custom_conv)
    application.add_handler(profile_name_conv)
    application.add_handler(profile_phone_conv)
    
    # Voice message handler
    application.add_handler(MessageHandler(filters.VOICE, VoiceHandler.handle_voice))
    
    # Command handlers
    application.add_handler(CommandHandler('menu', MainMenuHandler.show_main_menu))
    
    # =====================================================
    # VIDEO VIEW CALLBACKS
    # =====================================================
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.show_realtime_cameras,
        pattern='^view_realtime$'
    ))
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.capture_realtime,
        pattern='^realtime_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.show_archive_time_selection,
        pattern='^view_archive$'
    ))
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.handle_quick_time,
        pattern='^archive_(10min|1hour|today|yesterday)$'
    ))
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.show_custom_time_input,
        pattern='^archive_custom$'
    ))
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.extract_archive_video,
        pattern='^archive_cam_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.show_bookmarks,
        pattern='^view_bookmarks$'
    ))
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.save_bookmark,
        pattern='^bookmark_save_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.view_bookmark,
        pattern='^bookmark_view_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.delete_bookmark,
        pattern='^bookmark_delete_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.show_download_menu,
        pattern='^view_download$'
    ))
    
    # =====================================================
    # AI SEARCH RESULT CALLBACKS
    # =====================================================
    application.add_handler(CallbackQueryHandler(
        AISearchHandler.view_video,
        pattern='^ai_view_video(_\\d+)?$'
    ))
    
    # =====================================================
    # QUICK ACTIONS CALLBACKS
    # =====================================================
    application.add_handler(CallbackQueryHandler(
        QuickActionsHandler.show_quick_actions,
        pattern='^quick_actions$'
    ))
    application.add_handler(CallbackQueryHandler(
        QuickActionsHandler.quick_ai_kirdi,
        pattern='^quick_ai_kirdi$'
    ))
    application.add_handler(CallbackQueryHandler(
        QuickActionsHandler.quick_ai_nima,
        pattern='^quick_ai_nima$'
    ))
    
    # =====================================================
    # EXPORT CALLBACKS
    # =====================================================
    application.add_handler(CallbackQueryHandler(
        ExportHandler.show_export_menu,
        pattern='^export_menu$'
    ))
    application.add_handler(CallbackQueryHandler(
        ExportHandler.export_video_options,
        pattern='^export_video$'
    ))
    application.add_handler(CallbackQueryHandler(
        ExportHandler.export_format_selected,
        pattern='^export_format_(mp4|avi)$'
    ))
    application.add_handler(CallbackQueryHandler(
        ExportHandler.export_quality_selected,
        pattern='^export_quality_(1080|720|480)$'
    ))
    application.add_handler(CallbackQueryHandler(
        ExportHandler.export_stats,
        pattern='^export_stats$'
    ))
    application.add_handler(CallbackQueryHandler(
        ExportHandler.export_events,
        pattern='^export_events$'
    ))
    
    # =====================================================
    # STATISTICS CALLBACKS
    # =====================================================
    application.add_handler(CallbackQueryHandler(
        StatisticsHandler.show_weekly_report,
        pattern='^stats_weekly$'
    ))
    application.add_handler(CallbackQueryHandler(
        StatisticsHandler.show_camera_analytics,
        pattern='^stats_cameras$'
    ))
    application.add_handler(CallbackQueryHandler(
        StatisticsHandler.show_alerts_summary,
        pattern='^stats_alerts$'
    ))
    application.add_handler(CallbackQueryHandler(
        StatisticsHandler.export_report,
        pattern='^stats_export$'
    ))
    application.add_handler(CallbackQueryHandler(
        StatisticsHandler.show_graph,
        pattern='^stats_graph$'
    ))
    
    # =====================================================
    # ANALYTICS CALLBACKS (from analytics.py)
    # =====================================================
    application.add_handler(CallbackQueryHandler(
        AnalyticsHandler.show_detection_stats,
        pattern='^stats_detections$'
    ))
    application.add_handler(CallbackQueryHandler(
        AnalyticsHandler.show_storage_stats,
        pattern='^stats_storage$'
    ))
    application.add_handler(CallbackQueryHandler(
        AnalyticsHandler.show_activity_graph,
        pattern='^stats_activity$'
    ))
    application.add_handler(CallbackQueryHandler(
        AnalyticsHandler.show_dashboard,
        pattern='^menu_analytics$'
    ))
    
    # =====================================================
    # SETTINGS CALLBACKS
    # =====================================================
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.show_profile,
        pattern='^settings_profile$'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.show_notifications,
        pattern='^settings_notifications$'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.show_security,
        pattern='^settings_security$'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.show_archive,
        pattern='^settings_archive$'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.show_language,
        pattern='^settings_language$'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.show_help,
        pattern='^settings_help$'
    ))
    
    # Notification toggle callbacks
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.toggle_notification,
        pattern='^notif_toggle_'
    ))
    
    # Security callbacks
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.security_password,
        pattern='^security_password$'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.security_logs,
        pattern='^security_logs$'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.security_logout_all,
        pattern='^security_logout_all$'
    ))
    
    # Archive callbacks
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.archive_retention,
        pattern='^archive_retention$'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.set_retention,
        pattern='^retention_'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.archive_quality,
        pattern='^archive_quality$'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.set_quality,
        pattern='^quality_'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.archive_cleanup,
        pattern='^archive_cleanup$'
    ))
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.do_cleanup,
        pattern='^cleanup_'
    ))
    
    # Help guide callback
    application.add_handler(CallbackQueryHandler(
        SettingsHandler.show_guide,
        pattern='^help_guide$'
    ))
    
    # =====================================================
    # CAMERA MANAGEMENT CALLBACKS
    # =====================================================
    application.add_handler(CallbackQueryHandler(
        CameraManagementHandler.show_camera_detail,
        pattern='^cam_detail_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        CameraManagementHandler.toggle_camera_on,
        pattern='^cam_on_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        CameraManagementHandler.toggle_camera_off,
        pattern='^cam_off_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        CameraManagementHandler.confirm_delete_camera,
        pattern='^cam_delete_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        CameraManagementHandler.delete_camera,
        pattern='^cam_delete_confirm_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        CameraManagementHandler.capture_realtime,
        pattern='^cam_snapshot_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        CameraManagementHandler.open_camera_archive,
        pattern='^cam_archive_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        CameraManagementHandler.open_camera_settings,
        pattern='^cam_settings_\\d+$'
    ))
    
    # =====================================================
    # MAIN MENU NAVIGATION (must be last - catches all menu_ patterns)
    # =====================================================
    application.add_handler(CallbackQueryHandler(
        MainMenuHandler.handle_menu_callback,
        pattern='^menu_'
    ))
    
    # =====================================================
    # UNKNOWN CALLBACK FALLBACK (must be last!)
    # =====================================================
    async def handle_unknown_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any unmatched callback queries with detailed logging."""
        query = update.callback_query
        await query.answer("⚠️ Noma'lum tugma")
        
        # DETAILED LOGGING for debugging
        user_id = update.effective_user.id
        callback_data = query.data
        
        # Get user org for logging
        try:
            from database.models import db
            user = db.get_user(user_id)
            org_id = user.get('organization_id') if user else 'N/A'
        except:
            org_id = 'ERROR'
        
        # Get current state info
        current_state = context.user_data.get('state', 'UNKNOWN')
        
        logger.warning(
            f"UNKNOWN CALLBACK | "
            f"user_id={user_id} | "
            f"org_id={org_id} | "
            f"callback='{callback_data}' | "
            f"state={current_state}"
        )
        
        # Try to show main menu with helpful message
        text = (
            "⚠️ Bu tugma hozirda ishlamaydi.\n\n"
            f"Callback: {callback_data[:30]}...\n\n"
            "Bas menyuga qaytin."
        )
        keyboard = [[InlineKeyboardButton("🏠 Bas Menyu", callback_data="menu_main")]]
        
        try:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass
    
    application.add_handler(CallbackQueryHandler(handle_unknown_callback))
    
    # =====================================================
    # STARTUP
    # =====================================================
    
    # Load existing cameras
    try:
        stream_manager.load_cameras_from_db()
        logger.info("✅ Cameras loaded from database")
    except Exception as e:
        logger.warning(f"Could not load cameras: {e}")
    
    # Start bot
    logger.info("✅ Bot started successfully!")
    logger.info("📱 Telegram'da /start buyrug'ini yuboring")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        stream_manager.cleanup()
        logger.info("Bot shutdown complete")
