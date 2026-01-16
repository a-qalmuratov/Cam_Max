"""
Camera management with full CRUD operations.
Premium UI with status indicators and controls.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.models import db
from camera.stream_manager import stream_manager
from utils.logger import logger

# Camera wizard states
CAM_NAME = 1
CAM_IP = 2
CAM_PORT = 3
CAM_USERNAME = 4
CAM_PASSWORD = 5
CAM_CONFIRM = 6


class CameraManagementHandler:
    """Handle camera management with premium UI."""
    
    @staticmethod
    async def show_camera_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show list of cameras with status and controls."""
        query = update.callback_query
        user_id = update.effective_user.id
        
        # Get user and their cameras
        user = db.get_user(user_id)
        if not user:
            await query.edit_message_text("❌ Foydalanuvchi topilmadi!")
            return
        
        org_id = user.get('organization_id')
        cameras = db.get_cameras_by_organization(org_id) or []
        
        # Build camera list
        if not cameras:
            text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃      📹 KAMERALAR         ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "📭 Hech qanday kamera yo'q\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Birinchi kamerangizni qo'shing!"
            )
            keyboard = [
                [InlineKeyboardButton("➕ Yangi Kamera Qo'shish", callback_data="cam_add")],
                [InlineKeyboardButton("« Asosiy Menyu", callback_data="menu_main")]
            ]
        else:
            text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃      📹 KAMERALAR         ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            )
            
            keyboard = []
            for cam in cameras:
                cam_id = cam['id']
                name = cam['name']
                status = cam.get('status', 'inactive')
                
                # Status icon
                if status == 'active':
                    icon = "🟢"
                    status_text = "ON"
                else:
                    icon = "🔴"
                    status_text = "OFF"
                
                text += f"{icon} {cam_id}. {name}\n"
                text += f"   ├─ Status: {status_text}\n"
                text += f"   └─ IP: {cam['ip_address']}\n\n"
                
                # Add button for each camera
                btn_text = f"{icon} {name}"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"cam_detail_{cam_id}")])
            
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            text += f"📊 Jami: {len(cameras)} kamera"
            
            keyboard.append([InlineKeyboardButton("➕ Yangi Kamera", callback_data="cam_add")])
            keyboard.append([InlineKeyboardButton("« Asosiy Menyu", callback_data="menu_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    @staticmethod
    async def show_camera_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed camera view with controls."""
        query = update.callback_query
        await query.answer()
        
        # Extract camera ID
        camera_id = int(query.data.split('_')[-1])
        
        # Get camera info
        camera = db.get_camera(camera_id)
        if not camera:
            await query.edit_message_text("❌ Kamera topilmadi!")
            return
        
        # Verify ownership
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        if camera.get('organization_id') != user.get('organization_id'):
            await query.edit_message_text("❌ Bu kamera sizga tegishli emas!")
            return
        
        status = camera.get('status', 'inactive')
        status_icon = "🟢" if status == 'active' else "🔴"
        status_text = "Faol" if status == 'active' else "O'chirilgan"
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃  📹 {camera['name'][:20]:<20} ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"{status_icon} Status: {status_text}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📍 IP: {camera['ip_address']}\n"
            f"🔌 Port: {camera['port']}\n"
            f"👤 Login: {camera['username']}\n"
            f"🔑 Parol: ••••••••\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⬇️ Amalni tanlang:"
        )
        
        # Build control buttons
        if status == 'active':
            toggle_btn = InlineKeyboardButton("⏹️ O'chirish", callback_data=f"cam_off_{camera_id}")
        else:
            toggle_btn = InlineKeyboardButton("▶️ Yoqish", callback_data=f"cam_on_{camera_id}")
        
        keyboard = [
            [toggle_btn],
            [InlineKeyboardButton("📸 Hozirgi Rasm", callback_data=f"cam_snapshot_{camera_id}")],
            [InlineKeyboardButton("📹 Video Arxiv", callback_data=f"cam_archive_{camera_id}")],
            [InlineKeyboardButton("⚙️ Sozlamalar", callback_data=f"cam_settings_{camera_id}")],
            [InlineKeyboardButton("🗑️ O'chirish", callback_data=f"cam_delete_{camera_id}")],
            [InlineKeyboardButton("« Kameralar", callback_data="menu_cameras")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    @staticmethod
    async def toggle_camera_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Turn camera ON."""
        query = update.callback_query
        camera_id = int(query.data.split('_')[-1])
        
        try:
            db.update_camera_status(camera_id, 'active')
            await query.answer("✅ Kamera yoqildi!", show_alert=True)
        except Exception as e:
            await query.answer(f"❌ Xatolik: {str(e)}", show_alert=True)
        
        # Refresh detail view
        context.user_data['refresh_cam_id'] = camera_id
        await CameraManagementHandler.show_camera_detail(update, context)
    
    @staticmethod
    async def toggle_camera_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Turn camera OFF."""
        query = update.callback_query
        camera_id = int(query.data.split('_')[-1])
        
        try:
            db.update_camera_status(camera_id, 'inactive')
            await query.answer("⏹️ Kamera o'chirildi!", show_alert=True)
        except Exception as e:
            await query.answer(f"❌ Xatolik: {str(e)}", show_alert=True)
        
        # Refresh detail view
        await CameraManagementHandler.show_camera_detail(update, context)
    
    @staticmethod
    async def confirm_delete_camera(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show delete confirmation."""
        query = update.callback_query
        await query.answer()
        
        camera_id = int(query.data.split('_')[-1])
        camera = db.get_camera(camera_id)
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃      ⚠️ O'CHIRISH?        ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"📹 {camera['name']}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ Barcha arxivlar ham o'chiriladi!\n\n"
            "Bu amalni qaytarib bo'lmaydi."
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Ha, O'chirish", callback_data=f"cam_delete_confirm_{camera_id}"),
                InlineKeyboardButton("❌ Yo'q", callback_data=f"cam_detail_{camera_id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    @staticmethod
    async def delete_camera(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Delete camera from database."""
        query = update.callback_query
        camera_id = int(query.data.split('_')[-1])
        
        try:
            db.delete_camera(camera_id)
            await query.answer("✅ Kamera o'chirildi!", show_alert=True)
        except Exception as e:
            await query.answer(f"❌ Xatolik: {str(e)}", show_alert=True)
        
        # Return to camera list
        await CameraManagementHandler.show_camera_list(update, context)
    
    @staticmethod
    async def capture_realtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Redirect to video view for snapshot."""
        from bot.handlers.video_view import VideoViewHandler
        # Change callback data format to match video view
        query = update.callback_query
        camera_id = int(query.data.split('_')[-1])
        query.data = f"realtime_{camera_id}"
        await VideoViewHandler.capture_realtime(update, context)
    
    @staticmethod
    async def start_add_camera(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start add camera wizard."""
        query = update.callback_query
        await query.answer()
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   ➕ YANGI KAMERA [1/5]   ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "📝 Kamera nomini kiriting:\n\n"
            "   Misol: Asosiy zal\n"
            "   Misol: Kassa\n"
            "   Misol: Kirish\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ Bekor qilish: /cancel"
        )
        
        await query.edit_message_text(text)
        return CAM_NAME
    
    @staticmethod
    async def get_camera_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get camera name in wizard."""
        name = update.message.text.strip()
        
        if len(name) < 2:
            await update.message.reply_text("❌ Ism juda qisqa! Kamida 2 ta belgi kiriting.")
            return CAM_NAME
        
        context.user_data['cam_name'] = name
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   📍 IP MANZIL [2/5]      ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"✅ Nom: {name}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📍 IP manzilni kiriting:\n\n"
            "   Misol: 192.168.1.100\n"
            "   Misol: 10.0.0.50\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ Bekor qilish: /cancel"
        )
        
        await update.message.reply_text(text)
        return CAM_IP
    
    @staticmethod
    async def get_camera_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get camera IP address."""
        ip = update.message.text.strip()
        
        # Validate IP format
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, ip):
            await update.message.reply_text(
                "❌ Noto'g'ri IP format!\n\n"
                "To'g'ri format: 192.168.1.100"
            )
            return CAM_IP
        
        context.user_data['cam_ip'] = ip
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   🔌 PORT [3/5]           ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"✅ Nom: {context.user_data['cam_name']}\n"
            f"✅ IP: {ip}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔌 RTSP portni kiriting:\n\n"
            "   Standart: 554\n"
            "   Boshqa: 8554, 5554\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Enter bosing = 554"
        )
        
        await update.message.reply_text(text)
        return CAM_PORT
    
    @staticmethod
    async def get_camera_port(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get camera port."""
        port_text = update.message.text.strip()
        
        # Default to 554 if empty
        if not port_text:
            port = 554
        else:
            try:
                port = int(port_text)
                if port < 1 or port > 65535:
                    raise ValueError()
            except ValueError:
                await update.message.reply_text("❌ Noto'g'ri port! 1-65535 oralig'ida kiriting.")
                return CAM_PORT
        
        context.user_data['cam_port'] = port
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   👤 LOGIN [4/5]          ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"✅ Nom: {context.user_data['cam_name']}\n"
            f"✅ IP: {context.user_data['cam_ip']}\n"
            f"✅ Port: {port}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👤 Foydalanuvchi nomini kiriting:\n\n"
            "   Standart: admin\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Enter bosing = admin"
        )
        
        await update.message.reply_text(text)
        return CAM_USERNAME
    
    @staticmethod
    async def get_camera_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get camera username."""
        username = update.message.text.strip() or 'admin'
        context.user_data['cam_username'] = username
        
        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   🔑 PAROL [5/5]          ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"✅ Nom: {context.user_data['cam_name']}\n"
            f"✅ IP: {context.user_data['cam_ip']}\n"
            f"✅ Port: {context.user_data['cam_port']}\n"
            f"✅ Login: {username}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔑 Parolni kiriting:\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 Parol xavfsiz saqlanadi"
        )
        
        await update.message.reply_text(text)
        return CAM_PASSWORD
    
    @staticmethod
    async def get_camera_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get camera password, test connection, and save."""
        password = update.message.text.strip()
        
        if not password:
            await update.message.reply_text("❌ Parol bo'sh bo'lishi mumkin emas!")
            return CAM_PASSWORD
        
        # Get user organization
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        org_id = user.get('organization_id')
        
        cam_data = context.user_data
        
        # Show testing message
        testing_msg = await update.message.reply_text(
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   🔄 TEKSHIRILMOQDA...    ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"📹 {cam_data['cam_name']}\n"
            f"📍 {cam_data['cam_ip']}:{cam_data['cam_port']}\n\n"
            "⏳ Kameraga ulanish tekshirilmoqda..."
        )
        
        # Test camera connection before saving
        from camera.rtsp_client import RTSPCamera
        
        test_camera = RTSPCamera(
            camera_id=0,
            name=cam_data['cam_name'],
            ip=cam_data['cam_ip'],
            port=cam_data['cam_port'],
            username=cam_data['cam_username'],
            password=password,
            camera_type='generic'
        )
        
        # Try to connect
        connection_success, connection_msg = test_camera.test_connection()
        test_camera.disconnect()
        
        if not connection_success:
            # Connection failed - ask user what to do
            text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   ⚠️ ULANISH XATOSI       ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"📹 {cam_data['cam_name']}\n"
                f"📍 {cam_data['cam_ip']}:{cam_data['cam_port']}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{connection_msg}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Nima qilmoqchisiz?\n"
                "• /retry - Qayta urinish\n"
                "• /save - Baribir saqlash\n"
                "• /cancel - Bekor qilish"
            )
            
            context.user_data['cam_password'] = password
            await testing_msg.edit_text(text)
            return CAM_PASSWORD
        
        # Connection successful - save camera
        rtsp_url = test_camera.rtsp_url
        
        try:
            # Save camera to database
            camera_id = db.add_camera(
                name=cam_data['cam_name'],
                ip_address=cam_data['cam_ip'],
                port=cam_data['cam_port'],
                username=cam_data['cam_username'],
                password=password,
                rtsp_url=rtsp_url,
                organization_id=org_id
            )
            
            # Update status to active since connection was successful
            db.update_camera_status(camera_id, 'active')
            
            # Clear wizard data
            for key in ['cam_name', 'cam_ip', 'cam_port', 'cam_username', 'cam_password']:
                context.user_data.pop(key, None)
            
            text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃  ✅ KAMERA MUVAFFAQIYATLI ┃\n"
                "┃     QO'SHILDI!            ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"📹 {cam_data['cam_name']}\n"
                f"📍 {cam_data['cam_ip']}:{cam_data['cam_port']}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{connection_msg}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🟢 Kamera ONLINE va tayyor!"
            )
            
            keyboard = [
                [InlineKeyboardButton("📸 Hozirgi Rasm", callback_data=f"realtime_{camera_id}")],
                [InlineKeyboardButton("📹 Kamerani Ko'rish", callback_data=f"cam_detail_{camera_id}")],
                [InlineKeyboardButton("➕ Yana Qo'shish", callback_data="cam_add")],
                [InlineKeyboardButton("« Kameralar", callback_data="menu_cameras")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await testing_msg.edit_text(text, reply_markup=reply_markup)
            
            logger.info(f"Camera added and connected: {cam_data['cam_name']} ({cam_data['cam_ip']})")
            
        except Exception as e:
            logger.error(f"Error adding camera: {e}")
            await testing_msg.edit_text(f"❌ Xatolik: {str(e)}")
        
        return ConversationHandler.END
    
    @staticmethod
    async def cancel_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel camera wizard."""
        # Clear wizard data
        for key in ['cam_name', 'cam_ip', 'cam_port', 'cam_username']:
            context.user_data.pop(key, None)
        
        await update.message.reply_text(
            "❌ Kamera qo'shish bekor qilindi.\n\n"
            "Asosiy menyu: /menu"
        )
        return ConversationHandler.END


# Import re for IP validation
import re

# Export handler instance
camera_management_handler = CameraManagementHandler()

# Export wizard states
__all__ = ['CameraManagementHandler', 'camera_management_handler', 
           'CAM_NAME', 'CAM_IP', 'CAM_PORT', 'CAM_USERNAME', 'CAM_PASSWORD', 'CAM_CONFIRM']
