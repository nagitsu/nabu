import logging
import re
import requests

from dateutil.parser import parse as _parse_date
from lxml import html


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'espectador.com'
DOCUMENT_URL = 'http://www.espectador.com/sociedad/312095/baa2839c23'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.espectador.com')
    link_re = re.compile(r'.*/[a-z-]+/(\d+)/[a-z-]+')

    root = html.fromstring(response.content)
    links = root.xpath("//a[@itemprop='url']/@href")
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
        title = root.cssselect('header > h1')[0].text_content().strip()
        summary = root.cssselect('article > p.copete')[0].text_content()
        article = root.cssselect('article > div.texto')[0].text_content()
        content = u'\n'.join([title, summary, article]).strip()
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Uruguay']
    }

    return result


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root.cssselect('header > h1')[0]\
                                .text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect('time.fecha')[0].get('datetime')
        date = _parse_date(raw_date.strip())
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
