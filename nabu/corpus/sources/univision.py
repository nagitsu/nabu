import logging
import re
import requests

from lxml import html

from nabu.corpus.utils import parse_date, was_redirected


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
        'tags': ['news', 'Mexico', 'spanish']
    }

    return result


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
        date = parse_date(u' '.join(raw_date.split('|')[1:]))
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
