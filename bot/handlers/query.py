"""Query handler for natural language searches."""
from telegram import Update
from telegram.ext import ContextTypes
from nlp.query_parser import search_engine
from utils.logger import logger

class QueryHandler:
    """Handle natural language queries."""
    
    @staticmethod
    async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle user query.
        
        Example: "3-kamera qaragan xonadagi stolda qizil sumka bor edi uni kim oldi?"
        """
        user_id = update.effective_user.id
        query_text = update.message.text
        
        # Remove /sorov command if present
        if query_text.startswith('/sorov'):
            query_text = query_text.replace('/sorov', '').strip()
        
        if not query_text:
            await update.message.reply_text(
                "❌ Iltimos savolingizni kiriting.\n\n"
                "Misol: 3-kamera qaragan xonadagi stolda qizil sumka bor edi uni kim oldi?"
            )
            return
        
        # Show searching message
        await update.message.reply_text(
            "🔍 Qidirilmoqda...\n"
            "Iltimos kuting..."
        )
        
        try:
            # Search
            result = search_engine.search(query_text, user_id)
            
            # Format response
            response = await QueryHandler._format_response(result)
            
            await update.message.reply_text(response)
            
            # Send evidence if available
            if result['evidence'].get('videos'):
                for video_path in result['evidence']['videos']:
                    try:
                        with open(video_path, 'rb') as video_file:
                            await update.message.reply_video(
                                video=video_file,
                                caption="📹 Video dalil"
                            )
                    except Exception as e:
                        logger.error(f"Error sending video: {e}")
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            await update.message.reply_text(
                f"❌ Xatolik yuz berdi: {str(e)}\n\n"
                "Iltimos qaytadan urinib ko'ring."
            )
    
    @staticmethod
    async def _format_response(result: dict) -> str:
        """Format search results for user."""
        params = result['query_params']
        results_count = len(result['results'])
        evidence = result['evidence']
        
        if results_count == 0:
            camera_text = params.get('camera', 'Barcha')
            object_text = params.get('object', "Noma'lum")
            time_text = params.get('time_range', "So'nggi 24 soat")
            return (
                "❌ Hech narsa topilmadi.\n\n"
                "📊 Qidiruv parametrlari:\n"
                f"- Kamera: {camera_text}\n"
                f"- Object: {object_text}\n"
                f"- Vaqt: {time_text}\n\n"
                "Iltimos boshqa so'rov bilan urinib ko'ring."
            )
        
        response = f"✅ Topildi! ({results_count} natija)\n\n"
        
        # Add camera info
        if params.get('camera'):
            response += f"📹 Kamera: {params['camera']}\n"
        
        # Add location info
        if params.get('location'):
            response += f"📍 Joyi: {params['location']}\n"
        
        # Add action info
        if params.get('action'):
            response += f"⚡ Harakat: {params['action']}\n"
        
        response += f"\n⏱️ Javob vaqti: {result.get('response_time_ms', 0)} ms\n"
        
        # Add evidence description
        if evidence.get('description_uz'):
            response += f"\n📝 {evidence['description_uz']}\n"
        
        # Add timeline
        if evidence.get('timeline'):
            response += "\n⏰ **TIMELINE:**\n"
            for event in evidence['timeline'][:5]:  # Show first 5 events
                response += f"• {event.get('time')} - {event.get('description')}\n"
        
        response += "\n📊 To'liq natijalar ushbu xabarga biriktirilgan."
        
        return response

# Export
query_handler = QueryHandler()
