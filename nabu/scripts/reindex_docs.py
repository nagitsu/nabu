from elasticsearch.helpers import bulk

from nabu.core.models import db, DataSource, Document, Entry
from nabu.core.index import es, create_index, prepare_document


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
