import logging
import re
import requests

from lxml import html

from ..utils import parse_date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'ultimahora.com'
DOCUMENT_URL = 'http://www.ultimahora.com/asdf-n{}.html'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.ultimahora.com')
    link_re = re.compile(r'.*/[-\w]+-n(\d+).html')

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
    # Check if redirected to the main page.
    if response.url.endswith('www.ultimahora.com'):
        return {'outcome': 'notfound'}

    # Check if the response is valid.
    if response.status_code == 404:
        return {'outcome': 'notfound'}
    elif response.status_code >= 400:
        logger.debug("request to %s returned status_code = %s",
                     response.url, response.status_code)
        return {'outcome': 'failure'}

    root = html.fromstring(response.content)

    try:
        title = root.cssselect('div.news-headline-obj > h1.t1')[0]\
                    .text_content().strip()
        summary = root.cssselect('div.news-headline-obj > h2.summary')[0]\
                      .text_content().strip()
        text = u'\n'.join(map(
            lambda node: node.text_content().strip(),
            root.cssselect('div.news-detail-obj p')
        ))

        content = u'\n'.join([title, summary, text]).strip()
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Paraguay']
    }

    return result


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root.cssselect('div.news-headline-obj > h1.t1')[0]\
                                .text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect(
            'div.news-headline-obj > div.cols1 div.floatright'
        )[0].text_content().strip()
        date = parse_date(raw_date)
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
