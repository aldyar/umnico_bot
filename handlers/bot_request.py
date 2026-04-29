from aiogram import Bot
from config import BOT_TOKEN,ADMINS

bot = Bot(token=BOT_TOKEN)

async def send_chat_log( text,client_name, role):
    if text.startswith("photo:"):
        return
    if role == 'client':
        header = f"💬 *Клиент написал:*"

    elif role == 'bot':
        header = f"🤖 *Бот ответил в чате:*"
 

    # Формируем итоговый текст
    log_text = (
        f"📱 *Чат с клиентом:* {client_name}\n\n"
        f"{header} {text}")

    # Рассылаем всем админам из списка
    for admin_id in ADMINS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=log_text,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Не удалось отправить лог админу {admin_id}: {e}")


async def send_chat_log_status(client_name, status):
    if status == 'end':
        header = f"⭕️ _Чат с клиентом завершен_"
    elif status == 'priced':
        header = f"⭕️ _Клиенту была названа цена_"
    elif status == 'master':
        header = f"⭕️ _Мастер зашел в чат, бот остановлен_"
 

    # Формируем итоговый текст
    log_text = (
        f"📱 *Чат с клиентом:* {client_name}\n\n"
        f"{header}")

    # Рассылаем всем админам из списка
    for admin_id in ADMINS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=log_text,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Не удалось отправить лог админу {admin_id}: {e}")


# async def send_chat_log_photo(client_name, url):
#     # Формируем итоговый текст
#     log_text = (
#         f"📱 *Чат с клиентом:* {client_name}\n\n"
#         f"_Пользователь отправил фото:_ {url}")

#     # Рассылаем всем админам из списка
#     for admin_id in ADMINS:
#         try:
#             await bot.send_message(
#                 chat_id=admin_id,
#                 text=log_text,
#                 parse_mode="Markdown"
#             )
#         except Exception as e:
#             print(f"Не удалось отправить лог админу {admin_id}: {e}")


async def send_chat_log_photo(client_name, url):
    # Экранируем имя на случай спецсимволов
    safe_name = client_name.replace("*", "\\*").replace("_", "\\_").replace("`", "\\`")
    
    # Текст подписи под фото
    caption = (
        f"📱 *Чат с клиентом:* {safe_name}\n\n"
        f"📸 _Пользователь прислал фотографию_"
    )

    for admin_id in ADMINS:
        try:
            # Отправляем именно фото, а не текстовое сообщение
            await bot.send_photo(
                chat_id=admin_id,
                photo=url,
                caption=caption,
                parse_mode="Markdown"
            )
        except Exception as e:
            # Если вдруг ссылка битая или Телеграм не может скачать фото, 
            # пробуем отправить хотя бы просто текст со ссылкой
            print(f"Ошибка отправки фото админу {admin_id}: {e}")
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=f"{caption}\n🔗 Ссылка на фото: {url}",
                    parse_mode="Markdown"
                )
            except:
                pass
