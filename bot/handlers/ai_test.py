"""AI detection test handler."""
import io
import cv2
from telegram import Update
from telegram.ext import ContextTypes
from database.models import db
from camera.stream_manager import stream_manager
from ai.detector import detector
from utils.logger import logger

class AITestHandler:
    """Handle AI detection testing."""
    
    @staticmethod
    async def test_detection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test AI detection on all cameras."""
        cameras = db.get_all_cameras()
        
        if not cameras:
            await update.message.reply_text(
                "❌ Hech qanday kamera sozlanmagan.\n\n"
                "Avval kamera qo'shish uchun /sozlash buyrug'ini yuboring."
            )
            return
        
        await update.message.reply_text(
            f"🤖 AI detection {len(cameras)} ta kamerada sinovdan o'tkazilmoqda...\n"
            f"Iltimos kuting..."
        )
        
        # Load cameras if not loaded
        if not stream_manager.cameras:
            stream_manager.load_cameras_from_db()
        
        for cam_data in cameras:
            camera = stream_manager.get_camera(cam_data['id'])
            
            if not camera:
                continue
            
            # Connect if not connected
            if not camera.is_connected:
                success = camera.connect()
                if not success:
                    await update.message.reply_text(
                        f"❌ '{cam_data['name']}' kamerasiga ulanib bo'lmadi"
                    )
                    continue
            
            # Get frame from camera
            frame = camera.get_frame()
            
            if frame is None:
                await update.message.reply_text(
                    f"❌ '{cam_data['name']}' kamerasidan kadr olib bo'lmadi"
                )
                continue
            
            # Run detection
            try:
                detections = detector.detect(frame)
                
                # Draw detections on frame
                annotated_frame = detector.draw_detections(frame, detections)
                
                # Get summary
                summary = detector.get_detection_summary(detections)
                
                # Convert frame to bytes for sending
                _, buffer = cv2.imencode('.jpg', annotated_frame)
                image_bytes = io.BytesIO(buffer.tobytes())
                image_bytes.seek(0)
                
                # Send result
                caption = (
                    f"📹 **{cam_data['name']}**\n\n"
                    f"{summary}\n\n"
                    f"📊 Aniqlangan objectlar soni: {len(detections)}\n"
                    f"✅ AI detection ishlayapti!"
                )
                
                await update.message.reply_photo(
                    photo=image_bytes,
                    caption=caption
                )
                
                # Save detection to database
                for det in detections:
                    db.add_detection(
                        camera_id=cam_data['id'],
                        object_type=det['class'],
                        confidence=det['confidence'],
                        bbox=det['bbox']
                    )
                
            except Exception as e:
                logger.error(f"Error during AI detection: {e}")
                await update.message.reply_text(
                    f"❌ '{cam_data['name']}' da xatolik yuz berdi: {str(e)}"
                )

# Export
ai_test_handler = AITestHandler()
