import logging
import re
import requests

from lxml import html

from nabu.corpus.utils import parse_date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'tuloescribes.com'
DOCUMENT_URL = 'http://www.tuloescribes.com/index.php?leng=es&idescrito={}'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.tuloescribes.com/')
    link_re = re.compile(r'.*idescrito=(\d+)')

    root = html.fromstring(response.content)
    links = root.cssselect("h3 a.titulo")
    ids = []
    for link in links:
        m = link_re.match(link.get('href', ''))
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
        title = root.cssselect('td.contenidos h1')[0].text_content().strip()
        text = ''.join(
            root.xpath('//td[@class="contenidos"]/text()')
        ).strip(' |\n\r')

        content = u'\n'.join([title, text]).strip()
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['amateur_writing']
    }

    return result


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root.cssselect(
            'td.contenidos h1')[0].text_content().strip()
    except:
        pass

    try:
        raw_date = root.xpath(
            '//div[@class="cajaHerramientas"]/span/text()[2]'
        )[0].strip()
        date = parse_date(raw_date)
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
