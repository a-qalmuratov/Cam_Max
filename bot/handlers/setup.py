"""Setup handler for camera configuration via Telegram bot."""
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from database.models import db
from camera.rtsp_client import detect_camera_type
from camera.stream_manager import stream_manager
from utils.logger import logger
from utils.config import get_rtsp_url

# Conversation states
(CAMERA_COUNT, CAMERA_NAME, CAMERA_IP, CAMERA_PORT, 
 CAMERA_USERNAME, CAMERA_PASSWORD, CAMERA_CONFIRM) = range(7)

class SetupHandler:
    """Handle interactive camera setup."""
    
    @staticmethod
    async def start_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start setup process."""
        user = update.effective_user
        
        # Save user to database
        db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_admin=True  # First user is admin
        )
        
        # Check if cameras already exist
        existing_cameras = db.get_all_cameras()
        
        if existing_cameras:
            message = (
                f"👋 Assalomu alaykum {user.first_name}!\n\n"
                f"🎥 Sizda {len(existing_cameras)} ta kamera sozlangan.\n\n"
                f"Nima qilishni xohlaysiz?\n\n"
                f"/kameralar - Barcha kameralarni ko'rish\n"
                f"/sozlash - Yangi kamera qo'shish\n"
                f"/test - Kameralarni test qilish\n"
                f"/yordam - Yordam"
            )
            await update.message.reply_text(message)
            return ConversationHandler.END
        
        message = (
            "👋 Assalomu alaykum!\n\n"
            "🎥 AI-ga asoslangan kuzatuv botiga xush kelibsiz.\n\n"
            "Bu bot sizning do'koningizda o'g'irliklarni aniqlash va "
            "video qidiruvni amalga oshiradi.\n\n"
            "Avval kameralaringizni sozlashimiz kerak.\n\n"
            "Nechta kamera ulashni xohlaysiz? (1-10)"
        )
        
        await update.message.reply_text(message)
        return CAMERA_COUNT
    
    @staticmethod
    async def get_camera_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get number of cameras to configure."""
        try:
            count = int(update.message.text)
            if not 1 <= count <= 10:
                await update.message.reply_text(
                    "❌ Iltimos 1 dan 10 gacha son kiriting."
                )
                return CAMERA_COUNT
            
            context.user_data['total_cameras'] = count
            context.user_data['current_camera'] = 1
            context.user_data['configured_cameras'] = []
            
            message = (
                f"✅ {count} ta kamera sozlanadi.\n\n"
                f"📹 **1-KAMERA SOZLASH**\n\n"
                f"Kamera nomini kiriting (masalan: \"Asosiy zal\" yoki \"Kassa\"):"
            )
            
            await update.message.reply_text(message)
            return CAMERA_NAME
            
        except ValueError:
            await update.message.reply_text(
                "❌ Iltimos faqat raqam kiriting (1-10)."
            )
            return CAMERA_COUNT
    
    @staticmethod
    async def get_camera_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get camera name."""
        name = update.message.text.strip()
        
        if not name or len(name) < 2:
            await update.message.reply_text(
                "❌ Kamera nomi juda qisqa. Iltimos qaytadan kiriting:"
            )
            return CAMERA_NAME
        
        context.user_data['camera_name'] = name
        
        await update.message.reply_text(
            f"Kamera IP manzilini kiriting (masalan: 192.168.1.100):"
        )
        return CAMERA_IP
    
    @staticmethod
    async def get_camera_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get camera IP address."""
        ip = update.message.text.strip()
        
        # Basic IP validation
        parts = ip.split('.')
        if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            await update.message.reply_text(
                "❌ Noto'g'ri IP manzil. Iltimos qaytadan kiriting (masalan: 192.168.1.100):"
            )
            return CAMERA_IP
        
        context.user_data['camera_ip'] = ip
        
        await update.message.reply_text(
            "RTSP portini kiriting (standart 554, agar bilmasangiz 554 deb yozing):"
        )
        return CAMERA_PORT
    
    @staticmethod
    async def get_camera_port(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get RTSP port."""
        try:
            port = int(update.message.text.strip())
            if not 1 <= port <= 65535:
                raise ValueError
            
            context.user_data['camera_port'] = port
            
            await update.message.reply_text(
                "Kamera login (username) ni kiriting:"
            )
            return CAMERA_USERNAME
            
        except ValueError:
            await update.message.reply_text(
                "❌ Noto'g'ri port. Iltimos raqam kiriting (1-65535):"
            )
            return CAMERA_PORT
    
    @staticmethod
    async def get_camera_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get camera username."""
        username = update.message.text.strip()
        
        if not username:
            await update.message.reply_text(
                "❌ Username bo'sh bo'lishi mumkin emas. Qaytadan kiriting:"
            )
            return CAMERA_USERNAME
        
        context.user_data['camera_username'] = username
        
        await update.message.reply_text(
            "Parolni kiriting:"
        )
        return CAMERA_PASSWORD
    
    @staticmethod
    async def get_camera_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get camera password and test connection."""
        password = update.message.text.strip()
        
        if not password:
            await update.message.reply_text(
                "❌ Parol bo'sh bo'lishi mumkin emas. Qaytadan kiriting:"
            )
            return CAMERA_PASSWORD
        
        context.user_data['camera_password'] = password
        
        # Show testing message
        await update.message.reply_text(
            "⏳ Kameraga ulanish tekshirilmoqda...\n"
            "Iltimos kuting..."
        )
        
        # Try to detect camera type and connect
        name = context.user_data['camera_name']
        ip = context.user_data['camera_ip']
        port = context.user_data['camera_port']
        username = context.user_data['camera_username']
        
        # Detect camera type
        camera_type = detect_camera_type(ip, username, password)
        
        # Generate RTSP URL
        rtsp_url = get_rtsp_url(camera_type, ip, port, username, password)
        
        # Save to database
        camera_id = db.add_camera(
            name=name,
            ip_address=ip,
            port=port,
            username=username,
            password=password,
            camera_type=camera_type,
            rtsp_url=rtsp_url
        )
        
        # Add to stream manager and test
        camera = stream_manager.add_camera(
            camera_id=camera_id,
            name=name,
            ip=ip,
            port=port,
            username=username,
            password=password,
            camera_type=camera_type
        )
        
        success, message = camera.test_connection()
        
        await update.message.reply_text(message)
        
        # Track configured cameras
        context.user_data['configured_cameras'].append(camera_id)
        
        # Check if more cameras need to be configured
        current = context.user_data['current_camera']
        total = context.user_data['total_cameras']
        
        if current < total:
            context.user_data['current_camera'] = current + 1
            
            keyboard = [['Ha, davom etish'], ['Yo\'q, bas']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                f"\nKeyingi kamerani ({current + 1}/{total}) sozlashni davom ettirasizmi?",
                reply_markup=reply_markup
            )
            return CAMERA_CONFIRM
        else:
            await update.message.reply_text(
                f"\n🎉 Barcha kameralar ({total}) muvaffaqiyatli sozlandi!\n\n"
                f"Quyidagi buyruqlardan foydalaning:\n"
                f"/kameralar - Barcha kameralarni ko'rish\n"
                f"/test - Kameralarni test qilish\n"
                f"/yordam - Yordam",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
    
    @staticmethod
    async def confirm_next_camera(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm if user wants to add another camera."""
        response = update.message.text.lower()
        
        if 'ha' in response or 'davom' in response:
            current = context.user_data['current_camera']
            total = context.user_data['total_cameras']
            
            await update.message.reply_text(
                f"📹 **{current}-KAMERA SOZLASH**\n\n"
                f"Kamera nomini kiriting:",
                reply_markup=ReplyKeyboardRemove()
            )
            return CAMERA_NAME
        else:
            total_configured = len(context.user_data['configured_cameras'])
            
            await update.message.reply_text(
                f"✅ {total_configured} ta kamera sozlandi.\n\n"
                f"Quyidagi buyruqlardan foydalaning:\n"
                f"/kameralar - Barcha kameralarni ko'rish\n"
                f"/test - Kameralarni test qilish\n"
                f"/yordam - Yordam",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
    
    @staticmethod
    async def cancel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel setup process."""
        await update.message.reply_text(
            "❌ Sozlash bekor qilindi.\n\n"
            "Qaytadan boshlash uchun /start buyrug'ini yuboring.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
