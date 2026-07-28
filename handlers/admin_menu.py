from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import keyboards as kb
from utils import is_admin

router = Router()
router.message.filter(lambda message: is_admin(message.from_user.id))


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🛠 Admin panel", reply_markup=kb.admin_main_menu())


@router.message(F.text == "🎬 Kontent boshqaruvi")
async def content_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🎬 Kontent boshqaruvi boʼlimi:", reply_markup=kb.content_menu())


@router.message(F.text == "👤 Foydalanuvchi menyusi")
async def switch_to_user_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("👤 Foydalanuvchi menyusiga oʼtdingiz.", reply_markup=kb.user_menu())


@router.message(F.text == "🔙 Orqaga")
async def back_to_admin_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🛠 Admin panel", reply_markup=kb.admin_main_menu())


@router.message(F.text == "❌ Bekor qilish")
async def cancel_any_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=kb.admin_main_menu())
