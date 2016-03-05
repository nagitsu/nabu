# EUBookshop corpus location: http://opus.lingfil.uu.se/download.php?f=EUbookshop%2Fes.raw.tar.gz
import gzip
import logging
import os
import sys

from datetime import datetime
from elasticsearch.helpers import bulk
from lxml import etree

from nabu.core import settings
from nabu.core.index import es, calculate_doc_id


logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DocumentPipeline(object):

    def __init__(self):
        self._dirty_articles = []

    def process_item(self, item):
        # Don't insert into Elasticsearch for every item received.
        self._dirty_articles.append(item)
        if len(self._dirty_articles) > 300:
            self.flush()

    def close(self, spider):
        self.flush()

    def flush(self):
        if not self._dirty_articles:
            return

        actions = []
        for article in self._dirty_articles:
            doc_id = calculate_doc_id(
                'bookshop.europa.eu',
                article['entry']['source_id']
            )

            actions.append({
                '_op_type': 'index',
                '_index': settings.ES_INDEX,
                '_type': settings.ES_DOCTYPE,
                '_id': doc_id,
                '_source': article
            })

        bulk(es, actions)
        logger.info('flushed count=%s', len(actions))

        self._dirty_articles = []


def prepare_document(filename, content):
    article_id = filename.split('.')[0]
    title = content.strip().split('\n')[0][:50]
    word_count = len(content.split())

    url = "http://bookshop.europa.eu/es/frontex-at-a-glance-pb{}/".format(article_id)

    article = {
        'content': content,
        'content_type': 'clean',
        'tags': ['books', 'EU', 'spanish'],
        'word_count': word_count,

        'data_source': 'bookshop.europa.eu',
        'entry': {
            'date_scraped': datetime.now(),
            'source_id': article_id,
        },

        'title': title,
        'url': url,
    }

    return article


def read_file(path):
    try:
        with gzip.open(path) as f:
            root = etree.fromstring(f.read())
    except:
        logger.warning("invalid file=%s", path)
        return

    content = " ".join([
        l.strip() for l in root.xpath('//text()') if l.strip()
    ])

    return content


def main(root_path):
    pipeline = DocumentPipeline()

    for root, _, files in os.walk(root_path):
        logger.info("found directory=%s", root)
        for filename in files:
            logger.info("found file=%s", filename)
            filepath = os.path.join(root, filename)
            content = read_file(filepath)
            if not content:
                continue

            doc = prepare_document(filename, content)
            pipeline.process_item(doc)

    pipeline.flush()


if __name__ == '__main__':
    root_path = sys.argv[1]
    main(root_path)
