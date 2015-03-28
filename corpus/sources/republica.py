import logging
import re
import requests

from datetime import datetime
from lxml import html

from ..utils import was_redirected


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


def _parse_date(date):
    """
    Parses dates from republica.com.uy. Example: "Viernes 19 abril, 6:12pm".
    """
    spanish_months = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'setiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
    }

    match = re.match('\w+ (\d+) (\w+), (\d+):(\d+)(\w+)', date)
    if match:
        day = int(match.group(1))
        month = spanish_months[match.group(2)]
        # The year is not present, we assume (incorrectly) the current year.
        year = datetime.now().year

        hour = int(match.group(3))
        minute = int(match.group(4))
        if match.group(5) == 'pm':
            hour = (hour + 12) % 24

        return datetime(year, month, day, hour, minute)


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
        date = _parse_date(raw_date.strip())
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
