from flask import Blueprint, jsonify

from nabu.core.index import es


bp = Blueprint('corpus', __name__, url_prefix='/corpus')


def get_corpus_size():
    query = {
        "aggs": {
            "words": {
                "sum": {
                    "field": "word_count"
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
        "aggs": {
            "per_source": {
                "terms": {
                    "field": "data_source",
                    "size": 0,
                },
                "aggs": {
                    "words": {
                        "sum": {"field": "word_count"}
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
        "query": {
            "range": {
                "entry.date_scraped": {
                    "gte": "now-10d/d"
                }
            }
        },
        "aggs": {
            "over_time": {
                "terms": {
                    "field": "data_source",
                    "min_doc_count": 0,
                    "size": 0,
                },
                "aggs": {
                    "over_time": {
                        "date_histogram": {
                            "field": "entry.date_scraped",
                            "format": "yyyy-MM-dd",
                            "interval": "1d",
                            "min_doc_count": 0,
                        },
                        "aggs": {
                            "word_counts": {
                                "sum": {"field": "word_count"}
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
