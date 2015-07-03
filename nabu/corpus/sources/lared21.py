import logging
import re
import requests

from lxml import html

from nabu.corpus.utils import parse_date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'lr21.com.uy'
DOCUMENT_URL = 'http://www.lr21.com.uy/politica/{}-f32as23cdsa'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.lr21.com.uy')
    link_re = re.compile(r'.*/[0-9a-z-]+/(\d+)-[0-9a-z-]+')

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

    root = html.fromstring(response.content)

    try:
        title = root.xpath(
            '//h1[contains(@itemprop, "headline") '
            'or contains(@id, "article-title")]'
        )[0].text_content()

        try:
            summary = root.xpath(
                '//h2[contains(@itemprop, "description")]'
            )[0].text_content()
        except IndexError:
            # No summary found. Doesn't matter, it's optional.
            summary = ""

        article = root.xpath(
            '//div[contains(@itemprop, "articleBody")]'
        )[0].text_content()

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
        metadata['title'] = root.xpath(
            '//h1[contains(@itemprop, "headline") '
            'or contains(@id, "article-title")]'
        )[0].text_content()
    except:
        pass

    try:
        raw_date = root.xpath(
            '//meta[@itemprop="datePublished"]'
        )[0].get('content')
        date = parse_date(raw_date.strip())
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
