import click
import json

from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from corpus.models import db, DataSource, Document, Entry
from corpus import sources


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
            }
        }
    },
    "mappings": {
        "document": {
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


def check_configuration():
    if not es.indices.exists(index="nabu"):
        es.indices.create(index="nabu", body=INDEX_BODY)


def create_index(force=False):
    """
    Create the `nabu` index with the specified settings. If `force` is set,
    deletes the old one if it already exists.
    """
    if force:
        es.indices.delete(index="nabu", ignore=404)
    es.indices.create(index="nabu", body=INDEX_BODY, ignore=400)


def prepare_document(doc):
    """
    Transforms a `Document` instance into a dictionary ready to be sent to
    Elasticsearch.
    """
    payload = json.loads(doc.metadata_)
    domain = doc.entry.data_source.domain
    source_id = doc.entry.source_id

    # Calculate the document's URL and add it to the metadata if it isn't
    # there already.
    if 'url' not in payload:
        url = sources.SOURCES[domain].DOCUMENT_URL.format(source_id)
        payload['url'] = url

    # Update the `date` field, if present.
    if 'date' in payload:
        payload['date'] = datetime.fromtimestamp(payload['date'])

    payload.update({
        "content": doc.content,
        "content_type": doc.content_type,
        "word_count": doc.word_count,
        "tags": json.loads(doc.tags),
        "data_source": domain,
        "entry": {
            "entry_id": doc.entry.id,
            "date_scraped": doc.entry.last_tried,
            "source_id": source_id,
        }
    })

    return payload


def prepare_documents(limit=None):
    """
    Returns an iterator of ES actions ready to pass to `bulk` of all the
    documents available on the database.
    """
    # Retrieve documents with at least 10 words; the rest shouldn't even be
    # stored.
    documents = db.query(Document).join(Entry).join(DataSource)\
                  .filter(Document.word_count >= 10)\
                  .yield_per(50000)

    if limit:
        documents = documents.limit(limit)

    for doc in documents:
        payload = prepare_document(doc)

        action = {
            "_op_type": "index",
            "_index": "nabu",
            "_type": "document",
            "_id": doc.id,
            "_source": payload,
        }

        yield action


def reindex_documents(limit=None, force=False):
    create_index(force=force)
    document_iterator = prepare_documents(limit=limit)
    bulk(es, document_iterator)


@click.command()
@click.option('--limit', default=None)
@click.option('--force', default=False)
def main(limit, force):
    reindex_documents(limit, force)


# Check everything is correctly configured when importing the module.
es = Elasticsearch()
check_configuration()


if __name__ == '__main__':
    main()
