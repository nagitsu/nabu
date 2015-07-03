import logging
import re
import requests

from lxml import html

from nabu.corpus.utils import parse_date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'abc.com.py'
DOCUMENT_URL = 'http://www.abc.com.py/asdf/asdf/Asdf-{}.html'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.abc.com.py/')
    link_re = re.compile(r'.*/\w+/[a-zA-Z\-]*(\d+).html')

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
    # Check if redirected to `/404/`.
    if "/404/" in response.url:
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
        title = root.cssselect('#article > h1')[0].text_content().strip()
        summary = root.cssselect('#article > p.summary')[0]\
                      .text_content().strip()
        text = u'\n'.join([
            node.text_content().strip()
            for node in root.cssselect('#article > div.text > p')
        ])

        # Old-style articles.
        if not text.strip():
            text = root.cssselect('#article > div.text')[0].text_content()

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
        metadata['title'] = root.cssselect('#article > h1')[0]\
                                .text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect('#article > h3')[0].text_content().strip()
        date = parse_date(raw_date)
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
