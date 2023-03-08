import re
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import create_engine, Column, String, Integer, or_, and_
from sqlalchemy import Engine
from sqlalchemy.orm import Session, DeclarativeBase

from config import DATE_FORMAT
from logger import logger


try:
    engine: Engine = create_engine('sqlite:///money_database.db')
    logger.debug('движок создан')
except Exception as error:
    logger.warning(error)


class Base(DeclarativeBase):
    pass


class TransactionCategories(Base):
    """
        таблица пользовательских категорий
    """
    __tablename__: str = 'transaction_categories'
    id: Column[int] = Column(Integer(), primary_key=True)
    user_id: Column[int] = Column(Integer(), nullable=False)
    category_sort: Column[str] = Column(String(100), nullable=False)
    category_name: Column[str] = Column(String(100), nullable=False)


class Transactions(Base):
    """
        таблица транзакций пользователей
    """
    __tablename__: str = 'transactions'
    id: Column[int] = Column(Integer(), primary_key=True)
    user_id: Column[int] = Column(Integer(), nullable=False)
    transaction_sort: Column[str] = Column(String(100), nullable=False)
    transaction_date: Column[str] = Column(String())
    transaction_category_name: Column[str] = Column(
        String(100), nullable=False)
    transaction_sum: Column[int] = Column(Integer(), nullable=False)
    transaction_comment: Column[str] = Column(String(), nullable=False)


class UsersSubscribes(Base):
    """
        таблица пользователей и их подписок
    """
    __tablename__: str = 'users_subscribes'
    id: Column[int] = Column(Integer(), primary_key=True)
    user_id: Column[int] = Column(Integer(), nullable=False)
    subscribe: Column[int] = Column(Integer(), nullable=False, default=1)


try:
    Base.metadata.create_all(engine)
    session: Session = Session(bind=engine)
except Exception as error:
    logger.warning(error)


def insert_default_categories(DEFAULT_TRANSACTION_CATEGORIES: list) -> None:
    """
        запись стандартных категорий транзакций
    """
    try:
        default_category: TransactionCategories | None = session.query(TransactionCategories).filter(
            TransactionCategories.user_id == 0).first()
        if default_category is None:
            for category in DEFAULT_TRANSACTION_CATEGORIES:
                category_sort: str = category['category_sort']
                category_name: str = category['category_name']
                query: TransactionCategories = TransactionCategories(user_id=0,
                                                                     category_sort=category_sort,
                                                                     category_name=category_name,
                                                                     )
                session.add(query)

            session.commit()
            logger.debug('Стандартные категории добавлены')

    except Exception as error:
        logger.warning(error)


def insert_user_category(user_category) -> None:
    """
        запись пользовательской категории
    """
    try:
        category_sort: str = user_category['category_sort']
        category_name: str = user_category['category_name']
        user_id: int = user_category['user_id']

        query: TransactionCategories = TransactionCategories(
            user_id=user_id,
            category_sort=category_sort,
            category_name=category_name
        )
        session.add(query)
        session.commit()
        logger.debug(f'Категория пользователя {user_id} добавлена')

    except Exception as error:
        logger.warning(error)


def get_user_categories(user_id, category_sort) -> list:
    '''
        получаем категории пользователя
    '''
    user_category: List = []
    try:
        request: List[TransactionCategories] = session.query(
            TransactionCategories).filter(
            and_(or_(TransactionCategories.user_id == user_id,
                     TransactionCategories.user_id == 0),
                 (TransactionCategories.category_sort == category_sort))).all()

        for item in request:
            user_category.append(item.category_name)

    except Exception as error:
        logger.warning(error)

    return user_category


def insert_transaction(user_data) -> None:
    """
        добавляем транзакцию
    """
    try:
        query: Transactions = Transactions(
            user_id=user_data['user_id'],
            transaction_sort=user_data['transaction_sort'],
            transaction_category_name=user_data['transaction_category_name'],
            transaction_sum=user_data['transaction_sum'],
            transaction_comment=user_data['transaction_comment'],
            transaction_date=user_data['transaction_date']
        )

        session.add(query)
        session.commit()
        logger.debug(f'Транзакция добавлена')
    except Exception as error:
        logger.warning(error)


