import logging
import logging.config
import time
from http import HTTPStatus

import requests
import telegram

import exceptions
from constants import (HOMEWORK_VERDICTS, PRACTICUM_TOKEN, RETRY_PERIOD,
                       TELEGRAM_CHAT_ID, TELEGRAM_TOKEN, ENDPOINT, HEADERS,
                       EXPECTED_LENGTH_TELEGRAM_CHAT_ID,)

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


def check_tokens():
    """Проверка доступности переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if all(tokens):
        response = requests.get(ENDPOINT).json()
        if response.get('code') == 'not_authenticated':
            logger.info(
                'Проверка доступности эндпоинта yandex прошла успешно: '
                f'{response.get("code")}'
            )
        else:
            logger.critical(
                'При неавторизованном запросе к эндпоиту '
                'ответ API не содержит ожидаемого значения: '
                f'not_authenticated. Ответ API: {response}'
            )
            return False
        if len(TELEGRAM_CHAT_ID) != EXPECTED_LENGTH_TELEGRAM_CHAT_ID:
            logger.critical(
                'Ошибка в TELEGRAM_CHAT_ID! '
                f'Текущая длина: {len(TELEGRAM_CHAT_ID)}, '
                f'Требуемая длина: {EXPECTED_LENGTH_TELEGRAM_CHAT_ID}'
            )
            return False
        return True


def send_message(bot, message):
    """Отправка сообщения в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Успешная отправка сообщения!')
    except Exception:
        logger.error('Ошибка отправки сообщения!')
        raise exceptions.TestException('Ошибка отправки сообщения!')


def get_api_answer(timestamp):
    """Запрос к API-сервиса и приведение ответа к типам данных Python."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException:
        logger.error(
            f'Возникло исключение requests.RequestException()! '
            f'Эндпоинт: {ENDPOINT} '
            f'Время запроса: {timestamp}'
        )
    if response.status_code != HTTPStatus.OK:
        logger.error('Сбой при обращении к эндпоинту!')
        raise exceptions.TestException('Сбой при обращении к эндпоинту!')
    return response.json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    if 'homeworks' not in response:
        logger.error('В ответе API отсутствует ключ "homeworks"!')
        raise TypeError('В ответе API отсутствует ключ "homeworks"!')
    if type(response['homeworks']) is not list:
        logger.error('По ключу "homeworks" передаётся не список!')
        raise TypeError('По ключу "homeworks" передаётся не список!')
    if len(response['homeworks']) == 0:
        logger.debug('Список работ пуст!')
        raise ValueError('Список работ пуст!')
    return response['homeworks'][0]


def parse_status(homework):
    """Проверка статуса работы."""
    if not list(homework.keys()).count('homework_name'):
        logger.error('Ключ homework_name отсутствует в ответе API.')
        raise KeyError('Ключ homework_name отсутствует в ответе API.')
    homework_name = homework.get('homework_name')
    if not list(HOMEWORK_VERDICTS.keys()).count(homework['status']):
        logger.error('Недокументированный статус в ответе API.')
        raise KeyError('Недокументированный статус в ответе API.')
    verdict = HOMEWORK_VERDICTS[homework.get('status')]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logger.info('Начало работы.')
    logger.info('Инициализация бота.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    buffer_message = ''
    error_message = ''

    while True:
        logger.info('Проверка переменных окружения.')
        if not check_tokens():
            logger.critical('Ошибка в переменных окружения!')
            break
        timestamp = 0
        try:
            logger.info('Запрос к API-сервиса.')
            response = get_api_answer(timestamp)
            logger.info('Проверка ответа API на соответствие документации.')
            response = check_response(response)
            logger.info('Проверка статуса работы.')
            message = parse_status(response)
            logger.info(
                'Проверка сообщения в промежуточной переменной статуса.'
            )
            if buffer_message != message:
                logger.info('Отправка сообщения.')
                send_message(bot, message)
                logger.info(
                    'Сохранение сообщения в промежуточную переменную статуса.'
                )
                buffer_message = message
            else:
                logger.debug(f'Статус работы не изменился: {buffer_message}')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(error, exc_info=True)
            logger.info(
                'Проверка сообщения в промежуточной переменной ошибок.'
            )
            if error_message != message:
                logger.info('Отправка сообщения об ошибке.')
                send_message(bot, message)
                logger.info(
                    'Сохранение сообщения об ошибке '
                    'в промежуточную переменную.'
                )
                error_message = message
        finally:
            logger.info('Ожидание.')
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
