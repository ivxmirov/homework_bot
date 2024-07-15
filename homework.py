import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

# Промежуток времени в секундах, соответствующий двум неделям.
REQUEST_PERIOD = 604800

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler('my_logger.log')
logger.addHandler(handler)


def check_tokens():
    """
    Проверь доступность переменных окружения.

    Проверяет доступность переменных окружения, которые необходимы для работы
    программы. Если отсутствует хотя бы одна переменная окружения — продолжать
    работу бота нет смысла.
    """
    tokens = PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    if not all(tokens):
        logger.critical('Отсутствуют переменные окружения.')
        raise sys.exit('Отсутствуют переменные окружения.')


def send_message(bot, message):
    """
    Отправь сообщение.

    Отправляет сообщение в Telegram-чат, определяемый переменной окружения
    TELEGRAM_CHAT_ID. Принимает на вход два параметра: экземпляр класса
    TeleBot и строку с текстом сообщения.
    """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logger.error(error, exc_info=True)
    else:
        logger.debug('Сообщение успешно отправлено')


def get_api_answer(timestamp):
    """
    Получи ответ API.

    Делает запрос к единственному эндпоинту API-сервиса. В качестве параметра
    в функцию передаётся временная метка. В случае успешного запроса должна
    вернуть ответ API, приведя его из формата JSON к типам данных Python.
    """
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=payload
        )
    except Exception as error:
        logger.error(error, exc_info=True)
    else:
        if homework_statuses.status_code != HTTPStatus.OK:
            logger.error('Сбой при запросе к эндпоинту', exc_info=True)
            raise ConnectionError('Сбой при запросе к эндпоинту')
        return homework_statuses.json()


def check_response(response):
    """
    Проверь ответ API.

    Проверяет ответ API на соответствие документации из урока «API сервиса
    Практикум Домашка». В качестве параметра функция получает ответ API,
    приведённый к типам данных Python.
    """
    if not isinstance(response, dict):
        raise TypeError('Структура данных не соответствует ожиданиям')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Данные под ключом "homeworks" не являются списком')
    return homeworks


def parse_status(homework):
    """
    Извлеки статус.

    Извлекает из информации о конкретной домашней работе статус этой работы.
    В качестве параметра функция получает только один элемент из списка
    домашних работ. В случае успеха функция возвращает подготовленную для
    отправки в Telegram строку, содержащую один из вердиктов словаря
    HOMEWORK_VERDICTS.
    """
    if 'homework_name' not in homework:
        logger.error('В ответе отсутствует ключ "homework_name"')
        raise KeyError('В ответе отсутствует ключ "homework_name"')
    if 'status' not in homework:
        logger.error('В ответе отсутствует ключ "status"')
        raise KeyError('В ответе отсутствует ключ "status"')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        logger.error('Неизвестный статус домашней работы')
        raise KeyError('Неизвестный статус домашней работы')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - REQUEST_PERIOD
    status_before_checking = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                homework = homeworks[0]
                status_after_checking = homework['status']
            else:
                message = 'У вас нет домашних работ на проверке'
            if status_after_checking != status_before_checking:
                status_before_checking = status_after_checking
                message = parse_status(homework)
            else:
                logging.debug('Статус работы не изменился')
                message = 'Статус работы не изменился'
            send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
        finally:
            logger.debug(
                f'Ожидаем паузу {RETRY_PERIOD} с перед новым запросом'
            )
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
