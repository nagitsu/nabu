import logging
import re
import requests

from lxml import html
from urllib.parse import urlsplit

from nabu.corpus.utils import parse_date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'montevideo.com.uy'
DOCUMENT_URL = 'http://www.montevideo.com.uy/auc.aspx?{},245'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.montevideo.com.uy/index.html')
    link_re = re.compile(r'.*auc\.aspx\?(\d+),')

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


def _parse_montevideo_com_uy(root):
    # We use the overtitle as the actual article title, as it's more
    # detailed.
    overtitle = root.xpath("//h1[@itemprop='headline']/text()")[0]

    title = root.xpath(
        "//h1[@itemprop='headline']/following-sibling::h4[1]/text()"
    )[0]
    summary = root.xpath("//h2[@itemprop='articleSection']/text()")[0]
    article = u"\n".join(root.xpath(
        "//h3[@itemprop='articleBody']/following-sibling::p/text()"
    ))
    content = u'\n'.join([overtitle, title, summary, article]).strip()

    raw_date = root.xpath("//time")[0].text_content()
    date = parse_date(raw_date)

    article = {
        'date': date,
        'title': overtitle,
        'content': content,
    }

    return article


def _parse_futbol_com_uy(root):
    # We use the overtitle as the actual article title, as it's more
    # detailed.
    overtitle = root.xpath("//div[@class='doscolsteizq']/h3/text()")[0]

    title = root.xpath("//div[@class='doscolsteizq']/h1/text()")[0]
    summary = root.xpath(
        "//div[@class='doscolsteizq']/div[@id='txt']/h5/text()"
    )[0]
    article = u"\n".join(root.xpath(
        "//div[@class='doscolsteizq']/div[@id='txt']/h6/"
        "following-sibling::p/text()"
    ))
    content = u'\n'.join([overtitle, title, summary, article]).strip()

    raw_date = root.xpath(
        "//div[@class='fecharedesizq']/h4"
    )[0].text_content()
    date = parse_date(raw_date)

    article = {
        'date': date,
        'title': overtitle,
        'content': content,
    }

    return article


def _parse_pantallazo_com_uy(root):
    # We use the overtitle as the actual article title, as it's more
    # detailed.
    overtitle = root.xpath("//div[@class='gral_ucdeest']/h1/text()")[0]

    title = root.xpath("//div[@class='gral_ucdeest']/h5/text()")[0]
    summary = root.xpath("//div[@class='gral_ucdeest']/h3/text()")[0]
    article = u"\n".join(root.xpath(
        "//div[@class='gral_ucdeest']/h4/"
        "following-sibling::p/text()"
    ))
    content = u'\n'.join([overtitle, title, summary, article]).strip()

    raw_date = root.xpath("//div[@class='gral_ucdeest']/h6/text()")[0]
    date = parse_date(raw_date)

    article = {
        'date': date,
        'title': overtitle,
        'content': content,
    }

    return article


def get_content(response):
    # Check if redirected to `/amensaje.aspx`.
    if 'amensaje.aspx' in response.url:
        return {'outcome': 'notfound'}

    # Check if the response is valid.
    if response.status_code == 404:
        return {'outcome': 'notfound'}
    elif response.status_code >= 400:
        logger.debug("request to %s returned status_code = %s",
                     response.url, response.status_code)
        return {'outcome': 'failure'}

    domain = urlsplit(response.url).netloc
    root = html.fromstring(response.content)

    try:
        if 'futbol.com.uy' in domain:
            content = _parse_futbol_com_uy(root)['content']
        elif 'pantallazo.com.uy' in domain:
            content = _parse_pantallazo_com_uy(root)['content']
        else:
            content = _parse_montevideo_com_uy(root)['content']
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Uruguay', 'spanish']
    }

    return result


def get_metadata(response):
    domain = urlsplit(response.url).netloc
    root = html.fromstring(response.content)

    metadata = {}
    try:
        if 'futbol.com.uy' in domain:
            data = _parse_futbol_com_uy(root)
        elif 'pantallazo.com.uy' in domain:
            data = _parse_pantallazo_com_uy(root)
        else:
            data = _parse_montevideo_com_uy(root)
    except:
        return metadata

    if data['title']:
        metadata['title'] = data['title']

    if data['date']:
        metadata['date'] = data['date']

    return metadata
