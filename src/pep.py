import logging
import re

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin

from constants import PEP_URL
from utils import get_response, find_tag


STATUS_MISMATCH = ('{url}: статус в карточке - {status}, ожидалось {expected}')

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


def find_statuses_and_links(session):
    response = get_response(session, PEP_URL)

    soup = BeautifulSoup(response.text, 'lxml')

    # tables = find_tag(
    #     soup, tag='section', attrs={'id': 'index-by-category'}
    # ).find_all('tbody')

    # может переписать, чтобы использовать прогресс-бар
    # если нет, то суп тоже во включение добавить
    return [
        {
            'status': find_tag(row, tag='abbr').text[1:],
            'link': find_tag(row, tag='a')['href']
        }
        for table in find_tag(
            soup, tag='section', attrs={'id': 'index-by-category'}
        ).find_all('tbody')
        for row in table.find_all('tr')
    ]


def chesk_status(session, status, url):
    """Проверит статуc на странице PEP."""  # переименовать

    response = get_response(session, url)
    soup = BeautifulSoup(response.text, 'lxml')

    pep_status = soup.find(string="Status").parent.find_next_sibling().string
    expected = EXPECTED_STATUS[status]
    if pep_status not in expected:
        print(STATUS_MISMATCH.format(
            url=url, status=pep_status, expected=expected
        ))  # сообщение в логи
    return pep_status


if __name__ == '__main__':
    session = requests_cache.CachedSession()
    counter = dict()
    for result in find_statuses_and_links(session):
        status = chesk_status(session, result['status'],
                              urljoin(PEP_URL, result['link']))
        if status not in counter:
            counter[status] = 0
        counter[status] += 1
    counter['Total'] = sum(counter.values())
    print(counter)
