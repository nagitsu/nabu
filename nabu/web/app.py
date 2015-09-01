import json
import os
import re
import subprocess

from datetime import datetime, timedelta
from flask import abort, Flask, jsonify, request
from sqlalchemy.sql import func

from nabu.core import settings
from nabu.core.models import (
    db, DataSource, Document, Entry, Embedding, TestSet, EvaluationTask,
)
from nabu.core.index import es
from nabu.vectors.tasks import (
    app as celery_app, train, test_full, test_missing, test_single,
)


app = Flask(__name__)


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


@app.route("/api/embedding/", methods=['POST'])
def create_embedding():
    data = request.get_json()

    existing = set(data.keys())
    needed = {'model', 'description', 'parameters', 'query'}
    if existing != needed:
        abort(400)

    existing_params = set(data['parameters'].keys())
    needed_params = {
        'dimension', 'min_count', 'window', 'subsampling', 'algorithm',
        'negative_sampling', 'hierarchical_softmax', 'epochs', 'alpha',
        'word_tokenizer', 'sentence_tokenizer', 'lowercase_tokens',
        'remove_accents',
    }
    if existing_params != needed_params:
        abort(400)

    # TODO: parameter defaults in JS:
    # size=100, min_count=5, window=5, sample=0, sg=1, hs=1, negative=0,
    # iter=1, alpha=0.025, word_tokenizer='alphanum',
    # sentece_tokenizer='periodspace'

    embedding = Embedding(
        model=data['model'],
        description=data['description'],
        query=data['query'],
        parameters=data['parameters']
    )

    db.add(embedding)
    db.commit()

    return jsonify(id=embedding.id)


@app.route("/api/embedding/", methods=['GET'])
def list_embeddings():
    training_only = request.args.get('training_only', False)
    if training_only:
        embeddings = db.query(Embedding)\
                       .filter(Embedding.elapsed_time == None)\
                       .filter(Embedding.task_id != None)  # noqa
    else:
        embeddings = db.query(Embedding).all()

    data = []
    for embedding in embeddings:
        serialized = {
            'id': embedding.id,
            'description': embedding.description,
        }

        if embedding.task_id:
            result = train.AsyncResult(embedding.task_id)
            serialized['state'] = result.state
            try:
                serialized['progress'] = result.result.get('progress')
            except AttributeError:
                serialized['progress'] = 0.0
        elif embedding.elapsed_time:
            serialized['state'] = 'SUCCESS'
        else:
            serialized['state'] = 'NOT_STARTED'

        data.append(serialized)

    return jsonify(
        result=data,
        count=len(data)
    )


@app.route("/api/embedding/<embedding_id>/")
def view_embedding(embedding_id):
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        abort(404)

    if embedding.task_id:
        result = train.AsyncResult(embedding.task_id)
        state = result.state
        try:
            progress = result.result.get('progress')
        except AttributeError:
            progress = 0.0
    elif embedding.elapsed_time:
        state = 'SUCCESS'
        progress = 100.0
    else:
        state = 'NOT_STARTED'
        progress = 0.0

    results = []
    for result in embedding.results.all():
        results.append({
            'testset': {
                'id': result.testset.id,
                'name': result.testset.name,
            },
            'accuracy': result.accuracy,
            'extended': result.extended,
            'creation_date': result.creation_date,
            'elapsed_time': result.elapsed_time,
        })

    return jsonify(
        id=embedding.id,
        description=embedding.description,
        model=embedding.model,
        parameters=embedding.parameters,
        query=embedding.query,
        creation_date=embedding.creation_date,
        elapsed_time=embedding.elapsed_time,
        state=state,
        progress=progress,
        evaluation=results,
    )


@app.route("/api/embedding/<embedding_id>/", methods=['DELETE'])
def delete_embedding(embedding_id):
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        abort(404)

    if embedding.trained:
        # Remove the model files if the embedding has been trained.
        if embedding.model == 'word2vec':
            path = os.path.join(settings.EMBEDDING_PATH, embedding.file_name)
            try:
                os.remove(path)
            except OSError:
                pass

            try:
                os.remove('{}.syn0.npy'.format(path))
            except OSError:
                pass

            try:
                os.remove('{}.syn1.npy'.format(path))
            except OSError:
                pass
        else:
            # Not implemented yet.
            abort(500)
    elif embedding.task_id:
        # Kill the task if it has been enqueued.
        celery_app.control.revoke(embedding.task_id, terminate=True)

    db.delete(embedding)
    db.commit()

    return jsonify(success=True)


