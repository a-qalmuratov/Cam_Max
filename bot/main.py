"""Main Telegram bot application - Premium Version with AI."""
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
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
from bot.handlers.video_view import VideoViewHandler
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

# Import utilities
from camera.stream_manager import stream_manager


def main():
    """Start the bot."""
    logger.info("🚀 Starting Cam_Max Bot (Premium AI Version)...")
    
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
            CommandHandler('cancel', AISearchHandler.cancel_search)
        ],
        per_message=False
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
        VideoViewHandler.extract_archive_video,
        pattern='^archive_cam_\\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        VideoViewHandler.show_bookmarks,
        pattern='^view_bookmarks$'
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
        pattern='^ai_view_video$'
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
    
    # =====================================================
    # MAIN MENU NAVIGATION (must be last - catches all menu_ patterns)
    # =====================================================
    application.add_handler(CallbackQueryHandler(
        MainMenuHandler.handle_menu_callback,
        pattern='^menu_'
    ))
    
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
