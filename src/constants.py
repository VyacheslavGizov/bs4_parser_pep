from pathlib import Path

# Ссылки
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'

# Директории и файлы
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = 'downloads'
RESULTS_DIR = 'results'
LOG_DIR = 'logs'
LOG_FILENAME = 'parser.log'

# Режимы вывода данных
PRETTY_MODE = 'pretty'
FILE_MODE = 'file'


DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
