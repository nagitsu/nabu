import json
import re
import subprocess

from datetime import datetime, timedelta
from flask import abort, Flask, jsonify
from sqlalchemy.sql import func

from nabu.core.models import db, DataSource, Document, Entry, Statistic
from nabu.core.index import es


app = Flask(__name__)


def disk_usage():
    output = subprocess.check_output(['df', '-h'])
    percentage = re.findall('(\d+%) \/\n', output)[0]
    return percentage


def calculate_statistics(limit_date):
    """
    Returns a dictionary with the values for the statistics, including entries
    up to `limit_date`.
    """
    stats = {}

    for row in db.query(DataSource.id).all():
        data_source_id = row[0]
        stats[data_source_id] = {
            'document_count': 0,
            'word_count': 0,
            'entry_count_tried': 0,
            'entry_count_total': 0,
        }

    results = db.query(Entry.data_source_id,
                       func.count(Document.id).label('document_count'),
                       func.sum(Document.word_count).label('word_count'),
                       func.count(Entry.id).label('entry_count_tried'))\
                .outerjoin(Document)\
                .filter(Entry.last_tried <= limit_date)\
                .group_by(Entry.data_source_id)\
                .all()

    for result in results:
        row = dict(map(lambda f: (f, getattr(result, f)), result.keys()))
        stats[result.data_source_id].update(row)

    results = db.query(Entry.data_source_id,
                       func.count(Entry.id).label('entry_count_total'))\
                .filter(Entry.added <= limit_date)\
                .group_by(Entry.data_source_id)\
                .all()

    for result in results:
        row = dict(map(lambda f: (f, getattr(result, f)), result.keys()))
        stats[result.data_source_id].update(row)

    return stats.values()


@app.route("/api/stats/update")
def update_statistics():
    # First get the last Statistic created.
    last = db.query(Statistic).order_by(Statistic.date.desc()).first()

    now = datetime.now()
    stats = []
    if not last:
        # If none exist, just create one for the present.
        limit = now.replace(minute=0, second=0, microsecond=0)
        stats = calculate_statistics(limit)
        for stat in stats:
            stat['date'] = limit
            db.merge(Statistic(**stat))
    else:
        # If one exists, calculate all the hour-length intervals up to the
        # present, and calculate the statistics for each of them.
        limit = last.date + timedelta(hours=1)
        while limit <= now:
            stats = calculate_statistics(limit)
            for stat in stats:
                stat['date'] = limit
                db.merge(Statistic(**stat))
            limit += timedelta(hours=1)

    db.commit()

    return jsonify(current=stats)


def get_source_stats(stat):
    """
    Returns a summary of statistics derived from the given `stat`.
    """
    summary = {}
    summary['document_count'] = stat.document_count
    summary['word_count'] = stat.word_count

    if stat.entry_count_total:
        summary['completion'] = (
            stat.entry_count_tried / float(stat.entry_count_total)
        )
    else:
        summary['completion'] = 0.0

    if stat.entry_count_tried:
        summary['successful'] = (
            stat.document_count / float(stat.entry_count_tried)
        )
    else:
        summary['successful'] = 0.0

    return summary


@app.route("/api/general")
def general():
    summary = {}

    # Obtain the disk usage.
    try:
        summary['disk_usage'] = disk_usage()
    except:
        summary['disk_usage'] = None

    sources = []
    word_count = 0
    tried_count = 0
    total_entries = 0

    for ds in db.query(DataSource).all():
        # TODO: Any way to avoid doing separate queries?
        stat = ds.statistics.order_by(Statistic.date.desc()).first()
        if not stat:
            continue

        source_info = {'domain': ds.domain}
        source_info.update(get_source_stats(stat))
        sources.append(source_info)

        word_count += stat.word_count
        tried_count += stat.entry_count_tried
        total_entries += stat.entry_count_total

    summary['word_count'] = word_count
    if total_entries:
        summary['completion'] = tried_count / float(total_entries)
    else:
        summary['completion'] = 0.0

    db.remove()

    return jsonify(summary=summary, sources=sources)


@app.route("/api/sources/<domain>")
def source_detail(domain):
    data_source = db.query(DataSource).filter_by(domain=domain).first()
    if not data_source:
        abort(404)

    summary = {}
    summary['domain'] = domain

    stat = data_source.statistics.order_by(Statistic.date.desc()).first()
    if stat:
        summary['document_count'] = stat.document_count
        summary['word_count'] = stat.word_count
    else:
        summary['document_count'] = 0
        summary['word_count'] = 0

    if stat and stat.entry_count_total:
        summary['completion'] = (
            stat.entry_count_tried / float(stat.entry_count_total)
        )
    else:
        summary['completion'] = 0.0

    if stat and stat.entry_count_tried:
        summary['successful'] = (
            stat.document_count / float(stat.entry_count_tried)
        )
    else:
        summary['successful'] = 0.0

    # TODO: Should tags be per-source?
    document = db.query(Document).join(Entry).join(DataSource)\
                 .filter(DataSource.domain == domain)\
                 .first()
    if document:
        summary['tags'] = json.loads(document.tags)
    else:
        summary['tags'] = []

    db.remove()

    return jsonify(summary=summary)


@app.route("/api/dashboard/word-count")
def word_count():
    query = {"aggs": {"words": {"sum": {"field": "word_count"}}}}
    response = es.search(
        index='nabu', doc_type='document',
        search_type='count', body=query
    )
    return jsonify(word_count=response['aggregations']['words']['value'])


@app.route("/api/dashboard/totals")
def dashboard():
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
            'value': bucket['words']['value'],
        })

    return jsonify(data=result)


@app.route("/api/dashboard/over-time")
def dashboard_over_time():
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
            'value': on_day,
        })

    # Fill up the missing days with zeros.
    for source in result:
        missing_days = days - set(map(lambda d: d['day'], source['value']))
        for day in missing_days:
            source['value'].append({
                'day': day,
                'value': 0,
            })
        source['value'].sort(key=lambda d: d['day'])

    return jsonify(data=result)


if __name__ == '__main__':
    app.run(debug=True)