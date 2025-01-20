from http import HTTPStatus

from requests import RequestException

from exceptions import ParserFindTagException, UnsuccessfulResponseError


REQUEST_ERROR = ('Сбой сети! При выполнении GET-запроса на {url} возникла '
                 'ошибка: {error}.')
UNSUCCESSFUL_RESPONSE = (
    'Неожиданный статус ответа! При выполнении GET-запроса на {url} '
    'получен ответ с кодом возврата: {response_status}. Ожидаемый код: 200.'
)
TAG_NOT_FOUND = 'Не найден тег {tag} {attrs}'


def get_response(session, url):
    try:
        response = session.get(url)
    except RequestException as error:
        raise ConnectionError(
            REQUEST_ERROR.format(url=url, error=error)
        )
    response_status = response.status_code
    if response_status != HTTPStatus.OK:
        raise UnsuccessfulResponseError(UNSUCCESSFUL_RESPONSE.format(
            url=url, response_status=response_status))
    response.encoding = 'utf-8'
    return response


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(TAG_NOT_FOUND.format(
            tag=tag, attrs=attrs))
    return searched_tag
