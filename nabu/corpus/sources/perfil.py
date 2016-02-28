import logging

from datetime import date, timedelta
from lxml import html

from nabu.corpus.utils import parse_date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'perfil.com'
DOCUMENT_URL = 'http://www.perfil.com/internacional/Asdf-{}.html'


def get_missing_ids(existing_ids):
    """
    An ID is composed of a date (e.g. 20150402) plus a four-digit number from
    0 to ~100.
    """
    if existing_ids:
        last_id = sorted(existing_ids, reverse=True)[0]
        last_date = date(
            int(last_id[:4]),
            int(last_id[4:6]),
            int(last_id[6:8])
        )
    else:
        # Initial date for Perfil.
        last_date = date(2006, 9, 9)

    missing_ids = []

    yesterday = date.today() - timedelta(days=1)
    one_day = timedelta(days=1)
    while last_date < yesterday:
        last_date += one_day
        id_base = last_date.isoformat().replace('-', '')
        for i in range(1, 101):
            missing_ids.append(id_base + "-{:04d}".format(i))

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
        title = root.xpath("//h1[@itemprop='name']")[0].text_content().strip()
        try:
            summary = root.xpath(
                "//h3[@itemprop='description']/following-sibling::p"
            )[0].text_content().strip()
        except:
            summary = ""
        text = root.xpath("//span[@itemprop='articleBody']")[0]\
                   .text_content().strip()

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
        metadata['title'] = root.xpath("//h1[@itemprop='name']")[0]\
                                .text_content().strip()
    except:
        pass

    try:
        raw_date = root.xpath("//*[@itemprop='author']/span")[0]\
                       .text_content().strip()
        date = parse_date(raw_date)
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
