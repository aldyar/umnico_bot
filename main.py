import uvicorn
from fastapi import FastAPI
from router.user import router as user_router
import asyncio
from database.models import async_main
from aiogram import Bot,Dispatcher
from config import BOT_TOKEN
from handlers.user import user
from app.command import set_main_menu

app = FastAPI()
app.include_router(user_router)
bot = Bot(token=BOT_TOKEN)
# if __name__ == "__main__":
#     try:
#         asyncio.run(async_main())
#     except Exception as e:
#         print(f"Ошибка при создании таблиц: {e}")
#     # Запуск на порту 5500, как в твоих логах
#     uvicorn.run("main:app", host="0.0.0.0", port=5500, reload=True)




# 2. Обертка для запуска FastAPI
async def run_fastapi():
    # Вот этот конфиг заменяет твою строку uvicorn.run
    # Он говорит серверу: работай на 5500 порту и используй наше приложение app
    config = uvicorn.Config(app, host="0.0.0.0", port=5500, reload=False)
    server = uvicorn.Server(config)
    await server.serve()

# 3. Функция стартапа (твоя база и конфиги)
async def on_startup():
    await async_main()
    await set_main_menu(bot)
    print('✅ BOT STARTED')

# 4. Главная функция, которая связывает всё
async def main():
    
    dp = Dispatcher()
    dp.include_routers(user)
    await on_startup()
    print('🚀 Запуск системы: FastAPI на 5500 и Bot...')
    await asyncio.gather(
        run_fastapi(),
        dp.start_polling(bot)
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановка приложения")