import logging
import re
import requests

from lxml import html


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'informador.com.mx'
DOCUMENT_URL = 'http://www.informador.com.mx/mexico/2015/{}/6/asdf.htm'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.informador.com.mx')
    link_re = re.compile(r'[^/]*/\w+/\d+/(\d+)/')

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

    root = html.fromstring(response.content)

    try:
        title = root.cssselect('div.tituloInt > h1')[0].text_content().strip()
        article = root.cssselect('div.textoNoticia')[0].text_content()
        content = u'\n'.join([title, article])
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Mexico']
    }

    return result


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}

    # No date present, just title.
    try:
        metadata['title'] = root.cssselect('div.tituloInt > h1')[0]\
                                .text_content().strip()
    except:
        pass

    return metadata
