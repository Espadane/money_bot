from typing import Dict, Any, Literal

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.keyboards import category_keyboard, skip_keyboard,\
    comfirm_keyboard, main_menu_keyboard
from database import get_user_categories, insert_transaction


router: Router = Router()


class AddTransaction(StatesGroup):
    """
        состояния добавления транзакций
    """
    chosing_transaction_category: State = State()
    input_transaction_sum: State = State()
    input_transaction_comment: State = State()
    confirm_transaction: State = State()


@router.message(F.text.in_(
    ['Расход', 'Доход']
))
async def add_transaction(msg: Message, state: FSMContext) -> None:
    """
        Обработка кнопки добавить транзакцию
    """
    user_id: int = msg.from_user.id
    sort_transaction: str = msg.text.lower()
    transaction_category: list = get_user_categories(user_id, sort_transaction)
    await msg.answer(
        "Выберите категорию",
        reply_markup=category_keyboard(transaction_category)
    )
    await state.update_data(user_id=int(user_id),
                            transaction_sort=sort_transaction
                            )

    await state.set_state(AddTransaction.chosing_transaction_category)


@router.message(AddTransaction.chosing_transaction_category)
async def transaction_category_chosen(msg: Message, state: FSMContext) -> None:
    """
        обработка выбора категории транзакции
    """
    user_data: Dict[str, Any] = await state.get_data()
    user_id: int = user_data['user_id']
    sort: str = user_data['transaction_sort']
    transaction_category: list = get_user_categories(user_id, sort)
    if msg.text.lower() not in transaction_category:
        await msg.answer(f'Такой категории у тебя нет, \
данный {sort} будет добавлен в другое.')
        await state.update_data(transaction_category_name='другое')
    else:
        await state.update_data(transaction_category_name=msg.text.lower())
    await msg.answer(text=f'Напишите сумму {sort}а',
                     reply_markup=ReplyKeyboardRemove())

    await state.set_state(AddTransaction.input_transaction_sum)


@router.message(AddTransaction.input_transaction_sum)
async def transaction_sum_input(msg: Message, state: FSMContext) -> None:
    """
        обработка ввода суммы транзакции
    """
    if '-' in msg.text:
        await msg.answer('Без знака минуса пожалуйста, просто число')
        await state.set_state(AddTransaction.input_transaction_sum)
    else:
        try:
            user_data: Dict[str, Any] = await state.get_data()
            sort: str = user_data['transaction_sort']
            if sort == 'расход':
                transaction_sum: int = -int(msg.text)
            elif sort == 'доход':
                transaction_sum: int = int(msg.text)
            await state.update_data(transaction_sum=transaction_sum)
            await state.set_state(AddTransaction.input_transaction_comment)
            await msg.answer('Введите коментарий, или нажмите кнопку пропустить', reply_markup=skip_keyboard())

        except BaseException:
            await msg.answer('Введено не корректное число')
            await state.set_state(AddTransaction.input_transaction_sum)


@router.message(AddTransaction.input_transaction_comment)
async def transaction_comment_input(msg: Message, state: FSMContext) -> None:
    """
        обработка ввода коментария
    """
    if msg.text == 'Пропустить':
        transaction_comment: Literal[''] = ''
    else:
        transaction_comment: Literal[''] = msg.text
    await msg.answer('Подтверждаете введенные данные?',
                     reply_markup=comfirm_keyboard())
    await state.update_data(transaction_comment=transaction_comment)
    await state.set_state(AddTransaction.confirm_transaction)
    user_data: Dict[str, Any] = await state.get_data()
    transaction_answer: str = f'{user_data["transaction_sort"].capitalize()}\n\
Сумма: {user_data["transaction_sum"]}\n\
Категория: {user_data["transaction_category_name"].capitalize()}\n\
Комментарий: {user_data["transaction_comment"]}'
    await msg.answer(transaction_answer)


@router.message(AddTransaction.confirm_transaction, F.text.in_(
    ['Подтвердить', 'Отменить']
))
async def confirm_transaction(msg: Message, state: FSMContext) -> None:
    """
        Подтверждение транзакции
    """
    user_data: Dict[str, int] = await state.get_data()

    if msg.text == 'Подтвердить':
        await msg.answer('Запись занесена в базу данных.',
                         reply_markup=main_menu_keyboard())
        insert_transaction(user_data)
    elif msg.text == 'Отменить':
        await msg.answer('Отменено пользователем, попробуйте снова.',
                         reply_markup=main_menu_keyboard())
    await state.clear()


@router.message(AddTransaction.confirm_transaction)
async def confirm_transaction_incorrectly(msg: Message) -> None:
    """
        обработка не корректного подтверждения транзакции
    """
    await msg.answer('Нажмите кнопку')
