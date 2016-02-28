from elasticsearch import Elasticsearch
from hashlib import sha512

from nabu.core import settings


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
        settings.ES_DOCTYPE: {
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


def check_configuration():
    if not es.indices.exists(index=settings.ES_INDEX):
        es.indices.create(index=settings.ES_INDEX, body=INDEX_BODY)


def create_index(force=False):
    """
    Create the index with the specified settings. If `force` is set, deletes
    the old one if it already exists.
    """
    if force:
        es.indices.delete(index=settings.ES_INDEX, ignore=404)
    es.indices.create(index=settings.ES_INDEX, body=INDEX_BODY, ignore=400)


def prepare_document(content, metadata, entry):
    """
    Transforms the data returned from a scraper into a dictionary ready to be
    sent to Elasticsearch.
    """
    payload = metadata
    domain = entry.data_source.domain
    source_id = entry.source_id
    word_count = len(content['content'].split())

    payload.update({
        "content": content['content'],
        "content_type": content.get('content_type', 'clean'),
        "word_count": word_count,
        "tags": content.get('tags', []),
        "data_source": domain,
        "entry": {
            "entry_id": entry.id,
            "date_scraped": entry.last_tried,
            "source_id": source_id,
        }
    })

    # Document ID is be fixed, so it can be overwritten if scraped again.
    doc_id = sha512(
        "{}@@{}".format(domain, source_id).encode('utf-8')
    ).hexdigest()[:30]

    return doc_id, payload


# Check everything is correctly configured when importing the module.
es = Elasticsearch(
    [settings.ES_HOST],
    http_auth=settings.ES_HTTP_AUTH,
    retry_on_timeout=True
)
check_configuration()
