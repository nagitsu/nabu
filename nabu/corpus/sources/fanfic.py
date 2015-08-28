import logging
import re
import requests

from lxml import html


logger = logging.getLogger(__name__)


SOURCE_DOMAIN = 'fanfic.es'
DOCUMENT_URL = 'http://www.fanfic.es/viewstory.php?sid={}&{}'


def get_missing_ids(existing_ids):
    response = requests.get('http://www.fanfic.es/')
    link_re = re.compile(r'.*?sid=(\d+)')

    root = html.fromstring(response.content)
    links = root.xpath('//div[@id="recentstory"]//a/@href')
    ids = []
    for link in links:
        m = link_re.match(link)
        if m:
            ids.append(int(m.group(1)))

    last_id = max(ids)

    scraped_ids = set(map(int, existing_ids))
    missing_ids = map(str, set(range(last_id + 1)) - set(scraped_ids))

    return ["{}@@index=1".format(id) for id in missing_ids]


def get_content(response):
    # Check if the response is valid.
    if response.status_code == 404:
        return {'outcome': 'notfound'}
    elif response.status_code >= 400:
        logger.debug("request to %s returned status_code = %s",
                     response.url, response.status_code)
        return {'outcome': 'failure'}

    root = html.fromstring(response.content)

    if 'index=1' in response.url:
        # index page, get new entries
        link_re = re.compile(r'.*?sid=(?P<sid>\d+).*?chapter=(?P<chapter>\d+)')
        try:
            new_entries = []
            nodes = root.cssselect('.storyindextable a')
            for node in nodes:
                link = node.get('href')
                m = link_re.match(link)
                if m:
                    new_entries.append(
                        "{}@@chapter={}".format(
                            m.group('sid'), m.group('chapter')
                        )
                    )
        except:
            return {'outcome': 'unparseable'}

        result = {
            'outcome': 'more_entries',
            'new_entries': new_entries
        }
    else:
        # we are in a fanfic chapter, just get the contents
        try:
            title = root.cssselect('h2#storypagetitle a')[0].text_content()
            c_title = root.cssselect('h3#storychaptertitle')[0].text_content()
            notes = '\n'.join(
                elem.text_content() for elem in root.cssselect('div.noteinfo')
            ).strip()
            text = '\n'.join(
                elem.text_content() for elem in root.cssselect('div#story')
            ).strip()

            content = u'\n'.join([title, c_title, notes, text]).strip()
        except:
            return {'outcome': 'unparseable'}

        result = {
            'outcome': 'success',
            'content': content,
            'tags': ['amateur_writing']
        }

    return result


def get_metadata(response):
    root = html.fromstring(response.content)

    metadata = {}
    try:
        metadata['title'] = root.cssselect(
            'h2#storypagetitle a')[0].text_content()
    except:
        pass

    return metadata
