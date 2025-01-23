import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    BASE_DIR,
    DATETIME_FORMAT,
    RESULTS_DIR,
    PRETTY_MODE,
    FILE_MODE
)
from utils import make_nested_dir


RESULT_FILENAME = '{parser_mode}_{timestamp}.csv'
SAVED_MESSAGE = 'Файл с результатами был сохранён: {file_path}'

logger = logging.getLogger(__name__)


def default_output(results, *args):
    for row in results:
        print(*row)


def pretty_output(results, *args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = make_nested_dir(RESULTS_DIR, BASE_DIR)
    file_path = results_dir / RESULT_FILENAME.format(
        parser_mode=cli_args.mode,
        timestamp=dt.datetime.now().strftime(DATETIME_FORMAT)
    )
    with open(file_path, 'w', encoding='utf-8') as f:
        csv.writer(f, dialect=csv.unix_dialect).writerows(results)
    logger.info(SAVED_MESSAGE.format(file_path=file_path))


OUTPUT_MODES = {
    PRETTY_MODE: pretty_output,
    FILE_MODE: file_output,
    None: default_output
}


def control_output(results, cli_args):
    OUTPUT_MODES[cli_args.output](results, cli_args)
