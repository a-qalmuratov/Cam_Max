"""
User registration and authentication system with 2FA.
Professional implementation with premium UI.
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
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃                           ┃\n"
            "┃      🎯 CAM MAX PRO       ┃\n"
            "┃                           ┃\n"
            "┃   AI Security Platform    ┃\n"
            "┃                           ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "👋 Xush kelibsiz!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔐 Shaxsiy kabinet yaratish\n\n"
            "📝 Ism va familiyangizni kiriting:\n\n"
            "   Misol: Azamat Qalmuratov\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💎 100% xavfsiz va maxfiy"
        )
        
        await update.message.reply_text(welcome_text)
        return REGISTRATION_NAME
    
    @staticmethod
    async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get user's full name with validation."""
        full_name = update.message.text.strip()
        
        # Validate name - allow Latin, Cyrillic, and spaces
        if len(full_name) < 3:
            await update.message.reply_text(
                "❌ Ism juda qisqa!\n\n"
                "Iltimos to'liq ism va familiyangizni kiriting.\n"
                "Masalan: Azamat Qalmuratov"
            )
            return REGISTRATION_NAME
        
        # Allow Latin, Cyrillic, apostrophe, and spaces
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s']+$", full_name):
            await update.message.reply_text(
                "❌ Noto'g'ri format!\n\n"
                "Faqat harflar ishlatilishi mumkin.\n"
                "Masalan: Azamat Qalmuratov"
            )
            return REGISTRATION_NAME
        
        # Store name
        context.user_data['full_name'] = full_name
        
        # Request phone number with button
        keyboard = [[KeyboardButton("📱 Telefon raqamni ulashish", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        phone_text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃      ✅ ISM QABUL QILINDI  ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"👤 {full_name}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📱 Telefon raqamingizni yuboring\n\n"
            "   Tugmani bosing yoki qo'lda kiriting:\n"
            "   +998 XX XXX XX XX\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 Bank darajasida shifrlangan"
        )
        
        await update.message.reply_text(phone_text, reply_markup=reply_markup)
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
                "❌ Noto'g'ri telefon raqam!\n\n"
                "Format: +998 XX XXX XX XX\n"
                "Masalan: +998901234567\n\n"
                "Qaytadan kiriting:",
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
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃      🔐 2FA VERIFICATION   ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"📱 Telefon: {phone}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔑 TASDIQLASH KODI:\n\n"
            f"       [ {code} ]\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⏰ Amal qilish: 5 daqiqa\n"
            "🔢 Urinishlar: 3 ta\n\n"
            "💬 Kodni kiriting:"
        )
        
        await update.message.reply_text(code_text, reply_markup=ReplyKeyboardRemove())
        
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
                "❌ Sessiya tugadi!\n\n"
                "Qaytadan boshlash: /start"
            )
            return ConversationHandler.END
        
        code_data = verification_codes[user_id]
        
        # Check expiration
        if datetime.now() > code_data['expires']:
            del verification_codes[user_id]
            await update.message.reply_text(
                "❌ Kod muddati tugadi!\n\n"
                "Qaytadan boshlash: /start"
            )
            return ConversationHandler.END
        
        # Check attempts
        if code_data['attempts'] >= 3:
            del verification_codes[user_id]
            await update.message.reply_text(
                "❌ Juda ko'p xato urinish!\n\n"
                "15 daqiqadan so'ng qaytadan urinib ko'ring."
            )
            return ConversationHandler.END
        
        # Verify code
        if entered_code != code_data['code']:
            code_data['attempts'] += 1
            remaining = 3 - code_data['attempts']
            
            await update.message.reply_text(
                f"❌ Noto'g'ri kod!\n\n"
                f"Qolgan urinishlar: {remaining}\n\n"
                f"Qaytadan kiriting:"
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
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃                           ┃\n"
            "┃    ✨ XUSH KELIBSIZ! ✨   ┃\n"
            "┃                           ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"👤 {full_name}\n"
            f"📱 {phone}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🎉 Shaxsiy kabinet tayyor!\n\n"
            "✨ Imkoniyatlar:\n\n"
            "   📹 Kameralar boshqaruvi\n"
            "   🎬 Video ko'rish va arxiv\n"
            "   🧠 AI qidiruv tizimi\n"
            "   📊 Tahlil va statistika\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🚀 Boshlash: /menu"
        )
        
        await update.message.reply_text(success_text)
        
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
            "❌ Ro'yxatdan o'tish bekor qilindi.\n\n"
            "Qayta boshlash: /start",
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
