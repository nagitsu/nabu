import logging
import re
import requests

from lxml import html

from ..utils import parse_date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'observador.com.uy'
DOCUMENT_URL = 'http://www.elobservador.com.uy/noticia/{}/c/'


def get_missing_ids(existing_ids):
    response = requests.get("http://www.elobservador.com.uy")
    link_re = re.compile(r'.*/noticia/(\d+)/')

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
    # Check if redirected to error_404.php.
    if "error_404.php" in response.url:
        return {'outcome': 'notfound'}

    # Check if the response is valid.
    if response.status_code >= 400:
        logger.debug("request to %s returned status_code = %s",
                     response.url, response.status_code)
        return {'outcome': 'failure'}

    root = html.fromstring(response.content)

    try:
        title = root.cssselect('div.story > h1')[0].text_content().strip()
        summary = root.cssselect('div.story > h2')[0].text_content()
        article = u"\n".join(root.xpath(
            "//div[@class='story_left']/p/text()"
        ))

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
        metadata['title'] = root.cssselect('div.story > h1')[0]\
                                .text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect('div.story div.fecha')[0].text_content()
        date = parse_date(raw_date.split('-')[1])
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
