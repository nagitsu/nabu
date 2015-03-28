import logging
import re
import requests

from datetime import datetime
from lxml import html

from ..utils import was_redirected


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'univision.com'
DOCUMENT_URL = 'http://noticias.univision.com/article/{}/'


def get_missing_ids(existing_ids):
    response = requests.get('http://noticias.univision.com/')
    link_re = re.compile(r'.*/article/(\d+)/')

    root = html.fromstring(response.content)
    links = root.xpath("//a/@href")
    ids = []
    for link in links:
        m = link_re.match(link)
        if m:
            ids.append(int(m.group(1)))

    last_id = max(ids)

    scraped_ids = set(map(int, existing_ids))
    missing_ids = map(str, set(range(last_id + 1)) - set(scraped_ids))

    return missing_ids


def get_content(response):
    # Check if the response is valid.
    if response.status_code in [404, 500]:
        return {'outcome': 'notfound'}
    elif response.status_code >= 400:
        logger.debug("request to %s returned status_code = %s",
                     response.url, response.status_code)
        return {'outcome': 'failure'}

    if was_redirected(response):
        return {'outcome': 'notfound'}

    root = html.fromstring(response.content)

    try:
        title = root.cssselect('h1.article-header')[0].text_content().strip()
        article = root.cssselect('div.article-text')[0].text_content()
        content = u'\n'.join([title, article])
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Mexico']
    }

    return result


def _parse_date(date):
    english_months = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
    }
    match = re.match(
        '.*\|\s*(\w+)\s*(\d+),\s*(\d+)\s*\|\s*(\d+):(\d+)\s*(\w+)',
        date, flags=re.UNICODE
    )
    if match:
        day = int(match.group(2))
        month = english_months[match.group(1).lower()]
        year = int(match.group(3))

        hour = int(match.group(4))
        minute = int(match.group(5))

        if match.group(6).lower() == 'pm':
            hour = (hour + 12) % 24

        return datetime(year, month, day, hour, minute)


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root.cssselect('h1.article-header')[0]\
                                .text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect('span.author-details')[0].text_content()
        date = _parse_date(raw_date.strip())
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
