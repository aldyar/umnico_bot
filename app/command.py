from aiogram import Bot
from aiogram.types import BotCommand

async def set_main_menu(bot: Bot):
    # Список команд, которые будут отображаться в меню
    main_menu_commands = [
        BotCommand(command='/start', description='Запустить бота'),
        #BotCommand(command='/menu', description='Открыть главное меню'),
        #BotCommand(command='/help', description='Справка и помощь'),
    ]
    
    await bot.set_my_commands(main_menu_commands)