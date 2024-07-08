import os
from datetime import time
from dotenv import load_dotenv
from telebot import TeleBot

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
    """
    Проверь доступность переменных окружения.

    Проверяет доступность переменных окружения, которые необходимы для работы
    программы. Если отсутствует хотя бы одна переменная окружения — продолжать
    работу бота нет смысла.
    """
    ...


def send_message(bot, message):
    """
    Отправь сообщение.

    Отправляет сообщение в Telegram-чат, определяемый переменной окружения
    TELEGRAM_CHAT_ID. Принимает на вход два параметра: экземпляр класса
    TeleBot и строку с текстом сообщения.
    """
    ...


def get_api_answer(timestamp):
    """
    Получи ответ API.

    Делает запрос к единственному эндпоинту API-сервиса. В качестве параметра
    в функцию передаётся временная метка. В случае успешного запроса должна
    вернуть ответ API, приведя его из формата JSON к типам данных Python.
    """
    ...


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
    ...

    # Создаем объект класса бота
    bot = ...
    timestamp = int(time.time())

    time.sleep(RETRY_PERIOD)

    while True:
        try:

            ...

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()
