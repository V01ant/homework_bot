import os

from dotenv import load_dotenv

load_dotenv()
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

EXPECTED_LENGTH_TELEGRAM_CHAT_ID = 9

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

RETRY_PERIOD = 600

DOMAIN = 'https://practicum.yandex.ru'
SLUG = 'api/user_api/homework_statuses'
ENDPOINT = f'{DOMAIN}/{SLUG}/'

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
