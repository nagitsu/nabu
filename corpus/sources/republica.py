import logging
import re
import requests

from lxml import html

from ..utils import parse_date, was_redirected


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'republica.com.uy'
DOCUMENT_URL = 'http://www.republica.com.uy/sdg23f23/{}/'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.republica.com.uy')
    link_re = re.compile(r'.*/[0-9a-z-]+/(\d+)/')

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
    if was_redirected(response):
        return {'outcome': 'notfound'}

    root = html.fromstring(response.content)

    try:
        try:
            overtitle = root.cssselect('p.colgado')[0].text_content()
        except IndexError:
            # No overtitle found. Doesn't matter, it's optional.
            overtitle = ""

        title = root.cssselect('h1.entry-title')[0].text_content()

        try:
            summary = root.cssselect(
                'div.excerpt_single'
            )[0].text_content()
        except IndexError:
            # No summary found. Doesn't matter, it's optional.
            summary = ""

        article = u'\n'.join([
            node.text_content()
            for node in root.cssselect('div.entry > p')
        ])
        content = u'\n'.join([overtitle, title, summary, article]).strip()
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
        metadata['title'] = root.cssselect('h1.entry-title')[0].text_content()
    except:
        pass

    try:
        raw_date = root.cssselect('p.post-meta > span.updated')[0]\
                       .text_content().strip()
        date = parse_date(raw_date.strip())
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
