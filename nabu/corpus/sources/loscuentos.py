import logging
import re
import requests

from lxml import html

from nabu.corpus.utils import parse_date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'loscuentos.net'
DOCUMENT_URL = 'http://www.loscuentos.net/cuentos/link/{}/'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.loscuentos.net/')
    link_re = re.compile(r'.*/link/\d*?/(\d+)/')

    root = html.fromstring(response.content)
    links = root.xpath("//table//a/@href")
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
        base_title = root.cssselect('font.pt')[0].text_content()
        title = base_title.split('/')[-1].strip()
        text = ' '.join([
            p.text_content() for p in root.cssselect('td.nt p')
        ]).strip()

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
        base_title = root.cssselect('font.pt')[0].text_content()
        metadata['title'] = base_title.split('/')[-1].strip()
    except:
        pass

    try:
        raw_date = root.cssselect('p.nt b')[0].text_content()
        date = parse_date(
            re.findall(r'agregado el (.*?\d),', raw_date)[0]
        )
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
