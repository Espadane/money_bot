from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.text import Text


from keyboards.keyboards import main_menu_keyboard, report_keyboard
from database import get_transactions_on_date


router: Router = Router()


class GiveReport(StatesGroup):
    """
        Состояния получения отчетов
    """
    choose_report_date: Optional[State] = State()
    input_report_date: Optional[State] = State()


@router.message(Text('Отчет'))
async def get_report(msg: Message, state: FSMContext) -> None:
    """
        Обработка нажатия на кнопку получения отчета
    """
    await msg.answer('Выберите за какое время получить отчет:',
                     reply_markup=report_keyboard())
    await state.set_state(GiveReport.choose_report_date)


@router.message(GiveReport.choose_report_date)
async def report_date_choosen(msg: Message, state: FSMContext) -> None:
    """
        выбор даты получения отчета
    """
    user_id: int = int(msg.from_user.id)
    date: str = msg.text.lower()
    if date in ['сегодня', 'вчера', 'месяц', 'год']:
        answer: str = get_transactions_on_date(date, user_id)
        await msg.answer(answer, reply_markup=main_menu_keyboard())
        await state.clear()
    elif date in ['даты']:
        await msg.answer('Введите желаемые даты в формате "01.01.2023"\
 или "01.01.2023 - 01.02.2023"',
                         reply_markup=ReplyKeyboardRemove())
        await state.set_state(GiveReport.input_report_date)
    else:
        await msg.answer('Нажмите кнопку')


@router.message(GiveReport.input_report_date)
async def input_report_date(msg: Message, state: FSMContext) -> None:
    """
        обработка ввода даты
    """
    user_id: int = int(msg.from_user.id)
    date: str = str(msg.text)
    answer: str = get_transactions_on_date(date, user_id)
    await msg.answer(answer, reply_markup=main_menu_keyboard())
    await state.clear()
