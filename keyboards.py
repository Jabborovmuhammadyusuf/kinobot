from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ---------------- ADMIN ----------------

def admin_main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="🎬 Kontent boshqaruvi")],
        [KeyboardButton(text="📢 Kanallar boshqaruvi"), KeyboardButton(text="📣 Xabar yuborish")],
        [KeyboardButton(text="👤 Foydalanuvchi menyusi")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def content_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🎥 Kino yuklash"), KeyboardButton(text="📺 Serial yuklash")],
        [KeyboardButton(text="➕ Yangi qism qoʼshish")],
        [KeyboardButton(text="✏️ Kino tahrirlash"), KeyboardButton(text="✏️ Serial tahrirlash")],
        [KeyboardButton(text="🔙 Orqaga")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True
    )


def user_menu() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="🔍 Kino qidirish")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def series_status_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🔢 Belgilangan son (fasl/qism)", callback_data="status_fixed")
    b.button(text="♾ Davom etmoqda", callback_data="status_ongoing")
    b.adjust(1)
    return b.as_markup()


def skip_description_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="⏭ Oʼtkazib yuborish", callback_data="skip_description")
    return b.as_markup()


def edit_fields_kb(target: str) -> InlineKeyboardMarkup:
    # target: "movie" yoki "series"
    b = InlineKeyboardBuilder()
    b.button(text="✏️ Nomini tahrirlash", callback_data=f"edit_title")
    b.button(text="📝 Maʼlumotni tahrirlash", callback_data=f"edit_description")
    if target == "series":
        b.button(text="🔄 Holatini oʼzgartirish (davom/tugagan)", callback_data="edit_status")
    b.button(text="🗑 Butunlay oʼchirish", callback_data="edit_delete")
    b.adjust(1)
    return b.as_markup()


def confirm_delete_kb(code: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Ha, oʼchirish", callback_data=f"confirm_delete_{code}")
    b.button(text="❌ Yoʼq", callback_data="cancel_delete")
    b.adjust(2)
    return b.as_markup()


def channels_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="➕ Kanal qoʼshish"), KeyboardButton(text="📋 Kanallar roʼyxati")],
        [KeyboardButton(text="🔙 Orqaga")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def channel_remove_kb(channels) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for ch in channels:
        b.button(text=f"🗑 {ch['title']}", callback_data=f"remove_channel_{ch['id']}")
    b.adjust(1)
    return b.as_markup()


def subscribe_kb(channels, bot_username: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for ch in channels:
        username = ch["channel_username"]
        if username:
            url = f"https://t.me/{username.lstrip('@')}"
        else:
            url = f"https://t.me/c/{str(ch['channel_id']).replace('-100', '')}"
        b.button(text=f"➕ {ch['title']}", url=url)
    b.button(text="✅ Aʼzo boʼldim", callback_data="check_subscription")
    b.adjust(1)
    return b.as_markup()


def parts_keyboard(code: str, total_parts: int, per_row: int = 5) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for i in range(1, total_parts + 1):
        b.button(text=str(i), callback_data=f"part_{code}_{i}")
    b.adjust(per_row)
    return b.as_markup()


def search_results_kb(movies) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for m in movies:
        icon = "🎬" if m["type"] == "movie" else "📺"
        b.button(text=f"{icon} {m['title']}", callback_data=f"open_{m['code']}")
    b.adjust(1)
    return b.as_markup()


def back_to_parts_kb(code: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🔙 Qismlar roʼyxatiga", callback_data=f"open_{code}")
    return b.as_markup()
