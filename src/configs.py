from logging.handlers import RotatingFileHandler
import argparse
import logging

from constants import BASE_DIR, FILE_MODE, LOG_DIR, LOG_FILENAME, PRETTY_MODE
from utils import make_nested_dir


LOG_FORMAT = ('%(asctime)s - %(name)s - [%(levelname)s] - '
              '%(filename)s: %(funcName)s: %(lineno)s - %(message)s')
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

DESCRIPTION = 'Парсер документации Python'
CLEAR_HELP = 'Очистка кеша'
OUTPUT_HELP = 'Дополнительные способы вывода данных'
MODES_HELP = 'Режимы работы парсера'


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        'mode',
        choices=available_modes,
        help=MODES_HELP
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help=CLEAR_HELP
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(PRETTY_MODE, FILE_MODE),
        help=OUTPUT_HELP
    )
    return parser


def configure_logging():
    log_file = make_nested_dir(LOG_DIR, BASE_DIR) / LOG_FILENAME
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5, encoding='utf-8'
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
