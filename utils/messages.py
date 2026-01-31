"""
Ulıwma til faylı - Barlıq bot tekstleri usı jerde.

Ózgertiw ushın tómendegilerdi ózgertirin.
"""


class Messages:
    """Barlıq bot xabarlari - Qaraqalpaq tilinde."""
    
    # ==========================================
    # ULIWMA
    # ==========================================
    
    BOT_NAME = "CAM MAX PRO"
    BOT_DESCRIPTION = "AI Video Baqlıw Sisteması"
    
    # Túymeler
    BTN_BACK = "« Artqa"
    BTN_MAIN_MENU = "« Bas Menyu"
    BTN_CANCEL = "❌ Biykarlaw"
    BTN_SAVE = "💾 Saqlaw"
    BTN_DELETE = "🗑️ Óshiriw"
    BTN_REFRESH = "🔄 Janalaw"
    BTN_RETRY = "🔄 Qayta urınıw"
    
    # Status
    STATUS_ACTIVE = "Aktiv"
    STATUS_INACTIVE = "Óshirilgen"
    STATUS_ONLINE = "ONLINE"
    STATUS_OFFLINE = "OFFLINE"
    
    # Qatelikler
    ERROR_GENERAL = "❌ Qatelik júz berdi"
    ERROR_USER_NOT_FOUND = "❌ Paydalanıwshı tabılmadı!"
    ERROR_CAMERA_NOT_FOUND = "❌ Kamera tabılmadı!"
    ERROR_NOT_YOUR_CAMERA = "❌ Bul kamera sizge tiyisli emes!"
    ERROR_CONNECTION = "❌ Baylaniw qatesi"
    
    # Nátiyje
    SUCCESS = "✅ Nátiyje!"
    
    # ==========================================
    # DIZIMNEN ÓTIW
    # ==========================================
    
    REG_WELCOME_TITLE = "CAM MAX PRO"
    REG_WELCOME_SUBTITLE = "AI Video Baqlıw Sisteması"
    REG_WELCOME_TEXT = "Xosh kelipsiz! Sistemaga kiriw ushın dizimnen ótin."
    REG_ENTER_NAME = "Iltimas, atınızdi jazın:"
    REG_NAME_EXAMPLE = "Mısalı: Azamat Qalmuratov"
    
    REG_ENTER_PHONE = "Telefon nomeriňizdi jazın:"
    REG_PHONE_FORMAT = "+998 XX XXX XX XX"
    REG_PHONE_EXAMPLE = "Mısalı: +998901234567"
    REG_PHONE_INVALID = "❌ Qate format! +998 menen baslansin basqa formatlar kiyin qosiladi."
    
    REG_ENTER_CODE = "SMS kod jiberildi!"
    REG_CODE_SENT_TO = "Kod jiberildi:"
    REG_CODE_EXPIRES = "Kod 5 minutqa amel etedi"
    REG_CODE_ATTEMPTS = "urınıw qaldı"
    REG_CODE_INVALID = "❌ Qate kod!"
    REG_CODE_EXPIRED = "❌ Kod waqtı ótip ketti!"
    
    REG_SUCCESS = "Qutlıqlaymız!"
    REG_SUCCESS_TEXT = "Siz dizimnen óttiniz!"
    REG_ALREADY_REGISTERED = "Siz allaqashan dizimnen ótkensiz!"
    REG_CANCELLED = "❌ Dizimnen ótiw biykar etildi."
    
    # ==========================================
    # BAS MENYU
    # ==========================================
    
    MENU_TITLE = "📋 BAS MENYU"
    MENU_WELCOME = "Xosh kelipsiz"
    MENU_SELECT_ACTION = "Háreketti tanlań:"
    
    # Menyu túymeleri
    MENU_BTN_CAMERAS = "📹 Kameralar basqarıwı"
    MENU_BTN_VIEW = "👁️ Kameralardı kóriw"
    MENU_BTN_AI = "🧠 AI Video izlew"
    MENU_BTN_STATS = "📊 Statistika"
    MENU_BTN_SETTINGS = "⚙️ Sazlawlar"
    
    # Statistika
    MENU_CAMERAS_COUNT = "Kameralar"
    MENU_ACTIVE = "Aktiv"
    
    # ==========================================
    # KAMERA BASQARIWI
    # ==========================================
    
    CAM_LIST_TITLE = "📹 KAMERALAR"
    CAM_NO_CAMERAS = "📭 Hesh qanday kamera joq"
    CAM_ADD_FIRST = "Birinshi kameranızdı qosıń!"
    CAM_TOTAL = "Jámi"
    CAM_CAMERA = "kamera"
    
    # Kamera Túymeleri
    CAM_BTN_ADD = "➕ Jańa Kamera Qosıw"
    CAM_BTN_ADD_SHORT = "➕ Jańa Kamera"
    CAM_BTN_VIEW = "📹 Kameranı Kóriw"
    CAM_BTN_SNAPSHOT = "📸 Házirgi súwret"
    CAM_BTN_ARCHIVE = "📹 Video Arxiv"
    CAM_BTN_SETTINGS = "⚙️ Sazlawlar"
    CAM_BTN_DELETE = "🗑️ Óshiriw"
    CAM_BTN_ON = "▶️ Qosıw"
    CAM_BTN_OFF = "⏹️ Óshiriw"
    
    # Kamera detallari
    CAM_STATUS = "Status"
    CAM_IP = "IP"
    CAM_PORT = "Port"
    CAM_LOGIN = "Login"
    CAM_PASSWORD = "Parol"
    CAM_SELECT_ACTION = "Háreketti tanlań:"
    
    # Kamera qosıw wizard
    CAM_ADD_STEP = "JAŃA KAMERA"
    CAM_ENTER_NAME = "Kamera atın jazın:"
    CAM_NAME_EXAMPLE1 = "Mısalı: Úlken zal"
    CAM_NAME_EXAMPLE2 = "Mısalı: Kassa"
    CAM_NAME_EXAMPLE3 = "Mısalı: Kiriw"
    CAM_NAME_TOO_SHORT = "❌ At qısqa! Kem degende 2 belgi jazın."
    
    CAM_ENTER_IP = "IP mánzildi jazın:"
    CAM_IP_EXAMPLE1 = "Mısalı: 192.168.1.100"
    CAM_IP_EXAMPLE2 = "Mısalı: 10.0.0.50"
    CAM_IP_INVALID = "❌ Qate IP format!"
    
    CAM_ENTER_PORT = "RTSP porttı jazın:"
    CAM_PORT_DEFAULT = "Standart: 554"
    CAM_PORT_OTHER = "Basqa: 8554, 5554"
    CAM_PORT_HINT = "💡 Enter basıń = 554"
    CAM_PORT_INVALID = "❌ Qate port! 1-65535 aralıǵında jazın."
    
    CAM_ENTER_USERNAME = "Paydalanıwshı atın jazın:"
    CAM_USERNAME_DEFAULT = "Standart: admin"
    CAM_USERNAME_HINT = "💡 Enter basıń = admin"
    
    CAM_ENTER_PASSWORD = "Paroldı jazın:"
    CAM_PASSWORD_SECURE = "🔒 Parol qáwipsiz saqlanadi"
    CAM_PASSWORD_EMPTY = "❌ Parol bos bolıwı múmkin emes!"
    
    CAM_TESTING = "🔄 TEKSERILMEKTE..."
    CAM_TESTING_TEXT = "⏳ Kameraga baylaniw tekserilmekte..."
    
    CAM_ADDED_SUCCESS = "✅ KAMERA QOSILDI!"
    CAM_ONLINE_READY = "🟢 Kamera ONLINE"
    
    CAM_CONNECTION_ERROR = "⚠️ BAYLANIW QATESI"
    CAM_CONNECTION_FAILED = "❌ Kameraga jalǵanıp bolmadı"
    CAM_CHECK_IP = "• IP mánzil durıs"
    CAM_CHECK_PORT = "• Port durıs"
    CAM_CHECK_CREDENTIALS = "• Login/parol durıs"
    CAM_CHECK_NETWORK = "• Kamera onlayn isleydi"
    
    # Kamera óshiriw
    CAM_DELETE_CONFIRM_TITLE = "⚠️ ÓSHIRIW?"
    CAM_DELETE_WARNING = "⚠️ Barlıq arxivler de óshiriledi!"
    CAM_DELETE_IRREVERSIBLE = "Bul háreketti qaytarıp bolmaydı."
    CAM_BTN_DELETE_CONFIRM = "✅ AWA, Óshiriw"
    CAM_BTN_DELETE_CANCEL = "❌ Yaq"
    CAM_DELETED = "✅ Kamera óshirildi!"
    
    CAM_TURNED_ON = "✅ Kamera qosıldı!"
    CAM_TURNED_OFF = "⏹️ Kamera óshirildi!"
    
    # ==========================================
    # VIDEO KÓRIW
    # ==========================================
    
    VIEW_TITLE = "👁️ VIDEO KÓRIW"
    VIEW_SELECT_MODE = "Rejimdi tanlań:"
    
    VIEW_BTN_REALTIME = "🔴 Real-time Kóriw"
    VIEW_BTN_ARCHIVE = "📅 Waqıt Boyınsha Kóriw"
    VIEW_BTN_BOOKMARKS = "⭐ Qızıqlı Momentler"
    VIEW_BTN_DOWNLOAD = "📥 Júklep Alıw"
    
    # Real-time
    VIEW_REALTIME_TITLE = "🔴 REAL-TIME"
    VIEW_SELECT_CAMERA = "Kameranı tanlań:"
    VIEW_NO_CAMERAS = "📭 Kamera joq!"
    VIEW_ADD_CAMERA_FIRST = "Aldın kamera qosıń."
    
    VIEW_CONNECTING = "⏳ Kameraga baylanbaqta..."
    VIEW_CAPTURING = "⏳ Súwretke túsirilip atır..."
    VIEW_PHOTO_SENT = "✅ Súwret jiberildi"
    
    VIEW_OFFLINE = "❌ OFFLINE"
    VIEW_CAMERA_NOT_CONNECTED = "Kamera jalǵanbaǵan yamasa offline."
    
    # Arxiv
    VIEW_ARCHIVE_TITLE = "📅 Waqıt Tanlaw"
    VIEW_QUICK_SELECT = "Tez tanlaw:"
    VIEW_BTN_10MIN = "⏱️ 10 minut"
    VIEW_BTN_1HOUR = "⏰ 1 saat"
    VIEW_BTN_TODAY = "📆 Búgin"
    VIEW_BTN_YESTERDAY = "📆 Keshe"
    VIEW_BTN_CUSTOM = "✍️ Anıq waqıttı jazın"
    
    VIEW_LAST_10MIN = "Soŋǵı 10 minut"
    VIEW_LAST_1HOUR = "Soŋǵı 1 saat"
    
    VIEW_SELECT_CAM_TITLE = "📹 KAMERA TANLAW"
    VIEW_PREPARING = "⏳ TAYARLANIP ATIR"
    VIEW_VIDEO_PROCESSING = "⏳ Video qayta islenip atır..."
    VIEW_VIDEO_SENT = "✅ Video jiberildi"
    VIEW_ARCHIVE_EMPTY = "📭 ARXIV BOS"
    VIEW_NO_VIDEO_IN_RANGE = "Bul waqıt aralıǵında video joq."
    VIEW_TURN_ON_RECORDING = "💡 Video jazıw ushın kameranı ON halına ótkerin."
    
    # Sewimlilar
    VIEW_BOOKMARKS_TITLE = "⭐ Qızıqlılar"
    VIEW_NO_BOOKMARKS = "📭 Saqlangan momentler joq."
    VIEW_BOOKMARK_HINT = "Real-time kóriwde ⭐ Saqlaw túymesin basın."
    VIEW_BTN_SAVE_BOOKMARK = "⭐ Saqlaw"
    
    # Júklep alıw
    VIEW_DOWNLOAD_TITLE = "📥 Júklep Alıw"
    VIEW_DOWNLOAD_HINT = "Videoni júklep alıw ushın aldın 📅 Waqıt boyınsha kóriw arqalı kerekli videoni tanlań."
    VIEW_BTN_SELECT_TIME = "📅 Waqıt Tanlaw"
    
    # ==========================================
    # AI IZLEW
    # ==========================================
    
    AI_TITLE = "🧠 AI JÁRDEMSHI"
    AI_GREETING = "🤖 Salem! Men siziń AI járdemshińizben."
    AI_ASK_ANYTHING = "💬 Maǵan qálegen sorawıńızdı beriń:"
    AI_EXAMPLES = "📝 Mısalı:"
    AI_EXAMPLE1 = "\"1-kamerada hozir nechta odam bor?\""
    AI_EXAMPLE2 = "\"Tashqaridagi oq malibu soat nechida keldi?\""
    AI_HINT = "💡 Bizdin AI hazirshe tek uzbek tilin tusinedi sol sebebpten sorawlardi ozbekshe jazin\nEger maǵlıwmat jeterli bolmasa, men sizden sorap alaman!"
    
    AI_THINKING = "🤔 Oylanbaqta..."
    AI_QUESTION_TITLE = "🤖 AI SORAWI"
    AI_ANSWER_TITLE = "🤖 AI JAWABI"
    AI_WRITE_ANSWER = "💬 Jawabıńızdı jazın:"
    AI_ASK_MORE = "💬 Basqa soraw beriń yamasa /menu"
    AI_BTN_NEW_QUESTION = "🔄 Jańa Soraw"
    
    AI_SEARCHING = "🔍 Barlıq kameralardan izlenbekte:"
    AI_PLEASE_WAIT = "⏳ Iltimas kútiń..."
    AI_FOUND = "✅ TABÍLDI!"
    AI_NOT_FOUND = "📭 TABÍLMADI"
    AI_CAMERAS_CHECKED = " kamera tekserildi"
    AI_TRY_ANOTHER = "💡 Basqa soraw menen urınıp kóriń yamasa video arxivinen izlewdi tanlań."
    AI_BTN_SEARCH_ARCHIVE = "📅 Arxivten izlew"
    AI_BTN_SEARCH_AGAIN = "🔄 Qayta Izlew"
    
    AI_ARCHIVE_TITLE = "🔍 ARXIV IZLEWI"
    AI_ARCHIVE_NOT_READY = "⚠️ Video arxiv sisteması ele tolıq iske túsirilmegen."
    AI_USE_REALTIME = "💡 \"Hozir qayerda?\" dep sorań real-time izlew ushın."
    AI_BTN_REALTIME_SEARCH = "🔴 Real-time Izlew"
    
    AI_CANCELLED = "❌ AI menen chat jabildi."
    
    # AI API Qatelikleri - Tolıq maǵlıwmat
    AI_ERROR_TITLE = "⚠️ AI SISTEMASI QATELIGI"
    
    AI_ERROR_404_TITLE = "❌ AI MODEL TABÍLMADI (404)"
    AI_ERROR_404_WHAT = """🔍 **NE BOLDI?**
AI model sistemada tabılmadı yamasa qollanbadı."""
    
    AI_ERROR_404_WHY = """💡 **SEBEP NEDE?**
• API model atı qate"""
    
    AI_ERROR_404_FIX = """🔧 **NE QILIW MUMKIN?**
1️⃣ Kútiń, keyin qayta urınıń
2️⃣ Eger durıslanbasa - admin baylanisin 
3️⃣ Waqıtsha AI járdemsiz jumıs islen"""
    
    AI_ERROR_429_TITLE = "⏳ AI ge beriletin sorawlar limitten asipketti (429)"
    AI_ERROR_429_WHAT = """🔍 **NE BOLDI?**
AI sistemasınıń kúnlik sorawlar shegi asıp ketti."""
    
    AI_ERROR_429_WHY = """💡 **SEBEP NEDE?**
• AI ge kóp soraw berildi
• AI rejim limiti"""
    
    AI_ERROR_429_FIX = """🔧 **NE QILIW MUMKIN?**
1️⃣ Kútiń (30-60 minut)
2️⃣ Qayta urınıń"""
    
    AI_ERROR_500_TITLE = "💥 AI SERVER QATELIGI (500)"
    AI_ERROR_500_WHAT = """🔍 **NE BOLDI?**
AI serverinde ishki qatelik júz berdi."""
    
    AI_ERROR_500_WHY = """💡 **SEBEP NEDE?**
• Server waqtinsha islemeydi
• Texnik jumıslar alip barilip atır
• Sistema júklenmesi kóp"""
    
    AI_ERROR_500_FIX = """🔧 **NE QILIW MUMKIN?**
1️⃣ 5-10 minut kútiń  
2️⃣ Qayta urınıń
3️⃣ Problem dawam etse - adminge xabar beriń"""
    
    AI_ERROR_NETWORK_TITLE = "📡 INTERNET BAYLANIW QATESI"
    AI_ERROR_NETWORK_WHAT = """🔍 **NE BOLDI?**
AI serveriga baylana almadıq."""
    
    AI_ERROR_NETWORK_WHY = """💡 **SEBEP NEDE?**
• Internet baylaniw joq yaki tomen
• Wi-Fi/mobil internet óshirilgen
• Server waqtinsha islemeydi"""
    
    AI_ERROR_NETWORK_FIX = """🔧 **NE QILIW MUMKIN?**
1️⃣ Internet baylaniwindi tekseriniń
2️⃣ Wi-Fi/mobil internetti qayta jalǵań
3️⃣ Internet durıslanǵan sań qayta urınıń"""
    
    AI_ERROR_TIMEOUT_TITLE = "⏱️ WAQIT OTTI"    
    AI_ERROR_TIMEOUT_WHAT = """🔍 **NE BOLDI?**
AI ge berilgen sorawdin waqti otipketti (waqit ottip ketti)."""
    
    AI_ERROR_TIMEOUT_WHY = """💡 **SEBEP NEDE?**
• Soraw juda qıyın
• Serverge jukleme tusken
• Internet baylanıw pas"""
    
    AI_ERROR_TIMEOUT_FIX = """🔧 **NE QILIW MUMKIN?**
1️⃣ Sorawındı qısqartıp urınıń
2️⃣ Internet baylaniwın tekseriń"""
    
    AI_ERROR_AUTH_TITLE = "🔐 API KEY QATELIGI"
    AI_ERROR_AUTH_WHAT = """🔍 **NE BOLDI?**
AI API gilti qabıllanbadı."""
    
    AI_ERROR_AUTH_WHY = """💡 **SEBEP NEDE?**
• API key qate yamasa eski
• Key eski
• Sistemada sozlanbaǵan"""
    
    AI_ERROR_AUTH_FIX = """🔧 **NE QILIW MUMKIN?**
1️⃣ Admin tez arada API giltti janalaydi"""
    
    AI_ERROR_UNKNOWN_TITLE = "❌ BELGISIZ QATELIK"
    AI_ERROR_UNKNOWN_WHAT = """🔍 **NE BOLDI?**
Kútilmegen qatelik júz berdi."""
    
    AI_ERROR_UNKNOWN_WHY = """💡 **SEBEP NEDE?**
Anıq sebep belgisiz."""
    
    AI_ERROR_UNKNOWN_FIX = """🔧 **NE QILIW MUMKIN?**
1️⃣ Qayta urınıń
2️⃣ Eger dawam etse - adminge xabar beriń"""

    
    # ==========================================
    # STATISTIKA
    # ==========================================
    
    STATS_TITLE = "📊 STATISTIKA"
    STATS_TODAY = "BÚGIN"
    STATS_PEOPLE = "Adamlar"
    STATS_VEHICLES = "Mashinalar"
    STATS_OBJECTS = "Kóshirilgen"
    STATS_PEAK_HOURS = "EŃ BAND WAQIT"
    STATS_CAMERAS = "KAMERALAR"
    STATS_TOTAL = "Jámi"
    STATS_ACTIVE = "Aktiv"
    STATS_INACTIVE = "Óshirilgen"
    
    STATS_BTN_WEEKLY = "📈 Háptelik Esabat"
    STATS_BTN_CAMERAS = "📊 Kamera Analitika"
    STATS_BTN_ALERTS = "🔔 Bildirpeler"
    STATS_BTN_EXPORT = "📥 PDF Júklep Alıw"
    
    STATS_WEEKLY_TITLE = "📈 Háptelik Esabat"
    STATS_WEEKLY_TREND = "Háptelik trend"
    STATS_DAILY_BREAKDOWN = "KÚNLIK BREAKDOWN"
    STATS_WARNINGS_TITLE = "ESKERTWLER"
    STATS_SUSPICIOUS = "dana gúmanlı háreket"
    STATS_UNKNOWN = "dana belgisiz adam"
    STATS_TOP_EVENTS = "TOP WAQIYALAR"
    STATS_BTN_GRAPH = "📊 Grafikti Kóriw"
    
    # ==========================================
    # SAZLAWLAR
    # ==========================================
    
    SETTINGS_TITLE = "⚙️ Sazlawlar"
    SETTINGS_SELECT = "Sazlawlar bólimin tanlań:"
    
    SETTINGS_BTN_PROFILE = "👤 Profil"
    SETTINGS_BTN_NOTIFICATIONS = "🔔 Bildirpeler"
    SETTINGS_BTN_SECURITY = "🔐 Qáwipsizlik"
    SETTINGS_BTN_ARCHIVE = "💾 Arxiv"
    SETTINGS_BTN_LANGUAGE = "🌍 Til"
    SETTINGS_BTN_HELP = "❓ Járdem"
    
    # Profil
    SETTINGS_PROFILE_TITLE = "👤 Profil"
    SETTINGS_NAME = "Atı"
    SETTINGS_PHONE = "Tel"
    SETTINGS_REGISTERED = "Dizim"
    SETTINGS_CAMERAS = "Kameralar"
    SETTINGS_STORAGE = "Xotira"
    SETTINGS_PLAN = "Rejim"
    SETTINGS_BTN_EDIT_NAME = "✏️ Attı Ózgertiw"
    SETTINGS_BTN_EDIT_PHONE = "📱 Telefondi Ózgertiw"
    
    # Bildirpeler
    SETTINGS_NOTIF_TITLE = "🔔 Bildirpeler"
    SETTINGS_EVENTS = "WAQIYALAR"
    SETTINGS_TIME = "WAQIT"
    SETTINGS_CHANNEL = "KANAL"
    SETTINGS_BTN_TIME = "⏰ Waqıttı Ózgertiw"
    
    # Qáwipsizlik
    SETTINGS_SECURITY_TITLE = "🔐 Qáwipsizlik"
    SETTINGS_2FA = "2FA"
    SETTINGS_ENABLED = "Qosılǵan"
    SETTINGS_IP_WHITELIST = "IP Whitelist"
    SETTINGS_ACTIVITY_LOGS = "Aktivlik Jurnalı"
    SETTINGS_ACTIVE_SESSIONS = "AKTIV SESSIYALAR"
    SETTINGS_THIS_DEVICE = "Usı qurılma"
    SETTINGS_NOW = "Házir"
    SETTINGS_BTN_CHANGE_PASSWORD = "🔒 Paroldı Ózgertiw"
    SETTINGS_BTN_IP_PERMISSIONS = "🛡️ IP Ruqsatlar"
    SETTINGS_BTN_ACTIVITY = "📋 Aktivlikler"
    SETTINGS_BTN_LOGOUT_ALL = "🚪 Barlıq Sessiyalardan Shıǵıw"
    
    # Arxiv
    SETTINGS_ARCHIVE_TITLE = "💾 ARXIV"
    SETTINGS_STORAGE_SETTINGS = "SAQLAW SAZLAMALARI"
    SETTINGS_RETENTION = "Saqlaw múddeti"
    SETTINGS_QUALITY = "Sapa"
    SETTINGS_FORMAT = "Format"
    SETTINGS_STORAGE_STATUS = "XOTIRA"
    SETTINGS_TOTAL_STORAGE = "Jámi"
    SETTINGS_FREE_SPACE = "Bos orın"
    SETTINGS_BTN_RETENTION = "📅 Saqlaw Múddeti"
    SETTINGS_BTN_QUALITY = "📺 Sapanı Ózgertiw"
    SETTINGS_BTN_CLEANUP = "🗑️ Eski Arxivlerdi Tazalaw"
    
    # Til
    SETTINGS_LANGUAGE_TITLE = "🌍 TIL"
    SETTINGS_SELECT_LANGUAGE = "Tildi tanlań:"
    SETTINGS_LANG_UZ = "🇺🇿 Qaraqalpaq tili"
    SETTINGS_LANG_RU = "🇷🇺 Русский"
    SETTINGS_LANG_EN = "en English"
    
    # Járdem
    SETTINGS_HELP_TITLE = "❓ JÁRDEM"
    SETTINGS_COMMANDS = "BUYRUQLAR"
    SETTINGS_CAPABILITIES = "MÚMKINSHILIKLER"
    SETTINGS_CONTACT = "BAYLANIW"
    SETTINGS_BTN_GUIDE = "📖 Tolıq Qollanba"
    
    # ==========================================
    # EKSPORT
    # ==========================================
    
    EXPORT_TITLE = "📥 EKSPORT"
    EXPORT_SELECT_TYPE = "Eksport túrin tanlań:"
    EXPORT_BTN_VIDEO = "📹 Video Eksport"
    EXPORT_BTN_STATS = "📊 Statistika Eksport"
    EXPORT_BTN_EVENTS = "📋 Bolǵan waqiyalar listesi"
    
    EXPORT_VIDEO_TITLE = "📹 VIDEO EKSPORT"
    EXPORT_FORMAT = "FORMAT"
    EXPORT_QUALITY = "SAPA"
    EXPORT_BTN_HD = "🔷 HD 1080p"
    EXPORT_BTN_SD = "🔶 SD 720p"
    EXPORT_BTN_LOW = "⚪ Tómen 480p"
    
    EXPORT_PREPARING = "⏳ TAYYARLANMAQTA"
    EXPORT_NOT_READY = "⚠️ Video eksport sisteması házir islep shıǵılmaǵan."
    EXPORT_USE_VIEW = "💡 Házir individual video kóriw arqalı júklep alıwıńız múmkin."
    
    EXPORT_STATS_REPORT = "📊 Statistika esabatı"
    EXPORT_SENT = "✅ JIBERILDI"
    EXPORT_FILE_SENT = "📊 Statistika faylı jiberildi!"
    
    # ==========================================
    # TEZ HÁREKTLER
    # ==========================================
    
    QUICK_TITLE = "⚡ TEZ HÁREKTLER"
    QUICK_RECENT_CAMERAS = "📹 Soŋǵı kameralar:"
    QUICK_TIME = "TEZ HÁREKET WAQTI"
    QUICK_AI = "TEZ AI"


# Global instance
msg = Messages()
