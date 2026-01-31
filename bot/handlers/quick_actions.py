"""
Quick Actions handler for fast access to common operations.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.models import db
from datetime import datetime
from utils.logger import logger


class QuickActionsHandler:
    """Handle quick actions for fast operations."""
    
    @staticmethod
    async def show_quick_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show quick actions menu."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        cameras = db.get_cameras_by_organization(user.get('organization_id')) or []
        
        text = (
            "━━━━━━━━━━━━\n"
            "     ⚡ TEZKOR HARAKATLAR   \n"
            "━━━━━━━━━━━━\n\n"
        )
        
        keyboard = []
        
        # Recent cameras
        if cameras:
            text += "📹 Oxirgi kameralar:\n\n"
            for cam in cameras[:3]:
                status_icon = "🟢" if cam.get('status') == 'active' else "🔴"
                keyboard.append([
                    InlineKeyboardButton(
                        f"{status_icon} {cam['name']} - 📸 Rasm",
                        callback_data=f"realtime_{cam['id']}"
                    )
                ])
        
        text += "\n──── TEZKOR VAQT ────\n\n"
        
        # Quick time buttons
        keyboard.append([
            InlineKeyboardButton("⏱️ 10 min", callback_data="archive_10min"),
            InlineKeyboardButton("⏰ 1 soat", callback_data="archive_1hour")
        ])
        keyboard.append([
            InlineKeyboardButton("📆 Bugun", callback_data="archive_today"),
            InlineKeyboardButton("📆 Kecha", callback_data="archive_yesterday")
        ])
        
        text += "\n──── TEZKOR AI ────\n\n"
        
        # Quick AI searches
        keyboard.append([
            InlineKeyboardButton("🧠 \"Kim kirdi?\"", callback_data="quick_ai_kirdi"),
            InlineKeyboardButton("🧠 \"Nima bor?\"", callback_data="quick_ai_nima")
        ])
        
        keyboard.append([InlineKeyboardButton("« Bas Menyu", callback_data="menu_main")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def quick_ai_kirdi(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick AI search: Who entered?"""
        query = update.callback_query
        await query.answer()
        
        # Simulate the query
        context.user_data['quick_query'] = "Bugun kim kirdi?"
        
        from bot.handlers.ai_search import AISearchHandler
        
        # Create a fake message with the query
        text = (
            "━━━━━━━━━━━━\n"
            "    🧠 TEZKOR QIDIRUV      \n"
            "━━━━━━━━━━━━\n\n"
            "🔍 So'rov: \"Bugun kim kirdi?\"\n\n"
            "━━━━━━━━━━━━\n\n"
            "💬 AI qidiruv menyusiga o'ting va\n"
            "   so'rovingizni to'liq kiriting."
        )
        
        keyboard = [
            [InlineKeyboardButton("🧠 AI Qidiruv", callback_data="menu_ai")],
            [InlineKeyboardButton("« Orqaga", callback_data="quick_actions")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def quick_ai_nima(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick AI search: What's there?"""
        query = update.callback_query
        await query.answer()
        
        text = (
            "━━━━━━━━━━━━\n"
            "    🧠 TEZKOR QIDIRUV      \n"
            "━━━━━━━━━━━━\n\n"
            "🔍 So'rov: \"Hozir kameralarda nima bor?\"\n\n"
            "━━━━━━━━━━━━\n\n"
            "💬 AI qidiruv menyusiga o'ting va\n"
            "   so'rovingizni to'liq kiriting."
        )
        
        keyboard = [
            [InlineKeyboardButton("🧠 AI Qidiruv", callback_data="menu_ai")],
            [InlineKeyboardButton("« Orqaga", callback_data="quick_actions")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# Export
quick_actions_handler = QuickActionsHandler()
