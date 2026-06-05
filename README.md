# New Films Telegram Bot

Uzbek tilidagi Telegram bot — [top-newfilms API](https://top-newfilms.onrender.com) orqali kinolar va kategoriyalarni ko'rsatadi.

## Imkoniyatlar

- **🎬 Barcha kinolar** — barcha kinolar ro'yxati (inline tugmalar)
- **📁 Kategoriyalar** — kategoriyalar va har biridagi kinolar soni
- Kino tanlanganda poster, reyting, davlat, davomiylik, rejissyor va tavsif ko'rsatiladi

## O'rnatish

### 1. Bot token olish

1. Telegramda [@BotFather](https://t.me/BotFather) ga yozing
2. `/newbot` buyrug'ini yuboring va ko'rsatmalarga amal qiling
3. Olingan tokenni saqlang

### 2. Loyihani sozlash

```bash
pip install -r requirements.txt
```

`.env.example` faylini `.env` ga nusxalang va tokenni kiriting:

```
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 3. Botni ishga tushirish

```bash
python bot.py
```

## API manbalari

- Kinolar: `https://top-newfilms.onrender.com/api/films/`
- Kategoriyalar: `https://top-newfilms.onrender.com/api/categories/`
