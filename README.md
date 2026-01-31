# 🎥 Cam Max Bot

<div align="center">

![Cam Max](https://img.shields.io/badge/Cam%20Max-AI%20Video%20Analytics-blue?style=for-the-badge&logo=telegram)
![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-orange?style=for-the-badge)
![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Powered-purple?style=for-the-badge&logo=google)


[Telegram Bot](https://t.me/Cam_Max_Bot) • [Muallif](https://t.me/a_qalmuratov) • [Hujjatlar](#-hujjatlar)

</div>

---

## 🌟 Xususiyatlar

### 🧠 13 ta AI Feature

<table>
<tr>
<td width="50%">

#### Asosiy (6 ta)
| # | Feature | Vazifasi |
|---|---------|----------|
| 1 | 💬 Kontekst | Oldingi savollarni eslaydi |
| 2 | ✍️ Typo Fix | Yozuv xatolarini tuzatadi |
| 3 | ⏰ Smart Time | "Kecha", "2 soat oldin" tushunadi |
| 4 | 💡 Follow-up | Keyingi savollarni taklif qiladi |
| 5 | 📊 Summary | Kunlik statistika |
| 6 | 👤 Profiler | Foydalanuvchi afzalliklari |

</td>
<td width="50%">

#### Advanced (7 ta)
| # | Feature | Vazifasi |
|---|---------|----------|
| 7 | 👤 Face | Yuzni tanish |
| 8 | 🚗 Plate OCR | Avtomobil raqamini o'qish |
| 9 | 🏃 Anomaly | Shubhali harakatni aniqlash |
| 10 | 👕 Clothing | Kiyim bo'yicha qidirish |
| 11 | 🔄 Tracking | Multi-object tracking |
| 12 | 🗺️ Zone | Hudud nazorati |
| 13 | 📊 Auto | Avtomatik hisobotlar |

</td>
</tr>
</table>

---

## 🚀 O'rnatish

### 1. Klonlash
```bash
git clone https://github.com/a-qalmuratov/Cam_Max.git
cd Cam_Max
```

### 2. Virtual muhit
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Kutubxonalar
```bash
pip install -r requirements.txt
```

### 4. Sozlamalar
`.env` faylini yarating:
```env
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Ishga tushirish
```bash
python run.py
```

---

## 📱 Foydalanish

### Telegram'da:
1. [@Cam_Max_Bot](https://t.me/Cam_Max_Bot) ga boring
2. `/start` buyrug'ini yuboring
3. Kamera qo'shing
4. Natural language bilan so'rang!

### Namuna savollar:
```
"Kecha kim keldi?"
"Bugun nechta mashina kirdi?"
"01A001AA mashina qachon keldi?"
"Qizil ko'ylakli odam qayerda?"
"Shubhali harakat bormi?"
```

---

## 🏗️ Arxitektura

```
Cam_Max/
├── 🤖 bot/
│   ├── handlers/        # Telegram handlers
│   └── main.py          # Bot entry point
├── 🧠 ai/
│   ├── detector.py      # YOLOv8 detection
│   ├── gemini_ai.py     # Google Gemini integration
│   ├── universal_analyst.py  # Main AI brain
│   ├── face_recognition_module.py
│   ├── plate_reader.py
│   ├── anomaly_detector.py
│   ├── clothing_analyzer.py
│   ├── object_tracker.py
│   ├── zone_monitor.py
│   └── auto_analyzer.py
├── 📹 camera/
│   ├── rtsp_client.py   # RTSP streaming
│   └── video_recorder.py
├── 💾 database/
│   └── models.py        # SQLite database
└── ⚙️ utils/
    ├── config.py
    └── logger.py
```

---

## 🔧 Texnologiyalar

| Kategoriya | Texnologiya |
|------------|-------------|
| **Bot** | python-telegram-bot 20.7 |
| **AI Detection** | YOLOv8, Ultralytics |
| **LLM** | Google Gemini Pro |
| **Face Recognition** | face_recognition, DeepFace |
| **OCR** | EasyOCR |
| **Vision** | OpenCV, CLIP |
| **Database** | SQLite |
| **Deploy** | Hugging Face Spaces, Replit |

---

## 📊 Qo'llab-quvvatlanadigan kameralar

- 📷 **Hikvision** - DS-2CD series
- 📷 **Dahua** - IPC-HDW series
- 📷 **TP-Link** - Tapo C series
- 📷 **Xiaomi** - Mi Camera
- 📷 **Generic** - Har qanday RTSP kamera
- 📱 **Telefon** - IP Webcam, IP Camera apps

---

## 🌍 Til qo'llab-quvvatlashi

- 🇺🇿 **O'zbek** (asosiy)
- 🇷🇺 **Qoraqalpoq**
- 🇬🇧 **English** (tez kunda)

---

## 📝 API Kalitlarini Olish

### Telegram Bot Token
1. [@BotFather](https://t.me/BotFather) ga boring
2. `/newbot` buyrug'ini yuboring
3. Bot nomini va username'ni kiriting
4. Token'ni oling

### Google Gemini API
1. [Google AI Studio](https://aistudio.google.com/app/apikey) ga boring
2. API kalitini yarating

---

## 🚀 Deploy

### Hugging Face Spaces
```bash
python upload_to_hf.py
```

### Replit
1. Replit.com da yangi Python loyiha yarating
2. Fayllarni yuklang
3. Secrets'ga `BOT_TOKEN` va `GEMINI_API_KEY` qo'shing
4. Run tugmasini bosing

---

## 👨‍💻 Muallif

<div align="center">

**Azamat Qalmuratov**

[![Telegram](https://img.shields.io/badge/Telegram-@a__qalmuratov-blue?style=flat-square&logo=telegram)](https://t.me/a_qalmuratov)
[![GitHub](https://img.shields.io/badge/GitHub-a--qalmuratov-black?style=flat-square&logo=github)](https://github.com/a-qalmuratov)
[![Email](https://img.shields.io/badge/Email-qalmuratovazamat5@gmail.com-red?style=flat-square&logo=gmail)](mailto:qalmuratovazamat5@gmail.com)

📱 +998 20 005 00 26

</div>

---

## 📜 Litsenziya

MIT License - Batafsil [LICENSE](LICENSE) faylida.

---

<div align="center">


</div>
