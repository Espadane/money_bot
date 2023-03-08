import asyncio
from typing import NoReturn

from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command, Text
from aiogram.filters.command import CommandObject
import aioschedule

from config import *
from logger import logger
from database import insert_default_categories, get_transactions_on_date,\
    get_users_list, change_user_subscribe_status
from keyboards.keyboards import main_menu_keyboard
from handlers import add_transaction, add_category, report


router: Router = Router()
bot: Bot = Bot(token=TOKEN, parse_mode='HTML')


@router.message(Command(commands=['start', 'help']))
async def command_start_handler(msg: Message) -> None:
    """
        Старт он же хелп
    """
    await msg.answer(HELP_MASSAGE,
                     reply_markup=main_menu_keyboard())


@router.message(Command(commands=['status']))
async def cmd_status(msg: Message, command: CommandObject) -> None:
    """
        команда status в зависимости используется в зависимость от аргументов
    """
    user_id: int = msg.from_user.id
    if command.args:
        answer: str = get_transactions_on_date(command.args.lower(), user_id)
        await msg.answer(answer)
    else:
        await msg.answer('Пожалуйста введи значение после "/status ".')


@router.message(Text('Вкл/Выкл подписку'))
async def on_of_subscribe(msg: Message) -> None:
    """
        меняем статус подписки по нажатию кнопки
    """
    user_id: int = int(msg.from_user.id)
    status: int = change_user_subscribe_status(user_id)

    if status == 1:
        answer: str = 'Вы подписаны на отчет за день в 21:00'
    elif status == 0:
        answer: str = 'Вы отписались от отчета за день'

    await msg.answer(answer)


async def send_daily_report() -> None:
    """
        отправлеяем отчет за день
    """
    users_list: list = get_users_list()
    for user_id in users_list:
        daily_report: str = get_transactions_on_date('сегодня', user_id)
        try:
            await bot.send_message(user_id, daily_report)
            await bot.send_message(user_id, 'Проверьте все ли данные\
 за сегодня вы внесли.')
        except Exception as error:
            logger.warning(error)


async def schedeller() -> NoReturn:
    """
        функция планировщика
    """
    aioschedule.every().day.at('21:00').do(send_daily_report)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup() -> None:
    """
        запускает планировщик со стартом бота
    """
    asyncio.create_task(schedeller())


async def main() -> None:
    insert_default_categories(DEFAULT_TRANSACTION_CATEGORIES)
    dp: Dispatcher = Dispatcher()
    dp.include_router(router)
    dp.include_router(add_transaction.router)
    dp.include_router(add_category.router)
    dp.include_router(report.router)

    dp.startup.register(on_startup)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    asyncio.run(main())
