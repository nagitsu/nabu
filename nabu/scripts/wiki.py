"""
Cleans and indexes the spanish wikipedia dump.
"""
import bz2
import multiprocessing as mp
import os
import re

from datetime import datetime
from hashlib import sha512

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


es = Elasticsearch(http_auth=('nabu', 'nabunabu'))
now = datetime.now()


def prepare_document(page_id, url, title, text):
    word_count = len(text.split())
    es_id = sha512(page_id.encode('utf-8')).hexdigest()[:30]

    payload = {
        'content': text,
        'content_type': 'clean',
        'word_count': word_count,
        'tags': ['wikipedia', 'spanish'],
        'data_source': 'es.wikipedia.com',
        'title': title,
        'url': url,
        'entry': {
            'date_scraped': now,
            'source_id': page_id,
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


def process_file(file_path):
    """
    Parse a wikipedia article, indexing it on Elasticsearch.
    """
    try:
        content = bz2.BZ2File(file_path).read().decode('utf-8')

        # In case any `Ref` went unnoticed.
        ref_re = re.compile(r'<ref>.*</ref>', re.IGNORECASE)
        content = ref_re.sub('', content)

        # Extract the documents from the pseudo-XML files.
        doc_re = re.compile(
            r'^<doc id="(.*?)" url="(.*?)" title="(.*?)">$'
            '(.*?)'
            '^</doc>$',
            re.MULTILINE | re.DOTALL
        )
        matches = doc_re.findall(content)

        actions = []
        for page_id, url, title, text in matches:
            actions.append(prepare_document(page_id, url, title, text))

        bulk(es, actions)

        print("file_path = {}; length = {}".format(file_path, len(actions)))
    except:
        print("file_path = {}; FAILED".format(file_path))


def main():
    dir_name = 'wiki'
    files = []
    for container in os.listdir(dir_name):
        container_path = os.path.join(dir_name, container)
        for file_name in os.listdir(container_path):
            file_path = os.path.join(container_path, file_name)
            files.append(file_path)

    pool = mp.Pool(12)
    pool.map(process_file, files)


if __name__ == '__main__':
    main()
