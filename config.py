import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x.strip()]
DB_PATH = os.getenv("DB_PATH", "kino_bot.db")

# Albom (bir nechta video birga yuborilganda) yigʼilishini kutish vaqti, soniyada
ALBUM_DEBOUNCE = 1.2
