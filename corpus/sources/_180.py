import logging
import re
import requests

from datetime import datetime
from lxml import html


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = '180.com.uy'
DOCUMENT_URL = 'http://www.180.com.uy/articulo/{}'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.180.com.uy')
    link_re = re.compile(r'.*/articulo/(\d+)')

    root = html.fromstring(response.content)
    links = root.xpath("//a[@class='linkArticulo']/@href")
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
    if response.status_code == 404:
        return {'outcome': 'notfound'}
    elif response.status_code >= 400:
        logger.debug("request to %s returned status_code = %s",
                     response.url, response.status_code)
        return {'outcome': 'failure'}

    root = html.fromstring(response.content)

    try:
        title = root.cssselect('.text > h3')[0].text_content().strip()
        summary = root.cssselect('.text > h4')[0].text_content().strip()
        article = root.cssselect('.nota > article')[0].text_content().strip()
        content = u'\n'.join([title, summary, article]).strip()
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Uruguay']
    }

    return result


def _parse_date(date):
    """
    Parses dates from 180.com.uy.
    Example: "Actualizado: 13 de Agosto de 2014 | Por: Redaccion 180".
    """
    spanish_months = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5,
        'junio': 6, 'julio': 7, 'agosto': 8, 'setiembre': 9, 'octubre': 10,
        'noviembre': 11, 'diciembre': 12,
    }

    match = re.match('.* (\d+) de (\w+) de (\d+) |', date)
    if match:
        day = int(match.group(1))
        month = spanish_months[match.group(2).lower()]
        year = int(match.group(3))

        return datetime(year, month, day)


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root.cssselect('.text > h3')[0]\
                                .text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect('p.publicado')[0].text_content().strip()
        date = _parse_date(raw_date.strip())
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
