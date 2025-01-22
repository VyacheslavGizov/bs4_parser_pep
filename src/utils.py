from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException


REQUEST_ERROR = ('Сбой сети! При выполнении GET-запроса на {url} возникла '
                 'ошибка: {error}.')
TAG_NOT_FOUND = 'Не найден тег {tag} {attrs}'


def make_nested_dir(dir_name, base_dir, exist_ok=True):
    result_dir = base_dir / dir_name
    result_dir.mkdir(exist_ok=exist_ok)
    return result_dir


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
    except RequestException as error:
        raise ConnectionError(
            REQUEST_ERROR.format(url=url, error=error)
        )
    response.encoding = encoding
    return response


def get_soup(session, url):
    response = get_response(session, url)
    return response and BeautifulSoup(response.text, 'lxml')


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=({} if attrs is None else attrs))
    if searched_tag is None:
        raise ParserFindTagException(TAG_NOT_FOUND.format(
            tag=tag, attrs=attrs))
    return searched_tag
