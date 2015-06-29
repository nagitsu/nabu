import logging

from lxml import html
from datetime import date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'clarin.com'
DOCUMENT_URL = 'http://www.clarin.com/sociedad/argentino-Messi_0_{}.html'


def get_missing_ids(existing_ids):
    """
    The entries are created manually through a script; no need to do anything
    here.
    """
    return []


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
        title = root.cssselect('.int-nota-title > h1')[0].text_content()
        summary = " ".join([
            el.text_content()
            for el in root.cssselect('.int-nota-title > p')
        ])
        text = root.cssselect('article .nota')[0].text_content()

        content = u'\n'.join([title, summary, text]).strip()
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Argentina']
    }

    return result


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root.cssselect('.int-nota-title > h1')[0]\
                                .text_content()
    except:
        pass

    try:
        raw_date = root.cssselect('.breadcrumb > ul > li:nth-child(3)')[0]\
                       .get('id')\
                       .replace('timestamp_CLANWS', '')

        year = int(raw_date[:4])
        month = int(raw_date[4:6])
        day = int(raw_date[6:8])

        metadata['date'] = date(year, month, day)
    except:
        pass

    return metadata
