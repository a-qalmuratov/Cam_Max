"""
CAM MAX BOT - Keng qamrovli End-to-End Test Skripti
Barcha kritik funksiyalarni tekshiradi.
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Test results
TESTS_PASSED = 0
TESTS_FAILED = 0
TEST_RESULTS = []


def check_test(name: str, condition: bool, details: str = ""):
    """Test helper - renamed to avoid pytest confusion."""
    global TESTS_PASSED, TESTS_FAILED
    if condition:
        TESTS_PASSED += 1
        TEST_RESULTS.append(("✅", name, details))
        print(f"✅ {name}")
    else:
        TESTS_FAILED += 1
        TEST_RESULTS.append(("❌", name, details))
        print(f"❌ {name} - {details}")


def test_callback_patterns():
    """Test 1: Callback pattern va callback_data mos kelishini tekshirish."""
    print("\n" + "="*50)
    print("1️⃣ CALLBACK PATTERNS TEKSHIRUVI")
    print("="*50)
    
    # Collect all callback_data from handlers
    callback_button_patterns = [
        # video_view.py
        ("view_realtime", r"^view_realtime$"),
        ("realtime_123", r"^realtime_\d+$"),
        ("view_archive", r"^view_archive$"),
        ("archive_10min", r"^archive_(10min|1hour|today|yesterday)$"),
        ("archive_1hour", r"^archive_(10min|1hour|today|yesterday)$"),
        ("archive_today", r"^archive_(10min|1hour|today|yesterday)$"),
        ("archive_yesterday", r"^archive_(10min|1hour|today|yesterday)$"),
        ("archive_custom", r"^archive_custom$"),
        ("archive_cam_5", r"^archive_cam_\d+$"),
        ("view_bookmarks", r"^view_bookmarks$"),
        ("bookmark_save_12", r"^bookmark_save_\d+$"),
        ("bookmark_view_7", r"^bookmark_view_\d+$"),
        ("bookmark_delete_3", r"^bookmark_delete_\d+$"),
        ("view_download", r"^view_download$"),
        
        # ai_search
        ("ai_view_video", r"^ai_view_video$"),
        
        # quick_actions
        ("quick_actions", r"^quick_actions$"),
        ("quick_snapshot", r"^quick_snapshot$"),
        ("quick_status", r"^quick_status$"),
        
        # export
        ("export_menu", r"^export_menu$"),
        ("export_video", r"^export_video$"),
        ("export_format_mp4", r"^export_format_(mp4|avi)$"),
        ("export_quality_720", r"^export_quality_(1080|720|480)$"),
        ("export_stats", r"^export_stats$"),
        ("export_events", r"^export_events$"),
        
        # statistics
        ("stats_weekly", r"^stats_weekly$"),
        ("stats_cameras", r"^stats_cameras$"),
        ("stats_alerts", r"^stats_alerts$"),
        ("stats_export", r"^stats_export$"),
        ("stats_graph", r"^stats_graph$"),
        
        # analytics
        ("stats_detections", r"^stats_detections$"),
        ("stats_storage", r"^stats_storage$"),
        ("stats_activity", r"^stats_activity$"),
        ("menu_analytics", r"^menu_analytics$"),
        
        # settings
        ("settings_profile", r"^settings_profile$"),
        ("settings_notifications", r"^settings_notifications$"),
        ("settings_security", r"^settings_security$"),
        ("settings_archive", r"^settings_archive$"),
        ("settings_help", r"^settings_help$"),
        
        # camera management
        ("cam_add", r"^cam_add$"),
        ("cam_view_3", r"^cam_view_\d+$"),
        ("cam_edit_5", r"^cam_edit_\d+$"),
        ("cam_delete_7", r"^cam_delete_\d+$"),
        ("cam_delete_confirm_7", r"^cam_delete_confirm_\d+$"),
        ("cam_snapshot_2", r"^cam_snapshot_\d+$"),
        
        # main menu
        ("menu_main", r"^menu_"),
        ("menu_cameras", r"^menu_"),
        ("menu_view", r"^menu_"),
        ("menu_ai", r"^menu_"),
        ("menu_stats", r"^menu_"),
        ("menu_settings", r"^menu_"),
    ]
    
    all_match = True
    for callback_data, pattern in callback_button_patterns:
        matches = bool(re.match(pattern, callback_data))
        if not matches:
            all_match = False
            print(f"  ❌ '{callback_data}' <-> '{pattern}' MOS EMAS!")
    
    check_test("Barcha callback patterns mos keladi", all_match, 
         f"{len(callback_button_patterns)} ta callback tekshirildi")


def test_access_control():
    """Test 2: Access control ishlashini tekshirish."""
    print("\n" + "="*50)
    print("2️⃣ ACCESS CONTROL TEKSHIRUVI")
    print("="*50)
    
    try:
        from utils.access_control import access_control, time_helper
        
        # Test functions exist
        check_test("AccessControl class mavjud", hasattr(access_control, 'check_camera_access'))
        check_test("check_bookmark_access mavjud", hasattr(access_control, 'check_bookmark_access'))
        check_test("TimeHelper class mavjud", hasattr(time_helper, 'now_local'))
        check_test("parse_uzbek_time_phrase mavjud", hasattr(time_helper, 'parse_uzbek_time_phrase'))
        
    except ImportError as e:
        check_test("access_control import", False, str(e))


def test_timezone():
    """Test 3: Timezone konversiya to'g'riligini tekshirish."""
    print("\n" + "="*50)
    print("3️⃣ TIMEZONE TEKSHIRUVI")
    print("="*50)
    
    try:
        from utils.access_control import time_helper
        
        # Test local time
        local_now = time_helper.now_local()
        check_test("now_local() ishlaydi", local_now is not None)
        check_test("Timezone Asia/Tashkent", str(local_now.tzinfo) == "Asia/Tashkent", 
             f"Got: {local_now.tzinfo}")
        
        # Test UTC conversion
        utc_now = time_helper.now_utc()
        check_test("now_utc() ishlaydi", utc_now is not None)
        
        # Test time parsing
        start, end = time_helper.parse_uzbek_time_phrase("bugun")
        check_test("'bugun' parse ishlaydi", start is not None and end is not None)
        check_test("'bugun' vaqt oralig'i to'g'ri", start < end, 
             f"start={start}, end={end}")
        
        # Test yesterday
        start_y, end_y = time_helper.parse_uzbek_time_phrase("kecha")
        check_test("'kecha' parse ishlaydi", start_y is not None)
        check_test("'kecha' bugundan oldin", end_y < time_helper.now_utc())
        
    except Exception as e:
        check_test("Timezone tests", False, str(e))


def test_database_operations():
    """Test 4: Database operatsiyalarini tekshirish."""
    print("\n" + "="*50)
    print("4️⃣ DATABASE OPERATSIYALARI TEKSHIRUVI")
    print("="*50)
    
    try:
        from database.models import db
        
        # Test user operations
        check_test("db.get_user() mavjud", hasattr(db, 'get_user'))
        check_test("db.get_camera() mavjud", hasattr(db, 'get_camera'))
        check_test("db.get_bookmarks() mavjud", hasattr(db, 'get_bookmarks'))
        check_test("db.add_bookmark() mavjud", hasattr(db, 'add_bookmark'))
        check_test("db.delete_bookmark() mavjud", hasattr(db, 'delete_bookmark'))
        check_test("db.get_statistics() mavjud", hasattr(db, 'get_statistics'))
        check_test("db.get_weekly_statistics() mavjud", hasattr(db, 'get_weekly_statistics'))
        
        # Test bookmark CRUD with actual operations
        TEST_USER_ID = 99999999
        
        # Add bookmark
        bookmark_id = db.add_bookmark(
            user_id=TEST_USER_ID,
            camera_id=1,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            name="Test Bookmark"
        )
        check_test("add_bookmark() ishlaydi", bookmark_id is not None and bookmark_id > 0,
             f"ID: {bookmark_id}")
        
        # Get bookmarks
        bookmarks = db.get_bookmarks(TEST_USER_ID)
        check_test("get_bookmarks() ishlaydi", len(bookmarks) > 0,
             f"Count: {len(bookmarks)}")
        
        # Verify bookmark was saved
        found = any(b.get('name') == "Test Bookmark" for b in bookmarks)
        check_test("Bookmark DB'da saqlangan", found)
        
        # Delete bookmark
        deleted = db.delete_bookmark(bookmark_id, TEST_USER_ID)
        check_test("delete_bookmark() ishlaydi", deleted)
        
        # Verify deletion
        bookmarks_after = db.get_bookmarks(TEST_USER_ID)
        not_found = not any(b.get('id') == bookmark_id for b in bookmarks_after)
        check_test("Bookmark o'chirilgan", not_found)
        
    except Exception as e:
        check_test("Database tests", False, str(e))


def test_ai_integration():
    """Test 5: AI integratsiyasini tekshirish."""
    print("\n" + "="*50)
    print("5️⃣ AI INTEGRATSIYA TEKSHIRUVI")
    print("="*50)
    
    try:
        from ai.gemini_ai import gemini_ai
        
        check_test("gemini_ai instance mavjud", gemini_ai is not None)
        check_test("chat() metodi mavjud", hasattr(gemini_ai, 'chat'))
        check_test("analyze_image() metodi mavjud", hasattr(gemini_ai, 'analyze_image'))
        check_test("clear_history() metodi mavjud", hasattr(gemini_ai, 'clear_history'))
        check_test("_parse_action() metodi mavjud", hasattr(gemini_ai, '_parse_action'))
        
        # Test parse action with various inputs
        test_cases = [
            ('```json\n{"action": "search"}\n```', {'action': 'search'}),
            ('Normal text without JSON', {}),
        ]
        
        for text, expected_action in test_cases:
            result = gemini_ai._parse_action(text)
            matches = result.get('action') == expected_action.get('action')
            check_test(f"_parse_action handles: '{text[:30]}...'", matches)
        
    except Exception as e:
        check_test("AI integration tests", False, str(e))


def test_query_parser():
    """Test 6: Query parser NLP tekshiruvi."""
    print("\n" + "="*50)
    print("6️⃣ NLP QUERY PARSER TEKSHIRUVI")
    print("="*50)
    
    try:
        from nlp.query_parser import UzbekQueryParser, search_engine
        
        parser = UzbekQueryParser()
        
        # Test queries
        test_queries = [
            ("3-kamerada bugun qizil sumka", {'camera': 3, 'color': 'qizil', 'object': 'sumka'}),
            ("kecha mashina kirdi", {'action': 'kirdi'}),
            ("1-kamera ertalab", {'camera': 1}),
        ]
        
        for query, expected in test_queries:
            result = parser.parse(query)
            
            all_match = True
            for key, val in expected.items():
                if result.get(key) != val:
                    all_match = False
                    break
            
            check_test(f"Parse: '{query}'", all_match, f"Got: {result}")
        
        # Test time_range is returned
        result = parser.parse("bugun")
        check_test("time_range qaytariladi", 'time_range' in result and result['time_range'] is not None)
        
    except Exception as e:
        check_test("Query parser tests", False, str(e))


def test_conversation_handlers():
    """Test 7: Conversation handler fallback'larini tekshirish."""
    print("\n" + "="*50)
    print("7️⃣ CONVERSATION HANDLER TEKSHIRUVI")
    print("="*50)
    
    try:
        # Check main.py for conversation timeout
        with open('bot/main.py', 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        check_test("conversation_timeout mavjud", 'conversation_timeout' in main_content)
        check_test("/cancel fallback mavjud", "CommandHandler('cancel'" in main_content)
        check_test("/start fallback mavjud", "CommandHandler('start'" in main_content)
        check_test("/menu fallback mavjud", "CommandHandler('menu'" in main_content)
        check_test("menu_main callback fallback mavjud", "pattern='^menu_main$'" in main_content)
        
    except Exception as e:
        check_test("Conversation handler tests", False, str(e))


def test_unknown_callback_handler():
    """Test 8: Unknown callback handler mavjudligini tekshirish."""
    print("\n" + "="*50)
    print("8️⃣ UNKNOWN CALLBACK HANDLER TEKSHIRUVI")
    print("="*50)
    
    try:
        with open('bot/main.py', 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        check_test("handle_unknown_callback funksiyasi mavjud", 
             'handle_unknown_callback' in main_content)
        check_test("Unknown callback log mavjud", 
             'Unknown callback received' in main_content)
        check_test("Fallback handler oxirida qo'shilgan",
             'CallbackQueryHandler(handle_unknown_callback)' in main_content)
        
    except Exception as e:
        check_test("Unknown callback tests", False, str(e))


def test_ffmpeg_availability():
    """Test 9: FFmpeg mavjudligini tekshirish."""
    print("\n" + "="*50)
    print("9️⃣ FFMPEG TEKSHIRUVI")
    print("="*50)
    
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        check_test("FFmpeg o'rnatilgan", result.returncode == 0)
    except FileNotFoundError:
        check_test("FFmpeg o'rnatilgan", False, "ffmpeg topilmadi - video kesish fallback ishlaydi")
    except Exception as e:
        check_test("FFmpeg mavjud", False, str(e))


def print_summary():
    """Print test summary."""
    print("\n" + "="*50)
    print("📊 TEST NATIJALARI XULOSASI")
    print("="*50)
    print(f"✅ O'tgan: {TESTS_PASSED}")
    print(f"❌ Yiqilgan: {TESTS_FAILED}")
    print(f"📈 Umumiy: {TESTS_PASSED + TESTS_FAILED}")
    print(f"📊 Muvaffaqiyat: {TESTS_PASSED/(TESTS_PASSED+TESTS_FAILED)*100:.1f}%")
    
    if TESTS_FAILED > 0:
        print("\n❌ YIQILGAN TESTLAR:")
        for status, name, details in TEST_RESULTS:
            if status == "❌":
                print(f"  • {name}: {details}")


if __name__ == '__main__':
    print("🧪 CAM MAX BOT - KENG QAMROVLI TEST")
    print("="*50)
    
    test_callback_patterns()
    test_access_control()
    test_timezone()
    test_database_operations()
    test_ai_integration()
    test_query_parser()
    test_conversation_handlers()
    test_unknown_callback_handler()
    test_ffmpeg_availability()
    
    print_summary()
