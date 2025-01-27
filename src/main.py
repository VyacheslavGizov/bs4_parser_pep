from collections import defaultdict
from urllib.parse import urljoin
import logging
import re

from tqdm import tqdm
import requests_cache

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    DOWNLOADS_DIR,
    EXPECTED_STATUS,
    MAIN_DOC_URL,
    PEP_URL
)
from exceptions import ParserNotFindException
from outputs import control_output
from utils import (
    find_tag,
    get_soup,
    make_nested_dir,
)


# Сообщения исключений
ERROR_MESSAGE = 'Сбой в работе программы: {error}'
TAG_NOT_FOUND = 'Не найден тег {tag} {attrs}'
DOCS_LINKS_NOT_FOUND = 'Ссылки на документацию Python не найдены'

# Сообщения в журнал
START_PARSER = 'Парсер запущен!'
INPUT_ARGS = 'Аргументы командной строки: {args}'
PARSER_FINISHED = 'Парсер завершил работу.'
SAVED_MESSAGE = 'Архив был загружен и сохранён: {path}'
STATUS_MISMATCH = ('{url}: статус {status}, ожидалось {expected}')
BAD_URL_MESSAGE = 'Сбой при обращении по ссылке {url}: {error}'

WHATS_NEW_HEADLINES = ('Ссылка на статью', 'Заголовок', 'Редактор, автор')
LATEST_VERSIONS_HEADLINES = ('Ссылка на документацию', 'Версия', 'Статус')
PEP_HEADLINES = ('Статус', 'Количество')
PEP_FOOTER = 'Всего'

WARNING = 'warning'
INFO = 'info'


logger = logging.getLogger(__name__)


def whats_new(session):
    results = [WHATS_NEW_HEADLINES]
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)
    link_tags = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1 > a')
    log_records = []
    for link_tag in tqdm(link_tags):
        version_link = urljoin(whats_new_url, link_tag['href'])
        try:
            soup = get_soup(session, version_link)
        except ConnectionError as error:
            log_records.append(BAD_URL_MESSAGE.format(
                url=version_link,
                error=error,
            ))
            continue
        results.append((
            version_link,
            find_tag(soup, 'h1').text,
            find_tag(soup, 'dl').text.replace('\n', ' ')
        ))
    list(map(logger.warning, log_records))
    return results


def latest_versions(session):
    results = [LATEST_VERSIONS_HEADLINES]
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserNotFindException(DOCS_LINKS_NOT_FOUND)
    for a_tag in a_tags:
        text_match = re.search(
            pattern=r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)',
            string=a_tag.text
        )
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((a_tag['href'], version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    archive_url = urljoin(
        downloads_url,
        find_tag(soup, 'div', {'role': 'main'}).select_one(
            'table.docutils td > [href$=\'pdf-a4.zip\']')['href'])
    archive_path = make_nested_dir(
        DOWNLOADS_DIR, BASE_DIR) / archive_url.split('/')[-1]
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logger.info(SAVED_MESSAGE.format(path=archive_path))


def pep(session):
    records_by_levels = {
        WARNING: [],
        INFO: []
    }
    quantity_per_status = defaultdict(int)
    soup = get_soup(session, PEP_URL)
    pep_attrs = [
        {
            'status_preview': find_tag(row, tag='abbr').text[1:],
            'link': find_tag(row, tag='a')['href']
        }
        for table in find_tag(
            soup, 'section', {'id': 'index-by-category'}).find_all('tbody')
        for row in table.find_all('tr')
    ]
    for pep_attr in tqdm(pep_attrs):
        url = urljoin(PEP_URL, pep_attr['link'])
        try:
            soup = get_soup(session, url)
        except ConnectionError as error:
            records_by_levels[WARNING].append(BAD_URL_MESSAGE.format(
                url=url,
                error=error,
            ))
            continue
        status = soup.find(string='Status').parent.find_next_sibling().text
        expected = EXPECTED_STATUS[pep_attr['status_preview']]
        if status not in expected:
            records_by_levels[INFO].append(STATUS_MISMATCH.format(
                url=url,
                status=status,
                expected=expected
            ))
        quantity_per_status[status] += 1
    list(map(logger.warning, records_by_levels[WARNING]))
    list(map(logger.info, records_by_levels[INFO]))
    return [
        PEP_HEADLINES,
        *quantity_per_status.items(),
        (PEP_FOOTER, sum(quantity_per_status.values()))
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    logger.info(START_PARSER)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logger.info(INPUT_ARGS.format(args=args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as error:
        logger.error(ERROR_MESSAGE.format(error=error), exc_info=True)
    logger.info(PARSER_FINISHED)


if __name__ == '__main__':
    configure_logging()
    main()
