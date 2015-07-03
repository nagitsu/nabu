import logging
import re
import requests

from lxml import html

from nabu.corpus.utils import parse_date, was_redirected


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'fortunaweb.com.ar'
DOCUMENT_URL = 'http://fortunaweb.com.ar/2015-03-01-{}-asdf/'


def get_missing_ids(existing_ids):
    response = requests.get('http://fortunaweb.com.ar/')
    link_re = re.compile(r'.*/\d+-\d+-\d+-(\d+)-\w+')

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
    if response.status_code == 404:
        return {'outcome': 'notfound'}
    elif response.status_code >= 400:
        logger.debug("request to %s returned status_code = %s",
                     response.url, response.status_code)
        return {'outcome': 'failure'}

    # Now check if the redirection history changed our ID.
    if was_redirected(response, regexp=r'.*/\d+-\d+-\d+-(\d+)-\w+'):
        return {'outcome': 'notfound'}

    root = html.fromstring(response.content)

    try:
        title = root.cssselect('#contenido-general-articulo > header > h1')[0]\
                    .text_content().strip()
        summary = root.cssselect('header > #descripcion')[0]\
                      .text_content().strip()
        text = u' '.join(root.xpath("//section[@id='content']//p//text()"))

        content = u'\n'.join([title, summary, text]).strip()
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Argentina']
    }

    return result


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root.cssselect(
            '#contenido-general-articulo > header > h1'
        )[0].text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect('div.dia-publicacion')[0]\
                       .text_content().strip()
        date = parse_date(raw_date)
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
