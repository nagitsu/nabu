import logging
import re
import requests

from lxml import html

from ..utils import parse_date


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'emol.com'
DOCUMENT_URL = 'http://www.emol.com/noticias/todas/2000/12/06/{}/asdf.html'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.emol.com')
    link_re = re.compile(r'[^/]*/\w+/\w+/\d+/\d+/\d+/(\d+)/')

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
        title = root.cssselect('#cuDetalle_cuTitular_tituloNoticia')[0]\
                    .text_content().strip()
        summary = root.cssselect('#cuDetalle_cuTitular_bajadaNoticia')[0]\
                      .text_content().strip()
        article = root.cssselect('#cuDetalle_cuTexto_textoNoticia')[0]\
                      .text_content()
        content = u'\n'.join([title, summary, article])
    except:
        return {'outcome': 'unparseable'}

    # If no content was retrieved, the article doesn't really exist.
    if not content.strip():
        return {'outcome': 'notfound'}

    result = {
        'outcome': 'success',
        'content': content,
        'tags': ['news', 'Chile']
    }

    return result


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root\
            .cssselect('#cuDetalle_cuTitular_tituloNoticia')[0]\
            .text_content().strip()
    except:
        pass

    try:
        raw_date = root.cssselect('#cuDetalle_cuCreditos_fecha')[0]\
                       .text_content().strip()
        date = parse_date(raw_date)
        if date:
            metadata['date'] = date
    except:
        pass

    return metadata
