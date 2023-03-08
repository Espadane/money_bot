from os import getenv
from typing import Literal

from dotenv import load_dotenv

load_dotenv()


PROJECT_NAME: str = 'Money bot'
TOKEN: str | None = getenv('TOKEN')

DEFAULT_TRANSACTION_CATEGORIES: list[dict[str, str]] = [
    {'category_sort': 'расход', 'category_name': 'продукты'},
    {'category_sort': 'расход', 'category_name': 'транспорт'},
    {'category_sort': 'расход', 'category_name': 'развлечения'},
    {'category_sort': 'расход', 'category_name': 'здоровье'},
    {'category_sort': 'расход', 'category_name': 'семья'},
    {'category_sort': 'расход', 'category_name': 'другое'},
    {'category_sort': 'доход', 'category_name': 'зарплата'},
    {'category_sort': 'доход', 'category_name': 'аванс'},
    {'category_sort': 'доход', 'category_name': 'подарки'},
    {'category_sort': 'доход', 'category_name': 'другое'},
]

DATE_FORMAT: Literal['%d.%m.%Y'] = '%d.%m.%Y'

HELP_MASSAGE: str = '''
Данный бот создан для личного учета финансов.\nФункции:
- Добавление расходов. По нажатию одноименной кнопки необходимо ответить\
 на несколько вопросов и подтвердить запись.
- Добавление доходов. Тоже самое.
- Добавление своих категорий расходов и доходов. Тоже через кнопку.
- Получения отчета о финансах через комманду "status дата".
Где дата: сегодня, вчера, месяц, год, день в формате "01.01.2023" или период \
в формате "01.01.2023 - 02.01.2023".
- Получение отчета о финансках через кнопку "Отчет" в главном меню.\n
По вопросам обращаться @espadane.
'''
