import os
import telegram
import time
import requests
import telegram 
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


def check_tokens():
    """Проверка доступности переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if all(tokens):
        return True
    return False


def send_message(bot, message):
    """Отправка сообщения в чат."""
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(timestamp):
    """Запрос к API-сервиса и приведение ответа к типам данных Python."""
    payload = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    return response.json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    if type(response) is dict and response['homeworks']:
        return True
    return False


def parse_status(homework):
    """Проверка статуса работы."""
    homework_name = homework['homeworks'][0].get('homework_name')
    verdict = HOMEWORK_VERDICTS[homework['homeworks'][0].get('status')]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    # timestamp = int(time.time()) # Получает текущее значение времени в формате Unix time
    timestamp = 1671504050

    print('Начало работы')
    check_tokens()

    while True:
        try:
            print('совершаем запрос')
            response = get_api_answer(timestamp)
            if check_response(response):
                print('парсим статус')
                message = parse_status(response)
                print('отправляем сообщение')
                send_message(bot, message)


        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        finally:
            print('ждём 10 секунд')
            time.sleep(10)


if __name__ == '__main__':
    main()
