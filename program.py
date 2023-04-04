import os
from pathlib import Path
from time import sleep
from urllib.error import HTTPError
import logging
import sys

import requests
from dotenv import load_dotenv

from exceptions import (InvalidEnvs, InvalidDict, EmptyListError,
                        InvalidStatus, InvalidMessage)

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(Path(BASE_DIR, '.env'))

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
URL = os.getenv('URL')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

TIMEOUT = 20

last_status = [None]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    filename='program.log',
    filemode='a'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def check_tokens() -> None:
    """Проверяет доступность переменных окружения"""
    required_envs = (
        'PRACTICUM_TOKEN',
        'URL',
        'TELEGRAM_TOKEN',
        'TELEGRAM_CHAT_ID'
    )
    for env in required_envs:
        if os.getenv(env) is None:
            raise InvalidEnvs(f'env with key {env} is absent')


def get_api_answer() -> dict:
    """Возвращает ответ на запрос в формате JSON"""
    headers = {'Authorization': PRACTICUM_TOKEN}
    payload = {'from_date': 0}
    try:
        homework_statuses = requests.get(URL, headers=headers, params=payload)
        return homework_statuses.json()
    except (ConnectionError, HTTPError, TimeoutError) as error:
        logger.error(f'Network error: {error}')
    except ValueError as error:
        logger.error(f'Validation error: {error}')
    except Exception as error:
        logger.error(f'Unknown error: {error}')


def check_response(response) -> dict:
    """Проверяет ответ на соответствие документации"""
    check_tuple = ('current_date', 'homeworks')
    if not isinstance(type(response), dict()):
        logger.error('answer is not dict')
        raise TypeError('answer is not dict')
    if set(check_tuple).intersection(set(response.keys())) != set(check_tuple):
        raise InvalidDict(
            'Not all mandatory parameters are present in the dictionary.'
        )
    if len(response['homeworks']) == 0:
        raise EmptyListError(
            'The request issued an empty carriage of housework'
        )
    return response


def parse_status() -> str | None:
    """Проверяет статус и в случае смены статуса возвращает строку"""
    data = check_response(get_api_answer())
    homework_name = data['homeworks'][0]['homework_name']
    status = data['homeworks'][0]['status']
    status_tuple = ('reviewing', 'approved', 'rejected')
    if status is not status_tuple:
        raise InvalidStatus('An erroneous status of homework')
    if status != last_status[0]:
        last_status[0] = status
        return f'{homework_name}: {status}'
    return None


def send_message(timeout: int):
    """Отправляет сообщение в телеграмм"""
    while True:
        message = parse_status()
        if message is not None:
            url = (f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?"
                   f"chat_id={TELEGRAM_CHAT_ID}&text={message}")
            try:
                requests.get(url)
                logger.debug('The message is gone')
            except InvalidMessage as error:
                logger.error(f'Unknown error: {error}')
        sleep(timeout)


def main():
    check_tokens()
    send_message(TIMEOUT)


if __name__ == '__main__':
    main()
