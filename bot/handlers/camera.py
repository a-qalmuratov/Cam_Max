"""Camera management handler."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.models import db
from camera.stream_manager import stream_manager
from utils.logger import logger

class CameraHandler:
    """Handle camera-related commands."""
    
    @staticmethod
    async def list_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all configured cameras."""
        cameras = db.get_all_cameras()
        
        if not cameras:
            await update.message.reply_text(
                "❌ Hech qanday kamera sozlanmagan.\n\n"
                "Kamera qo'shish uchun /sozlash buyrug'ini yuboring."
            )
            return
        
        message = "📹 **BARCHA KAMERALAR**\n\n"
        
        for i, cam in enumerate(cameras, 1):
            status_icon = "🟢" if cam['status'] == 'active' else "🔴"
            message += (
                f"{i}. {status_icon} **{cam['name']}**\n"
                f"   📍 IP: {cam['ip_address']}:{cam['port']}\n"
                f"   🔧 Turi: {cam['camera_type'].title()}\n"
                f"   📊 Holat: {cam['status']}\n\n"
            )
        
        message += (
            "\n🔧 Kamera qo'shish: /sozlash\n"
            "🧪 Test qilish: /test"
        )
        
        await update.message.reply_text(message)
    
    @staticmethod
    async def test_cameras(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test all cameras."""
        cameras = db.get_all_cameras()
        
        if not cameras:
            await update.message.reply_text(
                "❌ Hech qanday kamera sozlanmagan.\n\n"
                "Kamera qo'shish uchun /sozlash buyrug'ini yuboring."
            )
            return
        
        await update.message.reply_text(
            f"🧪 {len(cameras)} ta kamera tekshirilmoqda...\n"
            f"Iltimos kuting..."
        )
        
        # Load cameras into stream manager if not already loaded
        if not stream_manager.cameras:
            stream_manager.load_cameras_from_db()
        
        results = []
        
        for cam_data in cameras:
            camera = stream_manager.get_camera(cam_data['id'])
            
            if camera:
                success, message = camera.test_connection()
                results.append((cam_data['name'], success, message))
                
                # Update status in database
                status = 'active' if success else 'inactive'
                db.update_camera_status(cam_data['id'], status)
        
        # Send results
        response = "📊 **TEST NATIJALARI**\n\n"
        
        for name, success, msg in results:
            response += f"{msg}\n\n"
        
        await update.message.reply_text(response)
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message."""
        message = (
            "📖 **YORDAM - BUYRUQLAR RO'YXATI**\n\n"
            
            "🎬 **Asosiy buyruqlar:**\n"
            "/start - Botni ishga tushirish va sozlash\n"
            "/kameralar - Barcha kameralarni ko'rish\n"
            "/test - Kameralarni test qilish\n"
            "/sozlash - Yangi kamera qo'shish\n"
            "/yordam - Bu yordam xabari\n\n"
            
            "🔍 **V2: Qidiruv va Tahlil:**\n"
            "/sorov - Tabiiy tilda so'rov\n"
            "Misol: \"3-kamera qaragan xonadagi stolda qizil sumka bor edi uni kim oldi?\"\n"
            "Yoki faqat savol yozing (buyruqsiz)\n\n"
            
            "📹 **V2: Video Yozuv:**\n"
            "/start_recording - Barcha kameralarda yozuvni boshlash\n"
            "/stop_recording - Yozuvni to'xtatish\n"
            "/recording_status - Yozuv holatini ko'rish\n\n"
            
            "📹 **Kamera sozlash:**\n"
            "1. /start yoki /sozlash buyrug'ini yuboring\n"
            "2. Kameralar sonini kiriting\n"
            "3. Har bir kamera uchun:\n"
            "   • Nom (masalan: Asosiy zal)\n"
            "   • IP manzil (masalan: 192.168.1.100)\n"
            "   • RTSP port (odatda 554)\n"
            "   • Login (username)\n"
            "   • Parol\n\n"
            
            "🎥 **Qo'llab-quvvatlanadigan kameralar:**\n"
            "• Hikvision\n"
            "• Dahua\n"
            "• TP-Link\n"
            "• Xiaomi\n"
            "• Va boshqa RTSP/ONVIF kameralar\n\n"
            
            "💡 **V2 Xususiyatlar:**\n"
            "✅ 24/7 video yozuv\n"
            "✅ AI tracking (odamlar va objectlar)\n"
            "✅ Tabiiy tilda qidiruv (O'zbek)\n"
            "✅ Video dalillar bilan javob\n"
            "✅ Timeline va tafsилot\n\n"
            
            "❓ Savollar bo'lsa, developer bilan bog'laning."
        )
        
        await update.message.reply_text(message)
