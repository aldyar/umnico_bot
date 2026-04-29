from aiogram import Bot, Dispatcher, F,types
from aiogram.filters import Command,CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery
from aiogram import Router
from function.account_func import AccountFunc
from aiogram.fsm.context import FSMContext
from app.state import EditAccount

user = Router()

# --- 1. Главное меню выбора аккаунтов ---
@user.message(CommandStart())
async def cmd_start(message: Message):
    accounts = await AccountFunc.get_all()
    
    if not accounts:
        await message.answer("Аккаунтов пока нет.")
        return

    builder = InlineKeyboardBuilder()
    for acc in accounts:
        # Текст кнопки: логин или ID. В callback_data передаем ID
        builder.row(types.InlineKeyboardButton(
            text=f"👤 {acc.login or acc.id}", 
            callback_data=f"view_acc_{acc.id}")
        )
    
    await message.answer("*Выберите аккаунт для управления:*",parse_mode='Markdown', reply_markup=builder.as_markup())


# --- 2. Меню конкретного аккаунта ---
@user.callback_query(F.data.startswith("view_acc_"))
async def view_account(callback: CallbackQuery):
    account_id = callback.data.split("_")[2]
    # Получаем данные одного аккаунта (предположим, есть метод get_one)
    acc = await AccountFunc.get_one(account_id) 
    
    if not acc:
        await callback.answer("Аккаунт не найден")
        return

    text = (
        f"*🗂 Данные аккаунта*\n"
        f"__________________________\n\n"
        f"*🆔 ID:* `{acc.id}`\n"
        f"*🏷 Тип:* `{acc.type}`\n"
        f"*👤 Логин:* `{acc.login}`\n\n"
        f"*📝 Текущий промпт:*\n"
        f"_{acc.prompt}_\n"
        f"__________________________\n"
    )

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="📝 Изменить промпт", 
        callback_data=f"edit_prompt_{acc.id}")
    )
    builder.row(types.InlineKeyboardButton(
        text="⬅️ Назад к списку", 
        callback_data="back_to_list")
    )

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")


# --- 3. Начало процесса изменения промпта ---
@user.callback_query(F.data.startswith("edit_prompt_"))
async def start_edit_prompt(callback: CallbackQuery, state: FSMContext):
    account_id = callback.data.split("_")[2]
    
    await state.update_data(edit_acc_id=account_id) # Запоминаем ID аккаунта
    await state.set_state(EditAccount.waiting_for_prompt)
    
    await callback.message.answer(f"Введите новый промпт для аккаунта (ID: {account_id}):")
    await callback.answer()


# --- 4. Прием нового промпта и апдейт в БД ---
@user.message(EditAccount.waiting_for_prompt)
async def process_new_prompt(message: Message, state: FSMContext):
    data = await state.get_data()
    account_id = data.get("edit_acc_id")
    new_prompt = message.text

    try:
        # Используем твою функцию update_one
        await AccountFunc.update_one(id=account_id, prompt=new_prompt)
        await message.answer(f"✅ Промпт для аккаунта {account_id} успешно обновлен!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении: {e}")
    
    await state.clear() # Сбрасываем состояние


# --- Вспомогательный: Назад к списку ---
@user.callback_query(F.data == "back_to_list")
async def back_to_list(callback: CallbackQuery):
    await cmd_start(callback.message)
    await callback.message.delete()