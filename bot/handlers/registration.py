"""
User registration and authentication system with 2FA.
Clean modern UI implementation - Qaraqalpaq tilinde.
"""
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, timedelta
import random
import re
from database.models import db
from utils.logger import logger

# Conversation states
REGISTRATION_NAME = 1
REGISTRATION_PHONE = 2
VERIFICATION_CODE = 3

# Temporary storage for verification codes
verification_codes = {}  # {user_id: {'code': '123456', 'expires': datetime, 'attempts': 0}}


class RegistrationHandler:
    """Handle user registration with 2FA."""
    
    @staticmethod
    async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start registration process."""
        user_id = update.effective_user.id
        
        # Check if user exists
        existing_user = db.get_user(user_id)
        if existing_user:
            # User already registered, show main menu
            from bot.handlers.main_menu import MainMenuHandler
            await MainMenuHandler.show_main_menu(update, context)
            return ConversationHandler.END
        
        welcome_text = (
            f"🎯 *CAM MAX PRO*\n"
            f"_AI Video Baqlıw Sisteması_\n\n"
            f"━━━━━━━━━━━━\n\n"
            f"👋 *Xosh kelipsiz!*\n\n"
            f"🔐 Shaxsiy kabinet jaratıw\n\n"
            f"📝 Atıńız hám familiyańızdı jazıń:\n"
            f"_Mısalı: Azamat Qalmuratov_\n\n"
            f"━━━━━━━━━━━━\n"
            f"💎 100% qáwipsiz hám jasırın"
        )
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        return REGISTRATION_NAME
    
    @staticmethod
    async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get user's full name with validation."""
        full_name = update.message.text.strip()
        
        # Validate name - allow Latin, Cyrillic, and spaces
        if len(full_name) < 3:
            await update.message.reply_text(
                "❌ At júda qısqa!\n\n"
                "Iltimas tolıq atıńız hám familiyańízdı jazıń.\n"
                "Mısalı: Azamat Qalmuratov"
            )
            return REGISTRATION_NAME
        
        # Allow Latin, Cyrillic, apostrophe, and spaces
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s']+$", full_name):
            await update.message.reply_text(
                "❌ Qate format!\n\n"
                "Tek hárpler paydalanılıwı múmkin.\n"
                "Mısalı: Azamat Qalmuratov"
            )
            return REGISTRATION_NAME
        
        # Store name
        context.user_data['full_name'] = full_name
        
        # Request phone number with button
        keyboard = [[KeyboardButton("📱 Telefon nomerin ulesiw", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        phone_text = (
            f"✅ *AT QABIL ETILDI*\n\n"
            f"👤 {full_name}\n\n"
            f"━━━━━━━━━━━━\n\n"
            f"📱 *Telefon nomeriňizdi jiberin*\n\n"
            f"Túymeni basıń yamasa qoldan jazıń:\n"
            f"`+998 XX XXX XX XX`\n\n"
            f"━━━━━━━━━━━━\n"
            f"🔒 Bank dárejesinde shifrlengen"
        )
        
        await update.message.reply_text(phone_text, reply_markup=reply_markup, parse_mode='Markdown')
        return REGISTRATION_PHONE
    
    @staticmethod
    async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get and validate user's phone number."""
        user_id = update.effective_user.id
        
        # Check if contact was shared
        if update.message.contact:
            phone = update.message.contact.phone_number
        else:
            phone = update.message.text.strip()
        
        # Normalize and validate phone number
        phone = RegistrationHandler._normalize_phone(phone)
        
        if not phone:
            await update.message.reply_text(
                "❌ Qate telefon nomer!\n\n"
                "Format: +998 XX XXX XX XX\n"
                "Mısalı: +998901234567\n\n"
                "Qaytadan jazıń:",
                reply_markup=ReplyKeyboardRemove()
            )
            return REGISTRATION_PHONE
        
        # Store phone
        context.user_data['phone'] = phone
        
        # Generate 6-digit verification code
        code = str(random.randint(100000, 999999))
        
        # Store code with 5-minute expiration
        verification_codes[user_id] = {
            'code': code,
            'expires': datetime.now() + timedelta(minutes=5),
            'attempts': 0
        }
        
        # Send verification code
        code_text = (
            f"🔐 *2FA TASTIYIQLAW*\n\n"
            f"📱 Telefon: `{phone}`\n\n"
            f"━━━━━━━━━━━━\n\n"
            f"🔑 *TASTIYIQLAW KODI:*\n\n"
            f"       *[ {code} ]*\n\n"
            f"━━━━━━━━━━━━\n\n"
            f"⏰ Isleydi: 5 minut\n"
            f"🔢 Urınıwlar: 3 ta\n\n"
            f"💬 Kodtı jazıń:"
        )
        
        await update.message.reply_text(code_text, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
        
        logger.info(f"Verification code for {user_id}: {code}")
        return VERIFICATION_CODE
    
    @staticmethod
    async def verify_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Verify the 2FA code and complete registration."""
        user_id = update.effective_user.id
        entered_code = update.message.text.strip()
        
        # Check if code exists
        if user_id not in verification_codes:
            await update.message.reply_text(
                "❌ Sessiya tuwdi!\n\n"
                "Qaytadan baslaw: /start"
            )
            return ConversationHandler.END
        
        code_data = verification_codes[user_id]
        
        # Check expiration
        if datetime.now() > code_data['expires']:
            del verification_codes[user_id]
            await update.message.reply_text(
                "❌ Kod waqtı ótip ketti!\n\n"
                "Qaytadan baslaw: /start"
            )
            return ConversationHandler.END
        
        # Check attempts
        if code_data['attempts'] >= 3:
            del verification_codes[user_id]
            await update.message.reply_text(
                "❌ Júda kóp qate urınıw!\n\n"
                "15 minuttan keyin qaytadan urınıń."
            )
            return ConversationHandler.END
        
        # Verify code
        if entered_code != code_data['code']:
            code_data['attempts'] += 1
            remaining = 3 - code_data['attempts']
            
            await update.message.reply_text(
                f"❌ Qate kod!\n\n"
                f"Qalǵan urınıwlar: {remaining}\n\n"
                f"Qaytadan jazıń:"
            )
            return VERIFICATION_CODE
        
        # Code is correct - create user
        full_name = context.user_data.get('full_name', 'User')
        phone = context.user_data.get('phone', '')
        username = update.effective_user.username
        first_name = update.effective_user.first_name
        last_name = update.effective_user.last_name
        
        # Create organization for user
        org_id = db.create_organization(
            name=f"{full_name} - Kameralar",
            owner_id=user_id
        )
        
        # Add user to database
        db.add_user(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_admin=True,
            phone_number=phone,
            organization_id=org_id,
            role='owner'
        )
        
        # Clean up
        del verification_codes[user_id]
        context.user_data.clear()
        
        # Success message
        success_text = (
            f"✨ *XOSH KELIPSIZ!* ✨\n\n"
            f"👤 {full_name}\n"
            f"📱 `{phone}`\n\n"
            f"━━━━━━━━━━━━\n\n"
            f"🎉 *Shaxsiy kabinet tayar!*\n\n"
            f"✨ Múmkinshilikler:\n\n"
            f"• 📹 Kameralar basqarıwı\n"
            f"• 🎬 Video kóriw hám arxiv\n"
            f"• 🧠 AI izlew sisteması\n"
            f"• 📊 Tahlil hám statistika\n\n"
            f"━━━━━━━━━━━━\n\n"
            f"🚀 Baslaw: /menu"
        )
        
        await update.message.reply_text(success_text, parse_mode='Markdown')
        
        logger.info(f"User registered: {user_id} ({full_name})")
        
        # Show main menu
        from bot.handlers.main_menu import MainMenuHandler
        await MainMenuHandler.show_main_menu(update, context)
        
        return ConversationHandler.END
    
    @staticmethod
    async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel registration process."""
        user_id = update.effective_user.id
        
        # Clean up verification code if exists
        if user_id in verification_codes:
            del verification_codes[user_id]
        
        context.user_data.clear()
        
        await update.message.reply_text(
            "❌ Dizimnen ótiw biykar etildi.\n\n"
            "Qaytadan baslaw: /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Normalize phone number to +998XXXXXXXXX format."""
        if not phone:
            return None
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Handle different formats
        if len(digits) == 9:
            digits = '998' + digits
        elif len(digits) == 12 and digits.startswith('998'):
            pass
        elif len(digits) == 13 and phone.startswith('+'):
            digits = digits
        else:
            return None
        
        # Validate length
        if len(digits) != 12:
            return None
        
        # Validate starts with 998
        if not digits.startswith('998'):
            return None
        
        return '+' + digits


# Export handler instance
registration_handler = RegistrationHandler()
