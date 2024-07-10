import logging
import os
import requests
import time
from dotenv import load_dotenv
from http import HTTPStatus
from telebot import TeleBot

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

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
    tokens = (
        ('PRACTICUM_TOKEN', PRACTICUM_TOKEN),
        ('TELEGRAM_TOKEN', TELEGRAM_TOKEN),
        ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID)
    )
    all_tokens_present = True
    missing_tokens = []
    for token_name, token_value in tokens:
        if not token_value:
            all_tokens_present = False
            missing_tokens.append(token_name)
    if not all_tokens_present:
        logger.critical(
            f'Отсутствуют следущие переменные окружения: '
            f'{", ".join(missing_tokens)}'
        )
        raise KeyError('Не хватает переменных окружения.')


def send_message(bot, message):
    """
    Отправь сообщение.

    Отправляет сообщение в Telegram-чат, определяемый переменной окружения
    TELEGRAM_CHAT_ID. Принимает на вход два параметра: экземпляр класса
    TeleBot и строку с текстом сообщения.
    """
    chat_id = TELEGRAM_CHAT_ID
    try:
        bot.send_message(chat_id, message)
    except Exception as error:
        logger.error(error, exc_info=True)


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
    ...


def parse_status(homework):
    """
    Извлеки статус.

    Извлекает из информации о конкретной домашней работе статус этой работы.
    В качестве параметра функция получает только один элемент из списка
    домашних работ. В случае успеха функция возвращает подготовленную для
    отправки в Telegram строку, содержащую один из вердиктов словаря
    HOMEWORK_VERDICTS.
    """
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - REQUEST_PERIOD
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = response['homeworks'][0]
            message = parse_status(homework)
            send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
        finally:
            logger.debug(
                'Ожидаем {RETRY_PERIOD} с перед новым запросом'
            )
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