def get_transactions_on_date(request: str, user_id: int) -> str:
    """
        получаем все транзакции пользователя по дате
    """
    day: bool = False
    try:
        if request == 'сегодня':
            date: str = datetime.now().strftime(DATE_FORMAT)
            day = True
        elif request == 'вчера':
            date: str = (
                datetime.now() -
                timedelta(
                    days=1)).strftime(DATE_FORMAT)
            day = True
        elif request == 'месяц':
            date: str = datetime.now().strftime('%m.%Y')
        elif request == 'год':
            date: str = datetime.now().strftime('%Y')
        elif re.match(r'^(0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[0-2]).\d{4}$',
                      request):
            date: str = request
            day = True
        elif re.match(r'^(0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[0-2]).\d{4} - (0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[0-2]).\d{4}$',
                      request):
            date: str = request
        else:
            return 'Я вас не понял, вы уверены, что все правильно ввели?'

        data_to_answer: list = get_transactions_from_db(date, user_id)
        formed_answer, detail = get_formed_report(data_to_answer, request)

    except Exception as error:
        logger.warning(error)
        formed_answer: str = 'Не удалось сформировать отчет. Мы уже работаем\
 над решением проблемы.'
    if day:
        formed_answer: str = formed_answer + detail

    return formed_answer


def get_transactions_from_db(date, user_id) -> list:
    """
        получаем транзакции пользователя по дате
    """
    data_to_answer: list = []
    try:
        date_left: str = date.split(' - ')[0]
        date_right: str = date.split(' - ')[1]
        transactions = session.query(Transactions).filter(
            Transactions.transaction_date.between(date_left, date_right)).all()
    except BaseException:
        transactions: List[Transactions] = session.query(Transactions).filter(
            and_(Transactions.user_id == user_id,
                 Transactions.transaction_date.ilike(f'%{date}%')
                 )).all()
    for i in transactions:
        data_to_answer.append({
            'sort': i.transaction_sort,
            'category': i.transaction_category_name,
            'sum': i.transaction_sum,
            'comment': i.transaction_comment
        })

    return data_to_answer


def get_formed_report(data_to_answer, report_date) -> str:
    """
        формируем отчет по транзакциям
    """
    expanse_sum: int = 0
    income_sum: int = 0
    expanses_transactions: dict = {}
    incomes_transactions: dict = {}
    expanses: list = []
    incomes: list = []
    all_transactions: list = []

    for transaction in data_to_answer:
        category: str = transaction['category']
        trans_sum: int = transaction['sum']
        sort: str = transaction['sort']
        comment: str = transaction['comment']

        all_transactions.append(
            f'{sort} {category} {trans_sum} руб. | {comment}\n')

        if sort == 'расход':
            expanse_sum += trans_sum
            if category not in expanses_transactions:
                expanses_transactions[category] = []
            expanses_transactions[category].append(trans_sum)
        elif sort == 'доход':
            income_sum += trans_sum
            if category not in incomes_transactions:
                incomes_transactions[category] = []
            incomes_transactions[category].append(trans_sum)

    for category, transactions in expanses_transactions.items():
        expanses.append(f'{category} {sum(transactions)} руб.\n')

    for category, transactions in incomes_transactions.items():
        incomes.append(f'{category} {sum(transactions)} руб.\n')

    answer: str = f'''
Отчет за {report_date}:
Всего доход: {income_sum} руб.
{''.join(incomes)}
Всего расход: {expanse_sum} руб.
{''.join(expanses)}
Итого: {income_sum + expanse_sum} руб.
'''

    detail: str = 'Детализация:\n' + ''.join(all_transactions)

    return answer, detail


def get_users_list() -> list:
    """
        получаем список пользователей
    """
    users_list: list = []
    query: list = session.query(UsersSubscribes.user_id).filter(
        UsersSubscribes.subscribe == 1).all()
    for i in query:
        users_list.append(i[0])

    return users_list


def change_user_subscribe_status(user_id: int) -> None:
    """
        меняем статус подписки пользователя
    """
    try:
        status: int = session.query(UsersSubscribes).filter(
            UsersSubscribes.user_id == user_id).first().subscribe
        if status == 1:
            status = 0
        elif status == 0:
            status = 1
        session.query(UsersSubscribes).filter(
            UsersSubscribes.user_id == user_id).update(
                {'user_id': user_id, 'subscribe': status},
                synchronize_session='fetch')
    except BaseException:
        session.add(UsersSubscribes(user_id=user_id, subscribe=1))
        status: int = 1

    session.commit()

    return status


print(get_users_list())
