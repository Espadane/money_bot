import logging
from config import PROJECT_NAME


logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger_handler: logging.FileHandler = logging.FileHandler('money_bot.log')
logger_formatter: logging.Formatter = logging.Formatter(
    f'{PROJECT_NAME}: %(asctime)s - %(levelname)s - \
%(funcName)s: %(lineno)d - %(message)s',
    datefmt='%d.%b.%Y %H:%M')
logger.addHandler(logger_handler)
logger_handler.setFormatter(logger_formatter)
