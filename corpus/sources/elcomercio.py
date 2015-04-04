import logging
import re
import requests

from lxml import html

from ..utils import parse_date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'elcomercio.pe'
DOCUMENT_URL = 'http://elcomercio.pe/mundo/actualidad/nunca-antes-visto-serie-television-feminista-afganistan-noticia-{}'


def get_missing_ids(existing_ids):
    response = requests.get('http://elcomercio.pe')
    link_re = re.compile(r'.*/[\w-]+/[\w-]*-(\d+)')

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
        title = root.xpath("//h1[@itemprop='headline']")[0]\
                    .text_content().strip()
        try:
            summary = root.xpath(
                "//h2[@itemprop='description']"
            )[0].text_content().strip()
        except:
            summary = ""
        text = root.xpath(
            "//*[@itemprop='articleBody']"
        )[0].text_content().strip()

        content = u'\n'.join([title, summary, text]).strip()
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Peru']
    }

    return result


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root.xpath("//h1[@itemprop='headline']")[0]\
                                .text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect('section.ec-main time.fecha')[0]\
                       .text_content().strip()
        date = parse_date(raw_date)
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
