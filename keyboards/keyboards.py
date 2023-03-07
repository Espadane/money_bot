from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
        клавиатура главного меню
    """
    keyboard: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    keyboard.button(text='Расход')
    keyboard.button(text='Доход')
    keyboard.adjust(2)
    keyboard.button(text='Добавить категорию')
    keyboard.adjust(1)

    return keyboard.as_markup(resize_keyboard=True)


def skip_keyboard() -> ReplyKeyboardMarkup:
    """
        клавиатура с кнопкой "пропустить"
    """
    keyboard: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    keyboard.button(text='Пропустить')
    keyboard.adjust(1)

    return keyboard.as_markup(resize_keyboard=True)


def comfirm_keyboard() -> ReplyKeyboardMarkup:
    """
        клавиатура подтверждения
    """
    keyboard: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    keyboard.button(text='Подтвердить')
    keyboard.button(text='Отменить')
    keyboard.adjust(2)

    return keyboard.as_markup(resize_keyboard=True)


def sort_category_keyboard() -> ReplyKeyboardMarkup:
    """
        Клавиатура выбора вида категории
    """
    keyboard: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    keyboard.button(text='Категория дохода')
    keyboard.button(text='Категория расхода')

    keyboard.adjust(2)

    return keyboard.as_markup(resize_keyboard=True)


def category_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
        генератор клавиатуры пользовательских категорий
    """
    keyboard: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    for item in items:
        keyboard.button(text=item.capitalize())

    keyboard.adjust(3)

    return keyboard.as_markup(resize_keyboard=True)
