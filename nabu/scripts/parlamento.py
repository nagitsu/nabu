import logging
import os
import re
import requests
import time

from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from lxml import html
from hashlib import sha512


es = Elasticsearch(http_auth=('nabu', 'nabunabu'))
now = datetime.now()


logging.basicConfig(
    format='%(asctime)s :: %(levelname)s :: %(message)s',
    level=logging.INFO
)
# Don't log `requests`'s INFO messages.
logging.getLogger("requests").setLevel(logging.WARNING)


DOMAIN = "http://www.parlamento.gub.uy"
BASE_URL = (
    "http://www.parlamento.gub.uy/sesiones/AccesoSesiones.asp"
    "?Url=/sesiones/diarios/{}/html/{}.htm"
)

OUTPUT_FOLDER = 'sesiones'
TIMEOUT = 60

URL_FORMAT = re.compile("/htmlstat/sesiones/pdfs/(\w+)/(\w+)\.pdf")


def download_sessions():
    sessions = []
    with open("links.txt") as f:
        for link in f.readlines():
            m = URL_FORMAT.match(link)
            sessions.append(m.groups() + (link.strip(),))

    for session in sessions:
        type_ = session[0]
        session_id = session[1]
        pdf_url = session[2]

        filename = "{}.html".format(session_id)

        downloaded_ids = [s.split('.')[0] for s in os.listdir(OUTPUT_FOLDER)]
        if session_id in downloaded_ids:
            logging.info("session_id = '%s' already exists", session_id)
            continue

        url = BASE_URL.format(type_, session_id)
        response = requests.get(url, timeout=TIMEOUT)

        # HTML version not found.
        if len(response.content) < 2500:
            response = requests.get(DOMAIN + pdf_url, timeout=TIMEOUT)
            filename = "{}.pdf".format(session_id)

        output = "{}/{}".format(OUTPUT_FOLDER, filename)
        with open(output, 'w') as f:
            f.write(response.content)

        logging.info(
            "session_id = '%s' downloaded successfully; %s",
            session_id,
            filename.split('.')[-1]
        )
        time.sleep(1)


def prepare_documents():
    files = [f for f in os.listdir('sesiones') if f.endswith('.html')]

    for filename in files:
        with open('sesiones/{}'.format(filename), encoding='latin-1') as f:
            root = html.fromstring(f.read())

        try:
            content = root.cssselect('body')[0].text_content()
        except:
            print(filename)
            continue
        doc_id = filename.split('.')[0]

        with open('documents/{}'.format(doc_id), 'w') as f:
            print(content, file=f)


def prepare_document(doc_id, content):
    word_count = len(content.split())
    title = content.strip().split('\n')[0].strip()

    if 'c' in doc_id:
        doc_type = "comision"
    elif 'd' in doc_id:
        doc_type = "camara"
    elif 's' in doc_id:
        doc_type = "senado"
    else:
        doc_type = "asamblea"

    url = (
        "http://www.parlamento.gub.uy/sesiones/diarios/{}/html/{}.htm"
    ).format(doc_type, doc_id)
    es_id = sha512(doc_id.encode('utf-8')).hexdigest()[:30]

    payload = {
        'content': content,
        'content_type': 'clean',
        'word_count': word_count,
        'tags': ['official', 'Uruguay', 'spanish'],
        'data_source': 'parlamento.gub.uy',
        'title': title,
        'url': url,
        'entry': {
            'date_scraped': now,
            'source_id': doc_id,
        }
    }

    action = {
        '_op_type': 'index',
        '_index': 'nabu2',
        '_type': 'document',
        '_id': es_id,
        '_source': payload,
    }

    return action


def index_documents():
    document_ids = [s for s in os.listdir('documents')]

    actions = []
    for document_id in document_ids:
        with open('documents/{}'.format(document_id)) as f:
            actions.append(prepare_document(document_id, f.read()))

    bulk(es, actions)


def main():
    # download_sessions()
    # prepare_documents()
    index_documents()


if __name__ == '__main__':
    main()
