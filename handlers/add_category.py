from typing import Optional, Literal, Dict, Any

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.text import Text

from keyboards.keyboards import main_menu_keyboard,\
    sort_category_keyboard, comfirm_keyboard
from database import insert_user_category


router: Router = Router()


class AddCategory(StatesGroup):
    """
        Состояния добаления категорий пользователя
    """
    choose_category_sort: Optional[State] = State()
    chose_category_name: Optional[State] = State()
    confirm_category: Optional[State] = State()


@router.message(Text('Добавить категорию'))
async def add_category(msg: Message, state: FSMContext) -> None:
    """
        Обработка нажатия кнопки добавить категорию
    """
    await msg.answer('Категория расхода или дохода?',
                     reply_markup=sort_category_keyboard())

    await state.set_state(AddCategory.choose_category_sort)


@router.message(AddCategory.choose_category_sort,
                F.text.in_(['Категория дохода', 'Категория расхода']))
async def category_sort_chosen(msg: Message, state: FSMContext) -> None:
    """
        Выбор категория дохода или расхода
    """
    match msg.text:
        case 'Категория дохода': category_sort: Literal['расход'] = 'доход'
        case 'Категория расхода': category_sort: Literal['расход'] = 'расход'

    await state.update_data(category_sort=category_sort)
    await msg.answer('Напишите название категории',
                     reply_markup=ReplyKeyboardRemove())

    await state.set_state(AddCategory.chose_category_name)


@router.message(AddCategory.choose_category_sort)
async def category_sort_incorrectly(msg: Message) -> None:
    """
        Обработка не запланированного ответа
    """
    await msg.answer('Нажми кнопки внизу. Пожалуйста.')


@router.message(AddCategory.chose_category_name)
async def category_name_chosen(msg: Message, state: FSMContext) -> None:
    """
        обработка ввода называния категории
    """
    await state.update_data(category_name=msg.text.lower())
    await state.update_data(user_id=int(msg.from_user.id))
    await msg.answer('Подтвердить?', reply_markup=comfirm_keyboard())
    await state.set_state(AddCategory.confirm_category)


@router.message(AddCategory.confirm_category, F.text.in_(
    ['Подтвердить', 'Отменить']
))
async def confirm_category(msg: Message, state: FSMContext) -> None:
    """
        Подтверждение создания пользовательской категории
    """
    user_data: Dict[str, int] = await state.get_data()

    if msg.text == 'Подтвердить':
        await msg.answer('Категория добавлена',
                         reply_markup=main_menu_keyboard())
        insert_user_category(user_data)
    elif msg.text == 'Отменить':
        await msg.answer('Отменено пользователем, попробуйте снова.',
                         reply_markup=main_menu_keyboard())
    await state.clear()


@router.message(AddCategory.confirm_category)
async def confirm_category_incorrectly(msg: Message) -> None:
    """
        Обработка неверного ввода подтверждения
    """
    await msg.answer('Нажмите кнопку')
