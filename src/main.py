from urllib.parse import urljoin
import logging
import re

from bs4 import BeautifulSoup
from tqdm import tqdm
import requests_cache


from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    EXPECTED_STATUS,
    LATEST_VERSIONS_HEADLINES,
    MAIN_DOC_URL,
    PEP_HEADLINES,
    PEP_URL,
    WHATS_NEW_HEADLINES,
)
from exceptions import ParserNotFindException
from outputs import control_output
from utils import get_response, find_tag


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

logger = logging.getLogger(__name__)


def whats_new(session):
    results = [WHATS_NEW_HEADLINES]
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    main_div = find_tag(
        soup=BeautifulSoup(response.text, 'lxml'),
        tag='section',
        attrs={'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        soup=main_div,
        tag='div',
        attrs={'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})
    for section in tqdm(sections_by_python, desc='Searching progress'):
        version_link = urljoin(whats_new_url, section.find('a')['href'])
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        results.append((
            version_link,
            find_tag(soup, 'h1').text,
            find_tag(soup, 'dl').text.replace('\n', ' ')
        ))
    return results


def latest_versions(session):
    results = [LATEST_VERSIONS_HEADLINES]
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    sidebar = find_tag(
        soup=BeautifulSoup(response.text, 'lxml'),
        tag='div',
        attrs={'class': 'sphinxsidebarwrapper'}
    )
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
    response = get_response(session, downloads_url)
    if response is None:
        return
    main_tag = find_tag(
        BeautifulSoup(response.text, 'lxml'),
        'div', {'role': 'main'}
    )
    table_tag = find_tag(
        soup=main_tag,
        tag='table',
        attrs={'class': 'docutils'}
    )
    pdf_a4_tag = find_tag(
        soup=table_tag,
        tag='a',
        attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / archive_url.split('/')[-1]
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(SAVED_MESSAGE.format(path=archive_path))


def find_statuses_and_links(session):
    response = get_response(session, PEP_URL)
    if response is None:
        return
    return [
        {
            'status_preview': find_tag(row, tag='abbr').text[1:],
            'link': find_tag(row, tag='a')['href']
        }
        for table in find_tag(
            soup=BeautifulSoup(response.text, 'lxml'),
            tag='section',
            attrs={'id': 'index-by-category'}
        ).find_all('tbody')
        for row in table.find_all('tr')
    ]


def check_status(session, status_preview, url):
    response = get_response(session, url)
    if response is None:
        return
    status = BeautifulSoup(response.text, 'lxml').find(
        string="Status").parent.find_next_sibling().text
    expected = EXPECTED_STATUS[status_preview]
    if status not in expected:
        logger.info(STATUS_MISMATCH.format(
            url=url, status=status, expected=expected))
    return status


def pep(session):
    results = [PEP_HEADLINES]
    quantity_per_status = dict()
    for result in tqdm(find_statuses_and_links(session)):
        status = check_status(
            session=session,
            status_preview=result['status_preview'],
            url=urljoin(PEP_URL, result['link'])
        )
        if status not in quantity_per_status:
            quantity_per_status[status] = 0
        quantity_per_status[status] += 1
    quantity_per_status['Total'] = sum(quantity_per_status.values())
    results.extend((key, str(value))
                   for key, value in quantity_per_status.items())
    return results


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
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    try:
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as error:
        message = ERROR_MESSAGE.format(error=error)
        logger.error(message, exc_info=True)
    logger.info(PARSER_FINISHED)


if __name__ == '__main__':
    configure_logging()
    main()
