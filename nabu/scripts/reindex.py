import logging
import sys

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, bulk
from hashlib import sha512


logging.basicConfig(format="%(asctime)s :: %(levelname)s :: %(message)s")


INDEX_BODY = {
    "settings": {
        "index": {
            "mapper": {"dynamic": False},
            "number_of_shards": 5,
            "number_of_replicas": 0,
            "analysis": {
                "filter": {
                    "spanish_stop": {
                        "type": "stop",
                        "stopwords": "_spanish_",
                    },
                },
                "analyzer": {
                    # Standrad analyzer plus folding.
                    "folding": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase", "spanish_stop", "asciifolding",
                        ],
                    }
                }
            },
            "query": {
                "default_field": "content"
            },
        }
    },
    "mappings": {
        "document": {
            "_all": {"enabled": False},
            "properties": {
                "content": {"type": "string", "analyzer": "folding"},
                # Also included in the content.
                "title": {"type": "string", "analyzer": "folding"},
                # May be `clean`, `html`. State the content is in.
                "content_type": {"type": "string", "index": "not_analyzed"},
                "date": {"type": "date", "format": "dateOptionalTime"},
                "url": {"type": "string", "index": "not_analyzed"},
                "tags": {"type": "string", "index": "not_analyzed"},
                "word_count": {"type": "long"},
                # The data source's domain.
                "data_source": {"type": "string", "index": "not_analyzed"},
                "entry": {
                    "properties": {
                        # ID of the entry on the database.
                        "entry_id": {"type": "long"},
                        "date_scraped": {
                            "type": "date",
                            "format": "dateOptionalTime",
                        },
                        # DataSource-level ID (e.g. 180's article ID).
                        "source_id": {
                            "type": "string",
                            "index": "not_analyzed",
                        },
                    },
                },
            }
        }
    }
}


def recreate_index(es, index_name):
    es.indices.delete(index=index_name, ignore=404)
    es.indices.create(index=index_name, body=INDEX_BODY, ignore=400)


def reindex(es, source_index, target_index, scroll='30m'):
    recreate_index(es, target_index)

    docs = scan(
        es, index=source_index, scroll=scroll,
        fields=('_source', '_parent', '_routing', '_timestamp'),
    )

    def update_documents(hits, new_index):
        for doc in hits:
            doc['_index'] = new_index
            if 'fields' in doc:
                doc.update(doc.pop('fields'))

            # Add the `spanish` tag if not present.
            tags = doc['_source'].get('tags', [])
            if 'spanish' not in tags:
                doc['_source'].setdefault('tags', []).append('spanish')

            # Update the ID of the document.
            doc_id = "{}@@{}".format(
                doc['_source']['data_source'],
                doc['_source']['entry']['source_id'],
            )
            doc['_id'] = sha512(doc_id.encode('utf-8')).hexdigest()[:30]

            # If document's content is too low, discard it.
            if len(doc['_source']['content'].split()) < 10:
                continue

            yield doc

    new_docs = update_documents(docs, target_index)

    return bulk(es, new_docs, chunk_size=1000, stats_only=True)


if __name__ == '__main__':
    source_index = sys.argv[1]
    target_index = sys.argv[2]

    if len(sys.argv) > 3:
        es_host = sys.argv[3]
    else:
        es_host = 'localhost:9200'

    if len(sys.argv) > 4:
        es_auth = sys.argv[4].split(':')
    else:
        es_auth = None

    es = Elasticsearch([es_host], http_auth=es_auth)
    reindex(es, source_index, target_index)
