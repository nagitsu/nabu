import logging
import re
import requests

from lxml import html

from nabu.corpus.utils import parse_date


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

    # `lxml` doesn't support <meta charset> tags, replace it for http-equiv.
    raw_content = response.content.replace(
        b'<meta charset="utf-8">',
        b'<meta http-equiv="content-type" content="text/html; charset=utf-8"/>'
    )
    root = html.fromstring(raw_content)

    try:
        title = root.cssselect('.main-content .nota .text > h3')[0]\
                    .text_content().strip()
        summary = root.cssselect('.main-content .nota .text > h4')[0]\
                      .text_content().strip()
        article = root.cssselect('.main-content .nota > article')[0]\
                      .text_content().strip()
        content = u'\n'.join([title, summary, article]).strip()
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Uruguay', 'spanish']
    }

    return result


def get_metadata(response):
    # `lxml` doesn't support <meta charset> tags, replace it for http-equiv.
    raw_content = response.content.replace(
        b'<meta charset="utf-8">',
        b'<meta http-equiv="content-type" content="text/html; charset=utf-8"/>'
    )
    root = html.fromstring(raw_content)

    metadata = {}
    try:
        metadata['title'] = root\
            .cssselect('.main-content .nota .text > h3')[0]\
            .text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect('p.publicado')[0].text_content().strip()
        date = parse_date(raw_date.split('|')[0])
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
