import json
import zipstream

from elasticsearch import ElasticsearchException
from elasticsearch.helpers import scan

from flask import Blueprint, jsonify, request, abort, Response, url_for

from nabu.core.index import es


bp = Blueprint('corpus', __name__, url_prefix='/corpus')


def get_corpus_size():
    query = {
        'aggs': {
            'words': {
                'sum': {
                    'field': 'word_count'
                }
            }
        }
    }
    response = es.search(
        index='nabu', doc_type='document',
        search_type='count', body=query
    )
    return response['aggregations']['words']['value']


def get_corpus_size_by_source():
    query = {
        'aggs': {
            'per_source': {
                'terms': {
                    'field': 'data_source',
                    'size': 0,
                },
                'aggs': {
                    'words': {
                        'sum': {'field': 'word_count'}
                    }
                }
            }
        }
    }

    response = es.search(
        index='nabu',
        doc_type='document',
        search_type='count',
        body=query
    )

    result = []
    for bucket in response['aggregations']['per_source']['buckets']:
        result.append({
            'source': bucket['key'],
            'size': bucket['words']['value'],
        })

    return result


def get_corpus_size_increase():
    query = {
        'query': {
            'range': {
                'entry.date_scraped': {
                    'gte': 'now-10d/d'
                }
            }
        },
        'aggs': {
            'over_time': {
                'terms': {
                    'field': 'data_source',
                    'min_doc_count': 0,
                    'size': 0,
                },
                'aggs': {
                    'over_time': {
                        'date_histogram': {
                            'field': 'entry.date_scraped',
                            'format': 'yyyy-MM-dd',
                            'interval': '1d',
                            'min_doc_count': 0,
                        },
                        'aggs': {
                            'word_counts': {
                                'sum': {'field': 'word_count'}
                            }
                        }
                    }
                }
            }
        }
    }

    response = es.search(
        index='nabu',
        doc_type='document',
        search_type='count',
        body=query
    )

    days = set()
    result = []
    for outer_bucket in response['aggregations']['over_time']['buckets']:
        on_day = []
        for inner_bucket in outer_bucket['over_time']['buckets']:
            day = inner_bucket['key_as_string']
            days.add(day)
            on_day.append({
                'day': day,
                'value': inner_bucket['word_counts']['value'],
            })
        result.append({
            'source': outer_bucket['key'],
            'values': on_day,
        })

    # Fill up the missing days with zeros.
    for source in result:
        missing_days = days - set(map(lambda d: d['day'], source['values']))
        for day in missing_days:
            source['values'].append({
                'day': day,
                'value': 0,
            })
        source['values'].sort(key=lambda d: d['day'])
        source['values'] = [v['value'] for v in source['values']]

    return result


@bp.route('/stats/')
def stats():
    return jsonify(data={
        'size': get_corpus_size(),
        'by_source': get_corpus_size_by_source(),
        'over_time': get_corpus_size_increase(),
    })


def clean_doc(doc):
    cleaned = {
        'document_id': doc['_id'],
        'source': doc['_source']['data_source'],
        'date_scraped': doc['_source']['entry']['date_scraped'],
    }

    try:
        cleaned['snippet'] = doc['highlight']['content'][0]
    except (KeyError, IndexError):
        # If no highlighting present, return the full field.
        cleaned['snippet'] = doc['_source']['content']

    return cleaned


@bp.route('/search/', methods=['POST'])
def search():
    offset = int(request.args.get('offset', 0))
    user_query = request.get_json(force=True)['query']

    highlight = {
        'fields': {
            'content': {
                'fragment_size': 100,
                'number_of_fragments': 1
            }
        }
    }

    query = {
        'query': user_query,
        'aggs': {'words': {'sum': {'field': 'word_count'}}},
        'highlight': highlight,
        'from': offset,
        'size': 25,
    }

    try:
        response = es.search(index='nabu', doc_type='document', body=query)
    except ElasticsearchException as e:
        return jsonify(message=e.error, error='Bad Request'), 400

    word_count = response['aggregations']['words']['value']
    hits = [clean_doc(hit) for hit in response['hits']['hits']]
    download_link = url_for('.download_search', query=json.dumps(user_query))

    data = {
        'word_count': word_count,
        'download_link': download_link,
        'hits': hits
    }

    meta = {
        'count': response['hits']['total'],
        'offset': offset,
    }

    return jsonify(meta=meta, data=data)


@bp.route('/document/<document_id>/')
def document_detail(document_id):
    try:
        response = es.get(index='nabu', doc_type='document', id=document_id)
    except ElasticsearchException:
        abort(404)

    try:
        permalink = response['_source']['url']
    except KeyError:
        permalink = None

    metadata = {}
    possible_metadata = {'title', 'date'}
    existing = set(response['_source'].keys())
    for field in possible_metadata & existing:
        metadata[field] = response['_source'][field]

    document = {
        'id': response['_id'],
        'content': response['_source']['content'],
        'data_source': response['_source']['data_source'],
        'date_scraped': response['_source']['entry']['date_scraped'],
        'metadata': metadata,
        'tags': response['_source']['tags'],
        'word_count': response['_source']['word_count'],
        'permalink': permalink,
    }

    return jsonify(data=document)


@bp.route('/download/', methods=['GET'])
def download_search():
    query = json.loads(request.args.get('query'))
    if not query:
        query = {'match_all': {}}

    documents = scan(
        es, index='nabu',
        scroll='30m', fields='content',
        query={'query': query}
    )

    def content_streamer():
        z = zipstream.ZipFile(
            mode='w',
            compression=zipstream.ZIP_DEFLATED
        )

        for document in documents:
            doc_id = document['_id']
            content = document['fields']['content'][0]

            def _it():
                yield content.encode('utf-8')

            # We need to make use of the private functions of zipstream,
            # because we need to feed the zipfile documents from ES while we
            # send them to the user. Since we want every document on a separate
            # file, we have no alternative than to call the `__write` method
            # manually.
            file_name = "{}.txt".format(doc_id)
            for data in z._ZipFile__write(iterable=_it(), arcname=file_name):
                yield data

        # Yield the rest of the data the zipfile might have (corresponding to
        # the `__close` method).
        for chunk in z:
            yield chunk

    response = Response(content_streamer(), mimetype="application/zip")
    disposition = "attachment; filename=corpus.zip"
    response.headers['Content-Disposition'] = disposition
    return response
