import logging
import re
import requests

from lxml import html

from nabu.corpus.utils import parse_date
from nabu.core import settings


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'infobae.com'
DOCUMENT_URL = 'http://www.infobae.com/2015/04/02/{}-asdf'


def get_missing_ids(existing_ids):
    response = requests.get(
        'http://www.infobae.com/?noredirect',
        headers=settings.REQUEST_HEADERS
    )
    link_re = re.compile(r'.*/\d+/\d+/\d+/(\d+)-\w+')

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
        unneeded = [
            'div.social-hori', 'footer', 'figure', 'div.modal', 'script',
            'div.tags', 'div.embed_cont',
        ]
        for selector in unneeded:
            nodes = root.cssselect(selector)
            for node in nodes:
                node.getparent().remove(node)

        title = root.cssselect('h1.entry-title > a')[0].text_content().strip()
        try:
            summary = root.xpath("//p[@class='preview']/following-sibling::p")[0]\
                        .text_content().strip()
        except:
            summary = root.xpath("//p[@class='preview']")[0].text_content().strip()

        text = u'\n'.join([
            node.text_content().strip()
            for node in root.cssselect('div.cuerposmart > div > p')
            if 'LEA MÁS:' not in node.text_content()
        ])

        if len(text) < 50:
            text = u'\n'.join([
                text.strip()
                for text in root.cssselect('div.cuerposmart > div')[0].text_content().split('\n')
                if len(text.strip()) > 30
            ])

        if len(text) < 50:
            return {'outcome': 'unparseable'}

        content = u'\n'.join([title, summary, text]).strip()
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Argentina', 'spanish']
    }

    return result


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root.cssselect('h1.entry-title > a')[0]\
                                .text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect('span.date')[0].text_content().strip()
        date = parse_date(raw_date)
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
