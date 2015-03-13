import re
import requests

from datetime import datetime
from lxml import html


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
    missing_ids = map(str, set(range(last_id)) - set(scraped_ids))

    return missing_ids


def get_content(response):
    # Check if redirected to error_404.php.
    if "error_404.php" in response.url:
        return {'outcome': 'notfound'}

    # Check if the response is valid.
    if response.status_code >= 400:
        return {'outcome': 'timeout'}

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


def _parse_date(date):
    """
    Example: "+ - 25.01.2015, 16:10 hs".
    """
    match = re.match(
        '[^\d]*(\d+)\.(\d+)\.(\d+),\s*(\d+):(\d+)',
        date, flags=re.UNICODE
    )
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))

        return datetime(year, month, day, hour, minute)


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
        date = _parse_date(raw_date.strip())
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
