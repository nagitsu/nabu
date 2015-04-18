import logging

from datetime import date, timedelta
from lxml import html

from ..utils import parse_date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'eldiario.net'
DOCUMENT_URL = 'http://www.eldiario.net/noticias/{}'


def get_missing_ids(existing_ids):
    """
    An ID is composed of a date plus a four-digit number from 0 to ~140.
    """
    if existing_ids:
        existing_ids = map(lambda s: s.split('/')[2], existing_ids)
        last_id = sorted(existing_ids, reverse=True)[0][2:]
        last_date = date(
            int("20" + last_id[:2]),
            int(last_id[2:4]),
            int(last_id[4:6])
        )
    else:
        # Initial date for Perfil.
        last_date = date(2012, 1, 6)

    missing_ids = []

    yesterday = date.today() - timedelta(days=1)
    one_day = timedelta(days=1)
    while last_date < yesterday:
        last_date += one_day
        # 2015-01-01 => 15-01-01.
        id_base = "{}/{}_{:02d}/nt{}/principal.php?n=".format(
            last_date.year,
            last_date.year,
            last_date.month,
            last_date.isoformat().replace('-', '')[2:]
        )
        for i in range(1, 131):
            missing_ids.append(id_base + str(i))

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
        title = root.cssselect('div.not_comp h1')[0].text_content().strip()
        try:
            summary = root.cssselect('p.epigrafe')[0].text_content().strip()
        except IndexError:
            summary = ""
        text = root.cssselect('div.nota_txt')[0].text_content()

        content = u'\n'.join([title, summary, text]).strip()

        if not content.strip():
            return {'outcome': 'notfound'}
    except:
        return {'outcome': 'unparseable'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Bolivia']
    }

    return result


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root.cssselect('div.not_comp h1')[0]\
                                .text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect('ul#menu_inf > li')[0]\
                       .text_content().strip().split(', ')[-1]
        date = parse_date(raw_date)
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
