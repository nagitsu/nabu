import re
import requests
import multiprocessing.dummy as mp

from datetime import datetime
from lxml import html

from nabu.core.models import db, Entry, DataSource


INDEX_URL = 'http://www.tusubtitulo.com/series.php'
SHOW_URL = 'http://www.tusubtitulo.com/show/{}'
SEASON_URL = 'http://www.tusubtitulo.com/ajax_loadShow.php?show={}&season={}'

HEADERS = {'Referer': 'http://www.tusubtitulo.com/'}


def parse_show_line(node):
    show_id = node.get('href')[len('/show/'):]
    show_name = node.text_content()
    return show_id, show_name


def get_show_list():
    response = requests.get(INDEX_URL)
    root = html.fromstring(response.text)
    show_nodes = root.cssselect('.line0 > a')
    shows = list(map(parse_show_line, show_nodes))
    return shows


def get_show_seasons(show_id):
    endpoint = SHOW_URL.format(show_id)
    response = requests.get(endpoint)
    root = html.fromstring(response.text)

    season_nodes = root.cssselect('span.titulo > a')
    prefix = 'javascript:loadShow({},'.format(show_id)
    seasons = list(map(
        lambda s: s.get('href')[len(prefix):-1],
        season_nodes
    ))

    return seasons


def get_season_episodes(show_id, season):
    endpoint = SEASON_URL.format(show_id, season)
    response = requests.get(endpoint, headers=HEADERS)
    root = html.fromstring(response.text)

    episode_nodes = root.cssselect('table')
    return episode_nodes


def valid_language(args):
    language, link = args
    if link and 'español' in language.lower():
        return True
    return False


def get_subtitle_id(episode_node):
    languages = []

    language_nodes = episode_node.cssselect('.language')
    for language_node in language_nodes:
        language = language_node.text_content().strip()

        link_node = language_node.getparent().cssselect('td > a')
        link = link_node[0].get('href') if link_node else None

        languages.append((language, link))

    valid_languages = list(filter(valid_language, languages))
    url = valid_languages[0][1] if valid_languages else None
    if url:
        subtitle_id = re.match('.*/(\d+)/(\d+)/(\d+)', url).groups()
    else:
        subtitle_id = None

    return subtitle_id


def get_season_subtitles(args):
    show_id, season = args
    nodes = get_season_episodes(show_id, season)
    subtitle_ids = list(map(get_subtitle_id, nodes))
    return subtitle_ids


def save_entries(ids, data_source):
    now = datetime.now()
    new_entries = []
    for source_id in ids:
        prepared_id = "@@".join(source_id)
        new_entries.append({
            'outcome': 'pending',
            'source_id': prepared_id,
            'added': now,
            'number_of_tries': 0,
            'data_source_id': data_source
        })
    db.execute(Entry.__table__.insert(), new_entries)
    db.commit()


def main():
    tusubtitulo = db.query(DataSource)\
                    .filter_by(domain='tusubtitulo.com')\
                    .first()

    if not tusubtitulo:
        tusubtitulo = DataSource(domain='tusubtitulo.com')
        db.add(tusubtitulo)
        db.commit()

    pool = mp.Pool(15)

    shows = get_show_list()
    all_seasons = pool.map(get_show_seasons, shows)

    season_tuples = []
    for show, show_seasons in zip(shows, all_seasons):
        for show_season in show_seasons:
            season_tuples.append((show, show_season))

    results = pool.map(get_season_subtitles, season_tuples)

    # Flatten the results.
    subtitle_ids = []
    for result in results:
        subtitle_ids.extend(result)

    # Fitler `None`s.
    subtitle_ids = list(filter(lambda s: s, subtitle_ids))

    existing = db.query(Entry.source_id).filter_by(data_source=tusubtitulo)
    existing = set(map(lambda r: r[0].split('@@')[1], existing))

    # We don't want repeated entries for the same episode.
    new_entries = []
    for subtitle_id in subtitle_ids:
        if subtitle_id[1] in existing:
            continue
        new_entries.append(subtitle_id)

    if new_entries:
        save_entries(new_entries, tusubtitulo.id)


if __name__ == '__main__':
    main()
