# 🎬 Kino/Serial Telegram Bot

Python (aiogram 3) + SQLite asosida qurilgan, kino va seriallarni boshqarish uchun toʼliq bot.

## ⚙️ Oʼrnatish

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` faylini oching va toʼldiring:

```
BOT_TOKEN=BotFather'dan olingan token
ADMIN_IDS=sizning_telegram_id_raqamingiz
```

Telegram ID raqamingizni bilish uchun @userinfobot ga yozing.

Botni ishga tushirish:

```bash
python3 bot.py
```

## 📋 Funksiyalar

### 1. Kino/Serial yuklash (avtomatik aniqlash)
- **"🎥 Kino yuklash"** — bitta video yuborsangiz, u kino sifatida saqlanadi.
- Agar shu yerda **bir vaqtda bir nechta video** (albom sifatida, hammasini birga tanlab) yuborsangiz, bot buni avtomatik ravishda **serial** deb hisoblaydi va har bir videoni alohida qism (1-qism, 2-qism, ...) qilib saqlaydi.
- **"📺 Serial yuklash"** — maxsus serial yuklash rejimi. Bu yerda video(lar)ni yuborgach, bot serial holatini soʼraydi:
  - 🔢 **Belgilangan son** — jami nechta qism/fasl boʼlishini kiritasiz.
  - ♾ **Davom etmoqda** — jami soni hali noaniq, keyinchalik qoʼshib borasiz.
- Har ikkala holatda ham bot ketma-ket soʼraydi: **kod → nomi → (serial uchun holati/soni) → maʼlumot (tavsif)**.
- Bitta kodga faqat bitta kino/serial biriktiriladi — kod band boʼlsa, bot boshqa kod kiritishni soʼraydi.

### 2. Yangi qism qoʼshish
- **"➕ Yangi qism qoʼshish"** tugmasi orqali admin serial kodini kiritadi.
- Bot avtomatik oʼsha serialni topadi (masalan, 5 qism yuklangan boʼlsa, keyingi video 6-qism boʼlib qoʼshiladi).
- Bitta yoki bir nechta yangi video (albom) yuborish mumkin — barchasi ketma-ket qism raqamlarini oladi.

### 3. Kontent tahrirlash
- **"✏️ Kino tahrirlash"** va **"✏️ Serial tahrirlash"** — alohida-alohida tugmalar.
- Kod kiritilgach, tugmalar chiqadi: nomini tahrirlash, maʼlumotini tahrirlash, (serial uchun) holatini oʼzgartirish, butunlay oʼchirish.

### 4. Statistika
- Jami/bugungi foydalanuvchilar soni
- Kinolar va seriallar soni, jami qismlar soni
- Jami koʼrishlar va eng koʼp koʼrilgan kontent
- **Har bir kanal boʼyicha** qancha obunachi shu kanaldan kelgani (referal havola orqali)

### 5. Kanallar boshqaruvi (majburiy obuna)
- **"➕ Kanal qoʼshish"** — kanal username yoki ID kiritiladi (bot shu kanalda admin boʼlishi shart).
- Bot har bir kanal uchun referal havola beradi: `t.me/BOT_USERNAME?start=ch_<ID>`.
- Shu havolani tegishli kanalda joylashtirsangiz, oʼsha kanaldan kelgan foydalanuvchilar avtomatik hisoblanadi.
- Foydalanuvchi botdan foydalanishdan oldin barcha qoʼshilgan kanallarga aʼzo boʼlishi shart (majburiy obuna tekshiruvi avtomatik ishlaydi).

### 6. Foydalanuvchi tomoni
- Kino/serial kodini yuborsa yoki nomi boʼyicha qidirsa, mos kontent chiqadi.
- Kino — toʼgʼridan-toʼgʼri video yuboriladi.
- Serial — 1 dan oxirgi qismgacha inline tugmalar chiqadi, bosilgan tugma oʼsha qismni yuboradi.

### 7. Xabar yuborish (broadcast)
- **"📣 Xabar yuborish"** — admin istalgan turdagi xabarni (matn/rasm/video) barcha foydalanuvchilarga yuboradi.

## 🗂 Loyiha tuzilishi

```
kino_bot/
├── bot.py              # Ishga tushirish nuqtasi
├── config.py            # .env orqali sozlamalar
├── database.py           # SQLite bilan ishlash (barcha funksiyalar)
├── states.py             # FSM holatlari
├── keyboards.py           # Barcha reply/inline tugmalar
├── utils.py              # Admin tekshiruvi, albom yigʼish, obuna tekshiruvi
├── handlers/
│   ├── user.py           # Foydalanuvchi: start, qidiruv, video yuborish
│   ├── admin_menu.py      # Admin asosiy menyu navigatsiyasi
│   ├── upload.py          # Kino/serial yuklash logikasi
│   ├── add_episode.py      # Yangi qism qoʼshish
│   ├── edit.py            # Tahrirlash/oʼchirish
│   ├── channels.py        # Majburiy kanallar boshqaruvi
│   ├── stats.py           # Statistika
│   └── broadcast.py        # Ommaviy xabar yuborish
└── requirements.txt
```

## 💡 Eslatmalar

- Ma'lumotlar bazasi — `kino_bot.db` (SQLite), avtomatik yaratiladi.
- Bot bir nechta admin qoʼllab-quvvatlaydi (`.env` da vergul bilan ajratib yozing).
- Bir vaqtda bir nechta video "albom" sifatida faqat Telegram ilovasida bir nechta faylni birga tanlab yuborganda ishlaydi (media group).
- Production muhitda botni doim ishlab turishi uchun `systemd`, `screen`/`tmux`, yoki `docker` dan foydalanishni tavsiya qilamiz.
