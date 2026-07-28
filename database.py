import aiosqlite
from datetime import datetime, date

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS movies (
    code TEXT PRIMARY KEY,
    type TEXT CHECK(type IN ('movie', 'series')) NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    is_ongoing INTEGER DEFAULT 0,
    total_parts INTEGER DEFAULT 0,
    declared_parts INTEGER DEFAULT 0,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    part_number INTEGER NOT NULL,
    file_id TEXT NOT NULL,
    added_at TEXT,
    FOREIGN KEY(code) REFERENCES movies(code) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    joined_at TEXT,
    source_channel TEXT
);

CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT UNIQUE,
    channel_username TEXT,
    title TEXT,
    added_at TEXT
);

CREATE TABLE IF NOT EXISTS views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    viewed_at TEXT
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


# ---------------- USERS ----------------

async def add_user(user_id: int, username: str, full_name: str, source_channel: str | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if row:
            return False
        await db.execute(
            "INSERT INTO users (user_id, username, full_name, joined_at, source_channel) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, full_name, datetime.utcnow().isoformat(), source_channel),
        )
        await db.commit()
        return True


async def users_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        (count,) = await cur.fetchone()
        return count


async def users_count_today() -> int:
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT COUNT(*) FROM users WHERE joined_at LIKE ?", (f"{today}%",)
        )
        (count,) = await cur.fetchone()
        return count


# ---------------- MOVIES / SERIES ----------------

async def movie_code_exists(code: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT code FROM movies WHERE code = ?", (code,))
        row = await cur.fetchone()
        return row is not None


async def create_movie(code: str, type_: str, title: str, description: str,
                        is_ongoing: bool, declared_parts: int = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO movies (code, type, title, description, is_ongoing, total_parts, declared_parts, created_at)
               VALUES (?, ?, ?, ?, ?, 0, ?, ?)""",
            (code, type_, title, description, int(is_ongoing), declared_parts, datetime.utcnow().isoformat()),
        )
        await db.commit()


async def add_part(code: str, part_number: int, file_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO parts (code, part_number, file_id, added_at) VALUES (?, ?, ?, ?)",
            (code, part_number, file_id, datetime.utcnow().isoformat()),
        )
        await db.execute(
            "UPDATE movies SET total_parts = (SELECT COUNT(*) FROM parts WHERE code = ?) WHERE code = ?",
            (code, code),
        )
        await db.commit()


async def get_movie(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM movies WHERE code = ?", (code,))
        return await cur.fetchone()


async def search_movies_by_title(query: str, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM movies WHERE title LIKE ? ORDER BY created_at DESC LIMIT ?",
            (f"%{query}%", limit),
        )
        return await cur.fetchall()


async def get_parts(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM parts WHERE code = ? ORDER BY part_number ASC", (code,)
        )
        return await cur.fetchall()


async def get_part(code: str, part_number: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM parts WHERE code = ? AND part_number = ?", (code, part_number)
        )
        return await cur.fetchone()


async def get_max_part_number(code: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT MAX(part_number) FROM parts WHERE code = ?", (code,))
        row = await cur.fetchone()
        return row[0] or 0


async def update_movie_field(code: str, field: str, value):
    assert field in ("title", "description", "is_ongoing", "declared_parts")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE movies SET {field} = ? WHERE code = ?", (value, code))
        await db.commit()


async def delete_movie(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM parts WHERE code = ?", (code,))
        await db.execute("DELETE FROM movies WHERE code = ?", (code,))
        await db.commit()


async def movies_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM movies WHERE type = 'movie'")
        (movies,) = await cur.fetchone()
        cur = await db.execute("SELECT COUNT(*) FROM movies WHERE type = 'series'")
        (series,) = await cur.fetchone()
        cur = await db.execute("SELECT COALESCE(SUM(total_parts), 0) FROM movies WHERE type = 'series'")
        (parts,) = await cur.fetchone()
        return {"movies": movies, "series": series, "series_parts": parts}


# ---------------- CHANNELS ----------------

async def add_channel(channel_id: str, channel_username: str, title: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO channels (channel_id, channel_username, title, added_at) VALUES (?, ?, ?, ?)",
            (channel_id, channel_username, title, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return cur.lastrowid


async def get_channels():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM channels ORDER BY id ASC")
        return await cur.fetchall()


async def get_channel(row_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM channels WHERE id = ?", (row_id,))
        return await cur.fetchone()


async def remove_channel(row_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM channels WHERE id = ?", (row_id,))
        await db.commit()


async def channel_referral_count(row_id: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT COUNT(*) FROM users WHERE source_channel = ?", (str(row_id),)
        )
        (count,) = await cur.fetchone()
        return count


# ---------------- VIEWS ----------------

async def log_view(code: str, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO views (code, user_id, viewed_at) VALUES (?, ?, ?)",
            (code, user_id, datetime.utcnow().isoformat()),
        )
        await db.commit()


async def total_views() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM views")
        (count,) = await cur.fetchone()
        return count


async def top_movies(limit: int = 5):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """SELECT m.code, m.title, COUNT(v.id) as views
               FROM movies m LEFT JOIN views v ON m.code = v.code
               GROUP BY m.code ORDER BY views DESC LIMIT ?""",
            (limit,),
        )
        return await cur.fetchall()
