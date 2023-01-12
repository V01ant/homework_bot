import os
import telegram
import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
import time
from http import HTTPStatus
import requests
import exceptions
import telegram # Потом тут надо будет импортировать бота отдельно.
from telegram.ext import Updater
from pprint import pprint


from dotenv import load_dotenv

load_dotenv()
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')



RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler()
logger.addHandler(handler)

def check_tokens():
    """Проверка доступности переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if all(tokens):
        return True
    logger.critical('Проблема с переменными окружения.')
    return False


def send_message(bot, message):
    """Отправка сообщения в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Успешная отправка сообщения.')
    except Exception:
        logger.error('Ошибка отправки сообщения!')
        raise exceptions.TestException('Ошибка отправки сообщения!')
    # if telegram.error.TelegramError('Something wrong'):
    #     logger.error('Ошибка отправки сообщения.')
        # raise exceptions.TestException('ooooooooooooooooooooo')


def get_api_answer(timestamp):
    """Запрос к API-сервиса и приведение ответа к типам данных Python."""
    payload = {'from_date': timestamp}
    try:    
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException:
        logger.error('Возникло исключение requests.RequestException()')

    if response.status_code != HTTPStatus.OK:
        raise exceptions.TestException('Эндпоинт недоступен!')

    return response.json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""

    print(response)
    print(type(response))

    if 'homeworks' not in response:
        raise TypeError('Отсутствует ключ homeworks')
        # logger.debug('Ключ присутствует в ответе!')

    if type(response['homeworks']) is not list:
        raise TypeError('Неверный тип homeworks')
        # logger.debug('По ключу передаётся список')

    if type(response['homeworks'][0]) is not dict:
        raise TypeError('Неверный тип homeworks')

    if type(response['current_date']) is not int:
        raise TypeError('Неверный тип current_date')

    if type(response) is not dict:
        raise TypeError('Неверный тип response')

    return True


def parse_status(homework):
    """Проверка статуса работы."""
    # if 'homework_name' != list(homework.keys())[1]:
    if not list(homework.keys()).count('homework_name'):
        raise KeyError(f'Ключ homework_name отсутствует в ответе API')
    homework_name = homework.get('homework_name')

    if not list(HOMEWORK_VERDICTS.keys()).count(homework['status']):
        raise KeyError(f'Недокументированный статус в ответе API')

    verdict = HOMEWORK_VERDICTS[homework.get('status')]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    logger.info('Начало работы')



    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    # timestamp = int(time.time()) # Получает текущее значение времени в формате Unix time
    # timestamp = 1671504050
    timestamp = 0

    # bot.send_message(TELEGRAM_CHAT_ID, logger.info('Начало работы!'))

    while True:
        if not check_tokens():
            break
        try:
            logger.info('совершаем запрос')
            response = get_api_answer(timestamp)
            if check_response(response):
                logger.info('парсим статус')
                message = parse_status(response['homeworks'][0])
                logger.info('отправляем сообщение')
                send_message(bot, message)


        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(error, exc_info=True)
            send_message(bot, message)
        finally:
            logger.info('Ожидание')
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
