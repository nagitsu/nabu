import re


SOURCE_DOMAIN = 'tusubtitulo.com'
DOCUMENT_URL = 'http://www.tusubtitulo.com/updated/{}/{}/{}'
HEADERS = {'Referer': 'http://www.tusubtitulo.com'}


def get_missing_ids(existing_ids):
    """
    The entries are created manually through a script; no need to do anything
    here.
    """
    return []


def parse_srt(subtitle):
    digit = re.compile(r'^\d+$')
    timing = re.compile(r'^\d+:\d+:\d+.*\d$')

    lines = []
    for line in subtitle.split('\r\n'):
        if not line or digit.match(line) or timing.match(line):
            continue
        lines.append(line)

    content = " ".join(lines)\
                 .replace('www.TUSUBTITULO.com -DIFUNDE LA CULTURA-', '')\
                 .replace('-', '')

    return content


def get_content(response):
    if response.url == 'http://www.tusubtitulo.com/index.php':
        return {'outcome': 'notfound'}

    # .srt files are always in latin-1 (or should be).
    subtitle = response.content.decode('latin-1')
    content = parse_srt(subtitle)

    result = {
        'outcome': 'success',
        'tags': ['subtitle'],  # 'Neutral', 'Spain'
        'content': content
    }

    return result


def get_metadata(response):
    """
    No metadata available for subtitles.
    """
    return {}
