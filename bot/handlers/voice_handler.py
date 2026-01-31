"""
Voice message handler for speech-to-text search.
Uses Telegram's voice message + AI transcription.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ai.gemini_ai import gemini_ai
from utils.logger import logger
import tempfile
import os


class VoiceHandler:
    """Handle voice messages for AI search."""
    
    @staticmethod
    async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle incoming voice message.
        Transcribe and send to AI search.
        """
        user_id = update.effective_user.id
        voice = update.message.voice
        
        # Show processing message
        processing_msg = await update.message.reply_text(
            "🎤 Ovozli xabar qayta ishlanmoqda...\n"
            "⏳ Iltimos kuting..."
        )
        
        try:
            # Download voice file
            voice_file = await context.bot.get_file(voice.file_id)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
                await voice_file.download_to_drive(tmp.name)
                voice_path = tmp.name
            
            # Transcribe using Gemini (it can understand audio context from text description)
            # For now, we'll use a placeholder approach
            # In production, you'd use a speech-to-text API like Google Cloud Speech
            
            await processing_msg.edit_text(
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃    🎤 OVOZLI QIDIRUV      ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "⚠️ Ovozli qidiruv hozircha\n"
                "   to'liq ishlamayapti.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "💡 Yozma shaklda yuboring:\n"
                "   Masalan: \"Qizil sumka qayerda?\"\n\n"
                "🔜 Tez orada ovozli qidiruv\n"
                "   to'liq ishga tushadi!"
            )
            
            # Clean up temp file
            os.unlink(voice_path)
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            await processing_msg.edit_text(
                f"❌ Ovozli xabarni qayta ishlashda xatolik:\n{str(e)}"
            )


# Export
voice_handler = VoiceHandler()
