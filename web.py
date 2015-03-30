import json
import re
import subprocess

from datetime import datetime, timedelta
from flask import abort, Flask, jsonify
from sqlalchemy.sql import func

from corpus.models import db, DataSource, Document, Entry, Statistic


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
        stats.setdefault(result.data_source_id, {}).update(row)

    results = db.query(Entry.data_source_id,
                       func.count(Entry.id).label('entry_count_total'))\
                .filter(Entry.added <= limit_date)\
                .group_by(Entry.data_source_id)\
                .all()

    for result in results:
        row = dict(map(lambda f: (f, getattr(result, f)), result.keys()))
        stats.setdefault(result.data_source_id, {}).update(row)

    return stats.values()


@app.route("/api/stats/update")
def update_statistics():
    # First get the last Statistic created.
    last = db.query(Statistic).order_by(Statistic.date.desc()).first()

    now = datetime.now()
    if not last:
        # If none exist, just create one for the present.
        limit = now.replace(minute=0, second=0, microsecond=0)
        for stat in calculate_statistics(limit):
            stat['date'] = limit
            db.merge(Statistic(**stat))
    else:
        # If one exists, calculate all the hour-length intervals up to the
        # present, and calculate the statistics for each of them.
        limit = last.date + timedelta(hours=1)
        while limit <= now:
            for stat in calculate_statistics(limit):
                stat['date'] = limit
                db.merge(Statistic(**stat))
            limit += timedelta(hours=1)

    db.commit()

    # `stat` holds the last Statistic added (i.e. the most current).
    return jsonify(current=stat)


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

        sources.append(ds.domain)
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

    entries = db.query(Entry).join(DataSource)\
                .filter(DataSource.domain == domain)\
                .filter(Entry.outcome == 'success')\
                .order_by(Entry.last_tried.desc())\
                .limit(5)
    last_entries = []
    for entry in entries:
        last_entries.append({
            'date': entry.last_tried,
            'source_id': entry.source_id
        })

    db.remove()

    return jsonify(summary=summary, last_entries=last_entries)


if __name__ == '__main__':
    app.run(debug=True)
