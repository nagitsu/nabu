from elasticsearch import ElasticsearchException
from flask import Blueprint, jsonify, request, abort

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
    # TODO: Download link.
    # TODO: Sanitize the query somehow? Or make less powerful.
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
    download_link = 'not-available-yet'
    hits = [clean_doc(hit) for hit in response['hits']['hits']]

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