@app.route("/api/embedding/<embedding_id>/train-start", methods=['POST'])
def training_start(embedding_id):
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        abort(404)

    result = train.delay(embedding_id)

    # Set the task ID for the embedding.
    embedding.task_id = result.task_id
    db.merge(embedding)
    db.commit()

    return jsonify(started=True)


@app.route("/api/embedding/<embedding_id>/train-status")
def training_status(embedding_id):
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        abort(404)

    if embedding.trained:
        return jsonify(state='SUCCESS')

    task_id = embedding.task_id
    result = train.AsyncResult(task_id)

    try:
        progress = result.result.get('progress')
    except AttributeError:
        progress = 0.0

    return jsonify(
        state=result.state,
        progress=progress,
    )


@app.route("/api/embedding/<embedding_id>/train-cancel", methods=['POST'])
def training_cancel(embedding_id):
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding or embedding.trained or not embedding.task_id:
        abort(404)

    celery_app.control.revoke(embedding.task_id, terminate=True)
    embedding.task_id = None

    db.merge(embedding)
    db.commit()

    return jsonify(succes=True)


@app.route("/api/embedding/<embedding_id>/evaluate-start", methods=['POST'])
def evaluation_start(embedding_id):
    """
    {
      "testset": <id> | 'full' | 'missing'
    }
    """
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        abort(404)

    try:
        test_type = request.get_json().get('testset')
    except KeyError:
        abort(400)

    if test_type != 'full' and test_type != 'missing':
        testset = db.query(TestSet).get(test_type)
        if not testset:
            abort(404)
        else:
            test_type = 'single'

    task = EvaluationTask(embedding=embedding.id, test_type=test_type)
    db.add(task)
    db.commit()

    if test_type == 'full':
        result = test_full.delay(task.id, embedding.id)
    elif testset == 'missing':
        result = test_missing.delay(task.id, embedding.id)
    else:
        result = test_single.delay(task.id, embedding.id, testset.id)

    # Set the task ID for the EvaluationTask.
    task.task_id = result.task_id
    db.merge(task)
    db.commit()

    return jsonify(task_id=task.id)


@app.route("/api/evaluate-status/<task_id>")
def evaluation_status(task_id):
    task = db.query(EvaluationTask).get(task_id)
    if not task:
        # May be due to it never existing or due to it having finished.
        abort(404)

    if task.test_type == 'full':
        result = test_full.AsyncResult(task.task_id)
    elif task.test_type == 'missing':
        result = test_missing.AsyncResult(task.task_id)
    else:
        result = test_single.AsyncResult(task.task_id)

    try:
        progress = result.result.get('progress')
    except AttributeError:
        progress = 0.0

    return jsonify(
        state=result.state,
        progress=progress,
    )


@app.route("/api/evaluate-status")
def evaluation_status_list():
    results = []

    tasks = db.query(EvaluationTask).all()
    for task in tasks:
        if task.test_type == 'full':
            result = test_full.AsyncResult(task.task_id)
        elif task.test_type == 'missing':
            result = test_missing.AsyncResult(task.task_id)
        else:
            result = test_single.AsyncResult(task.task_id)

        try:
            progress = result.result.get('progress')
        except AttributeError:
            progress = 0.0

        results.append({
            'id': task.id,
            'test_type': task.test_type,
            'embedding_id': task.embedding,
            'state': result.state,
            'progress': progress
        })

    return jsonify(data=results)


@app.route("/api/evaluate-cancel/<task_id>", methods=['POST'])
def evaluation_cancel(task_id):
    task = db.query(EvaluationTask).get(task_id)
    if not task or not task.task_id:
        abort(404)

    celery_app.control.revoke(task.task_id, terminate=True)

    # Delete the associated EvaluationTask.
    db.delete(task)
    db.commit()

    return jsonify(succes=True)


if __name__ == '__main__':
    app.run(debug=True)
