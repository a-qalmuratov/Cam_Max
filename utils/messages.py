"""
Uliwmaliq til fayli - Barliq bot textleri usi jerde.

Ozgertiw ushin tomendegilerdi ozgerttirin.
"""


class Messages:
    """Barliq bot xabarlari - Qaraqalpaq tilinde."""
    
    # ==========================================
    # ULUWMALIQ
    # ==========================================
    
    BOT_NAME = "CAM MAX PRO"
    BOT_DESCRIPTION = "AI Video Baqlaw Sistemasi"
    
    # Tuymeler
    BTN_BACK = "« Arqaga"
    BTN_MAIN_MENU = "« Bas Menyu"
    BTN_CANCEL = "❌ Biykarlaw"
    BTN_SAVE = "💾 Saqlaw"
    BTN_DELETE = "🗑️ Oshiriw"
    BTN_REFRESH = "🔄 Janalaw"
    BTN_RETRY = "🔄 Qayta Uriniw"
    
    # Status
    STATUS_ACTIVE = "Aktiv"
    STATUS_INACTIVE = "Oshirilgen"
    STATUS_ONLINE = "ONLINE"
    STATUS_OFFLINE = "OFFLINE"
    
    # Qatellikler
    ERROR_GENERAL = "❌ Qatelik juz berdi"
    ERROR_USER_NOT_FOUND = "❌ Paydalanuwshi tawilmadi!"
    ERROR_CAMERA_NOT_FOUND = "❌ Kamera tawilmadi!"
    ERROR_NOT_YOUR_CAMERA = "❌ Bul kamera sizge tiyisli emes!"
    ERROR_CONNECTION = "❌ Baylanis qateligi"
    
    # Natiyjeli
    SUCCESS = "✅ Natiyjeli!"
    
    # ==========================================
    # Reg ten otiw
    # ==========================================
    
    REG_WELCOME_TITLE = "CAM MAX PRO"
    REG_WELCOME_SUBTITLE = "AI Video Kuzatuv Tizimi"
    REG_WELCOME_TEXT = "Xosh kelipsiz! sistemaga kiriw ushin reg ten otin."
    REG_ENTER_NAME = "Iltimas, atinizdi jazin:"
    REG_NAME_EXAMPLE = "Misal: Azamat Qalmuratov"
    
    REG_ENTER_PHONE = "Telefon nomiringizdi jazin:"
    REG_PHONE_FORMAT = "+998 XX XXX XX XX"
    REG_PHONE_EXAMPLE = "Misal: +998901234567"
    REG_PHONE_INVALID = "❌ Qate format! +998 baslanin."
    
    REG_ENTER_CODE = "SMS kod jiberildi!"
    REG_CODE_SENT_TO = "Kod jiberildi:"
    REG_CODE_EXPIRES = "Kod 5 minut amal etedi"
    REG_CODE_ATTEMPTS = "urinis qaldi"
    REG_CODE_INVALID = "❌ Qate kod!"
    REG_CODE_EXPIRED = "❌ Kod muddeti otti!"
    
    REG_SUCCESS = "Qutliqlaymiz!"
    REG_SUCCESS_TEXT = "Siz reg ten ottiniz!"
    REG_ALREADY_REGISTERED = "Siz allaqashan reg ten otkensiz!"
    REG_CANCELLED = "❌ Reg ten otiw biykar etildi."
    
    # ==========================================
    # TIYKARGI MENYU
    # ==========================================
    
    MENU_TITLE = "📋 TIYKARGI MENYU"
    MENU_WELCOME = "Xosh kelipsiz"
    MENU_SELECT_ACTION = "Amaldi tanlang:"
    
    # Menyu tugmalari
    MENU_BTN_CAMERAS = "📹 Kameralardi Basqariw"
    MENU_BTN_VIEW = "👁️ Kameralardi Koriw"
    MENU_BTN_AI = "🧠 AI Video izlew"
    MENU_BTN_STATS = "📊 Statistika"
    MENU_BTN_SETTINGS = "⚙️ Duzetpeler"
    
    # Statistika
    MENU_CAMERAS_COUNT = "Kameralar"
    MENU_ACTIVE = "Aktiv"
    
    # ==========================================
    # KAMERA BOSHQARUWI
    # ==========================================
    
    CAM_LIST_TITLE = "📹 KAMERALAR"
    CAM_NO_CAMERAS = "📭 Eshqanday kamera joq"
    CAM_ADD_FIRST = "Birinshi kamerangizdi qosin!"
    CAM_TOTAL = "Jami"
    CAM_CAMERA = "kamera"
    
    # Kamera Tuymeleri
    CAM_BTN_ADD = "➕ Jana Kamera Qosiw"
    CAM_BTN_ADD_SHORT = "➕ Jana Kamera"
    CAM_BTN_VIEW = "📹 Kamerani Ko'riw"
    CAM_BTN_SNAPSHOT = "📸 Hozirgi suwreti"
    CAM_BTN_ARCHIVE = "📹 Video Arxiv"
    CAM_BTN_SETTINGS = "⚙️ Duzetpeler"
    CAM_BTN_DELETE = "🗑️ Oshiriw"
    CAM_BTN_ON = "▶️ Jagiw"
    CAM_BTN_OFF = "⏹️ O'shiriw"
    
    # Kamera detallari
    CAM_STATUS = "Status"
    CAM_IP = "IP"
    CAM_PORT = "Port"
    CAM_LOGIN = "Login"
    CAM_PASSWORD = "Parol"
    CAM_SELECT_ACTION = "Amaldi tanlan:"
    
    # Kamera qosiw wizard
    CAM_ADD_STEP = "JANA KAMERA"
    CAM_ENTER_NAME = "Kamera atin jazin:"
    CAM_NAME_EXAMPLE1 = "Misal: Uleken zal"
    CAM_NAME_EXAMPLE2 = "Misal: Kassa"
    CAM_NAME_EXAMPLE3 = "Misal: Kiriw"
    CAM_NAME_TOO_SHORT = "❌ At qisqa! Keminde 2 belgi jazin."
    
    CAM_ENTER_IP = "IP manzilni jazin:"
    CAM_IP_EXAMPLE1 = "Misal: 192.168.1.100"
    CAM_IP_EXAMPLE2 = "Misal: 10.0.0.50"
    CAM_IP_INVALID = "❌ Qate IP format!"
    
    CAM_ENTER_PORT = "RTSP portni jazin:"
    CAM_PORT_DEFAULT = "Standart: 554"
    CAM_PORT_OTHER = "Basqa: 8554, 5554"
    CAM_PORT_HINT = "💡 Enter basin = 554"
    CAM_PORT_INVALID = "❌ Qate port! 1-65535 oralig'inda jazin."
    
    CAM_ENTER_USERNAME = "Paydalanuwshi atin jazin:"
    CAM_USERNAME_DEFAULT = "Standart: admin"
    CAM_USERNAME_HINT = "💡 Enter basin = admin"
    
    CAM_ENTER_PASSWORD = "Paroldi jazin:"
    CAM_PASSWORD_SECURE = "🔒 Parol qawipsiz saqlanadi"
    CAM_PASSWORD_EMPTY = "❌ Parol bos qaliwi mumkin emes!"
    
    CAM_TESTING = "🔄 TEKSERILMEKTE..."
    CAM_TESTING_TEXT = "⏳ Kameraga baylanis tekserilmekte..."
    
    CAM_ADDED_SUCCESS = "✅ KAMERA QOSILDI!"
    CAM_ONLINE_READY = "🟢 Kamera ONLINE"
    
    CAM_CONNECTION_ERROR = "⚠️ BAYLANIS QATESI"
    CAM_CONNECTION_FAILED = "❌ Kameraga jalganip bolmadi"
    CAM_CHECK_IP = "• IP manzil tuwri"
    CAM_CHECK_PORT = "• Port tuwri"
    CAM_CHECK_CREDENTIALS = "• Login/parol tuwri"
    CAM_CHECK_NETWORK = "• Kamera linyada isleptur"
    
    # Kamera oshiriw
    CAM_DELETE_CONFIRM_TITLE = "⚠️ OSHIRIW?"
    CAM_DELETE_WARNING = "⚠️ Barliq arxivler ham oshiriledi!"
    CAM_DELETE_IRREVERSIBLE = "Bu amaldi qaytarip bolmaydi."
    CAM_BTN_DELETE_CONFIRM = "✅ AWA, Oshiriw"
    CAM_BTN_DELETE_CANCEL = "❌ Yaq"
    CAM_DELETED = "✅ Kamera o'shirildi!"
    
    CAM_TURNED_ON = "✅ Kamera Jag'ildi!"
    CAM_TURNED_OFF = "⏹️ Kamera o'shirildi!"
    
    # ==========================================
    # VIDEO KO'RIW
    # ==========================================
    
    VIEW_TITLE = "👁️ VIDEO KO'RIW"
    VIEW_SELECT_MODE = "Rejimdi tanlan:"
    
    VIEW_BTN_REALTIME = "🔴 Real-time Koriw"
    VIEW_BTN_ARCHIVE = "📅 Waqt Boyinsha Koriw"
    VIEW_BTN_BOOKMARKS = "⭐ Qiziqli Momentlar"
    VIEW_BTN_DOWNLOAD = "📥 Juklep Aliw"
    
    # Real-time
    VIEW_REALTIME_TITLE = "🔴 REAL-TIME"
    VIEW_SELECT_CAMERA = "Kamerani tanlan:"
    VIEW_NO_CAMERAS = "📭 Kamera joq!"
    VIEW_ADD_CAMERA_FIRST = "Aldin kamera qosin."
    
    VIEW_CONNECTING = "⏳ Kameraga baylanbaqta..."
    VIEW_CAPTURING = "⏳ Suwretke tusirilip atir..."
    VIEW_PHOTO_SENT = "✅ Suwret jiberildi"
    
    VIEW_OFFLINE = "❌ OFFLINE"
    VIEW_CAMERA_NOT_CONNECTED = "Kamera jalganbagan yaki offline."
    
    # Arxiv
    VIEW_ARCHIVE_TITLE = "📅 Waqt Tanlaw"
    VIEW_QUICK_SELECT = "Tez tanlaw:"
    VIEW_BTN_10MIN = "⏱️ 10 minut"
    VIEW_BTN_1HOUR = "⏰ 1 saat"
    VIEW_BTN_TODAY = "📆 Bugun"
    VIEW_BTN_YESTERDAY = "📆 Keshe"
    VIEW_BTN_CUSTOM = "✍️ Aniq waqtti jazin"
    
    VIEW_LAST_10MIN = "Songi 10 minut"
    VIEW_LAST_1HOUR = "Songi 1 saat"
    
    VIEW_SELECT_CAM_TITLE = "📹 KAMERA TANLAW"
    VIEW_PREPARING = "⏳ TAYARLANIP ATIR"
    VIEW_VIDEO_PROCESSING = "⏳ Video qayta islenip atir..."
    VIEW_VIDEO_SENT = "✅ Video jiberildi"
    VIEW_ARCHIVE_EMPTY = "📭 ARXIV BOS"
    VIEW_NO_VIDEO_IN_RANGE = "Bul waqt oralig'inda video joq."
    VIEW_TURN_ON_RECORDING = "💡 Video jaziw ushin kamerani ON jagdayina otkerin."
    
    # Sevimlilar
    VIEW_BOOKMARKS_TITLE = "⭐ Qiziqlilar"
    VIEW_NO_BOOKMARKS = "📭 Saqlangan momentlar joq."
    VIEW_BOOKMARK_HINT = "Real-time koriwde ⭐ Saqlaw tuymesin basin."
    VIEW_BTN_SAVE_BOOKMARK = "⭐ Saqlaw"
    
    # Juklep aliw
    VIEW_DOWNLOAD_TITLE = "📥 Juklep Aliw"
    VIEW_DOWNLOAD_HINT = "Videoni juklep aliw ushin aldin 📅 Waqt boyinsha koriw arqali kerikli videoni tanlan."
    VIEW_BTN_SELECT_TIME = "📅 Waqt Tanlaw"
    
    # ==========================================
    # AI IZLEW
    # ==========================================
    
    AI_TITLE = "🧠 AI JARDEMSHI"
    AI_GREETING = "🤖 Salem! Men sizdin AI jardemshinizben."
    AI_ASK_ANYTHING = "💬 Mag'an qálegen sorawin'izdi bering:"
    AI_EXAMPLES = "📝 Misali:"
    AI_EXAMPLE1 = "\"Stol ustidagi qizil sumka qayerde?\""
    AI_EXAMPLE2 = "\"Keshe kim kirdi?\""
    AI_EXAMPLE3 = "\"1-kamerada hazir kimler bar?\""
    AI_EXAMPLE4 = "\"Aq ko'ylekli adam qayerge ketti?\""
    AI_HINT = "💡 Eger ma'lumat jetarli bolmasa, men sizden sorap alaman!"
    
    AI_THINKING = "🤔 O'ylanbaqta..."
    AI_QUESTION_TITLE = "🤖 AI SORAWI"
    AI_ANSWER_TITLE = "🤖 AI JAWABI"
    AI_WRITE_ANSWER = "💬 Jawabin'izdi jazin:"
    AI_ASK_MORE = "💬 Boshqa soraw bering yaki /menu"
    AI_BTN_NEW_QUESTION = "🔄 Jana Soraw"
    
    AI_SEARCHING = "🔍 Barliq kameralardan izlenbekte:"
    AI_PLEASE_WAIT = "⏳ Iltimas kutin..."
    AI_FOUND = "✅ TABILDI!"
    AI_NOT_FOUND = "📭 TABILMADI"
    AI_CAMERAS_CHECKED = "ta kamerada tekserildi"
    AI_TRY_ANOTHER = "💡 Boshqa so'raw menen urinip ko'rin yaki video arxivinan izlewdi tanlan."
    AI_BTN_SEARCH_ARCHIVE = "📅 Arxivdan izlew"
    AI_BTN_SEARCH_AGAIN = "🔄 Qayta Izlew"
    
    AI_ARCHIVE_TITLE = "🔍 ARXIV IZLEWI"
    AI_ARCHIVE_NOT_READY = "⚠️ Video arxiv isitemasi ele toliq iske tusirilmegen."
    AI_USE_REALTIME = "💡 \"Hazir qayerde?\" deb soran real-time izlew ushin."
    AI_BTN_REALTIME_SEARCH = "🔴 Real-time Izlew"
    
    AI_CANCELLED = "❌ AI menen chat jawildi."
    
    # ==========================================
    # STATISTIKA
    # ==========================================
    
    STATS_TITLE = "📊 STATISTIKA"
    STATS_TODAY = "BUGUN"
    STATS_PEOPLE = "Adamlar"
    STATS_VEHICLES = "Mashinalar"
    STATS_OBJECTS = "Koshirilgen"
    STATS_PEAK_HOURS = "ENG BAND WAQIT"
    STATS_CAMERAS = "KAMERALAR"
    STATS_TOTAL = "Jami"
    STATS_ACTIVE = "Aktiv"
    STATS_INACTIVE = "Oshirilgen"
    
    STATS_BTN_WEEKLY = "📈 Haptelik Esabat"
    STATS_BTN_CAMERAS = "📊 Kamera Analitika"
    STATS_BTN_ALERTS = "🔔 Bildirtpeler"
    STATS_BTN_EXPORT = "📥 PDF Juklep Aliw"
    
    STATS_WEEKLY_TITLE = "📈 Haptelik Esabat"
    STATS_WEEKLY_TREND = "Haptelik trend"
    STATS_DAILY_BREAKDOWN = "KUNLIK BREAKDOWN"
    STATS_WARNINGS_TITLE = "ESKERTIWLER"
    STATS_SUSPICIOUS = "dana kozge taslangan hareket"
    STATS_UNKNOWN = "dana belgisiz adam"
    STATS_TOP_EVENTS = "TOP JAGDAYLAR"
    STATS_BTN_GRAPH = "📊 Grafik Ko'riw"
    
    # ==========================================
    # Sazlawlar
    # ==========================================
    
    SETTINGS_TITLE = "⚙️ Sazlawlar"
    SETTINGS_SELECT = "Sazlawlar bo'limin tanlan:"
    
    SETTINGS_BTN_PROFILE = "👤 Profil"
    SETTINGS_BTN_NOTIFICATIONS = "🔔 Bildirtpeler"
    SETTINGS_BTN_SECURITY = "🔐 Qawipsizlik"
    SETTINGS_BTN_ARCHIVE = "💾 Arxiv"
    SETTINGS_BTN_LANGUAGE = "🌍 Til"
    SETTINGS_BTN_HELP = "❓ Jardem"
    
    # Profil
    SETTINGS_PROFILE_TITLE = "👤 Profil"
    SETTINGS_NAME = "Ati"
    SETTINGS_PHONE = "Tel"
    SETTINGS_REGISTERED = "Dizim"
    SETTINGS_CAMERAS = "Kameralar"
    SETTINGS_STORAGE = "Storage"
    SETTINGS_PLAN = "Rejim"
    SETTINGS_BTN_EDIT_NAME = "✏️ Atin O'zgertiriw"
    SETTINGS_BTN_EDIT_PHONE = "📱 Telefon O'zgerttiriw"
    
    # Bildirtpeler
    SETTINGS_NOTIF_TITLE = "🔔 Bildirtpeler"
    SETTINGS_EVENTS = "JAGDAYLAR"
    SETTINGS_TIME = "WAQIT"
    SETTINGS_CHANNEL = "KANAL"
    SETTINGS_BTN_TIME = "⏰ Vaqt O'zgerttiriw"
    
    # Qawipsizlik
    SETTINGS_SECURITY_TITLE = "🔐 Qawipsizlik"
    SETTINGS_2FA = "2FA"
    SETTINGS_ENABLED = "Enabled"
    SETTINGS_IP_WHITELIST = "IP Whitelist"
    SETTINGS_ACTIVITY_LOGS = "Activity Logs"
    SETTINGS_ACTIVE_SESSIONS = "AKTIV SESSIYALAR"
    SETTINGS_THIS_DEVICE = "Usı qurilma"
    SETTINGS_NOW = "Házir"
    SETTINGS_BTN_CHANGE_PASSWORD = "🔒 Paroldi O'zgerttiriw"
    SETTINGS_BTN_IP_PERMISSIONS = "🛡️ IP Ruxsatlar"
    SETTINGS_BTN_ACTIVITY = "📋 Aktivlikler"
    SETTINGS_BTN_LOGOUT_ALL = "🚪 Barliq Sessiyalardan Shıg'ıw"
    
    # Arxiv
    SETTINGS_ARCHIVE_TITLE = "💾 ARXIV"
    SETTINGS_STORAGE_SETTINGS = "SAQLAW SAZLAMALARI"
    SETTINGS_RETENTION = "Saqlaw muddeti"
    SETTINGS_QUALITY = "Sapa"
    SETTINGS_FORMAT = "Format"
    SETTINGS_STORAGE_STATUS = "STORAGE"
    SETTINGS_TOTAL_STORAGE = "Jami"
    SETTINGS_FREE_SPACE = "Bos orin"
    SETTINGS_BTN_RETENTION = "📅 Saqlaw Muddeti"
    SETTINGS_BTN_QUALITY = "📺 Sapa O'zgerttiriw"
    SETTINGS_BTN_CLEANUP = "🗑️ Eski Arxivlerdi Tazalaw"
    
    # Til
    SETTINGS_LANGUAGE_TITLE = "🌍 TIL"
    SETTINGS_SELECT_LANGUAGE = "Tilni tanlang:"
    SETTINGS_LANG_UZ = "🇺🇿 O'zbek tili"
    SETTINGS_LANG_RU = "🇷🇺 Русский"
    SETTINGS_LANG_EN = "en English"
    
    # Jardem
    SETTINGS_HELP_TITLE = "❓ JARDEM"
    SETTINGS_COMMANDS = "BUYRUQLAR"
    SETTINGS_CAPABILITIES = "QABILYETLER"
    SETTINGS_CONTACT = "BAYLANIS"
    SETTINGS_BTN_GUIDE = "📖 Toliq Qollanba"
    
    # ==========================================
    # EKSPORT
    # ==========================================
    
    EXPORT_TITLE = "📥 EKSPORT"
    EXPORT_SELECT_TYPE = "Eksport turin tanlan:"
    EXPORT_BTN_VIDEO = "📹 Video Eksport"
    EXPORT_BTN_STATS = "📊 Statistika Eksport"
    EXPORT_BTN_EVENTS = "📋 Bolgan waqiyalar listi"
    
    EXPORT_VIDEO_TITLE = "📹 VIDEO EKSPORT"
    EXPORT_FORMAT = "FORMAT"
    EXPORT_QUALITY = "SAPA"
    EXPORT_BTN_HD = "🔷 HD 1080p"
    EXPORT_BTN_SD = "🔶 SD 720p"
    EXPORT_BTN_LOW = "⚪ Low 480p"
    
    EXPORT_PREPARING = "⏳ TAYYARLANBAQTA"
    EXPORT_NOT_READY = "⚠️ Video eksport sistemasi hozirshe islep shig'ilmatda."
    EXPORT_USE_VIEW = "💡 Hozirshe individual video koriw arqali juklep aliwiniz mumkin."
    
    EXPORT_STATS_REPORT = "📊 Statistika esabati"
    EXPORT_SENT = "✅ JIBERILDI"
    EXPORT_FILE_SENT = "📊 Statistika fayli jiberildi!"
    
    # ==========================================
    # TEZ HAREKETLER
    # ==========================================
    
    QUICK_TITLE = "⚡ TEZ HAREKETLER"
    QUICK_RECENT_CAMERAS = "📹 Oxirgi kameralar:"
    QUICK_TIME = "TEZ HAREKET VAQTI"
    QUICK_AI = "TEZ AI"


# Global instance
msg = Messages()
