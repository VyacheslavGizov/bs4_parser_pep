from logging.handlers import RotatingFileHandler
import argparse
import logging

from constants import BASE_DIR


LOG_FORMAT = ('%(asctime)s - %(name)s - [%(levelname)s] - '
              '%(filename)s: %(funcName)s: %(lineno)s - %(message)s')
LOG_DIR = BASE_DIR / 'logs'
LOG_FILENAME = 'parser.log'
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
        choices=('pretty', 'file'),
        help=OUTPUT_HELP
    )
    return parser


def configure_logging(log_dir=LOG_DIR, log_filename=LOG_FILENAME):
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / log_filename
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5, encoding='utf-8'
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
