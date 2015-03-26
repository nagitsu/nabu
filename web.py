import json
import re
import subprocess

from sqlalchemy.sql import func
from flask import abort, Flask, jsonify

from corpus.models import db, DataSource, Document, Entry


app = Flask(__name__)


def disk_usage():
    output = subprocess.check_output(['df', '-h'])
    percentage = re.findall('(\d+%) \/\n', output)[0]
    return percentage


@app.route("/api/general")
def general():
    summary = {}

    # Obtain the disk usage.
    try:
        summary['disk_usage'] = disk_usage()
    except:
        summary['disk_usage'] = None

    summary['word_count'] = db.query(func.sum(Document.word_count)).scalar()

    sources = [ds[0] for ds in db.query(DataSource.domain).all()]

    db.remove()

    return jsonify(summary=summary, sources=sources)


@app.route("/api/sources/<domain>")
def source_detail(domain):
    data_source = db.query(DataSource).filter_by(domain=domain).first()
    if not data_source:
        abort(404)

    summary = {}
    summary['domain'] = domain

    documents = db.query(Document).join(Entry).join(DataSource)\
                  .filter(DataSource.domain == domain)

    summary['document_count'] = documents.count()

    summary['word_count'] = db.query(func.sum(Document.word_count))\
                              .join(Entry)\
                              .filter(Entry.data_source == data_source)\
                              .scalar()

    entry_count = db.query(Entry).join(DataSource)\
                    .filter(DataSource.domain == domain)\
                    .count()
    successful_entries = db.query(Entry).join(DataSource)\
                           .filter(DataSource.domain == domain)\
                           .filter(Entry.outcome == 'success')\
                           .count()
    summary['success'] = successful_entries / float(entry_count)

    # TODO: Should tags be per-source?
    document = documents.first()
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
    app.run()
