from flask import Blueprint, jsonify, abort, request

from nabu.core.models import db, Embedding, TestSet, EvaluationTask
from nabu.vectors.tasks import (
    app as celery_app, train, test_full, test_missing, test_single,
)


bp = Blueprint('jobs', __name__, url_prefix='/jobs')


@bp.route("/api/embedding/<embedding_id>/train-start", methods=['POST'])
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


@bp.route("/api/embedding/<embedding_id>/train-status")
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


@bp.route("/api/embedding/<embedding_id>/train-cancel", methods=['POST'])
def training_cancel(embedding_id):
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding or embedding.trained or not embedding.task_id:
        abort(404)

    celery_app.control.revoke(embedding.task_id, terminate=True)
    embedding.task_id = None

    db.merge(embedding)
    db.commit()

    return jsonify(succes=True)


@bp.route("/api/embedding/<embedding_id>/evaluate-start", methods=['POST'])
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


@bp.route("/api/evaluate-status/<task_id>")
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


@bp.route("/api/evaluate-status")
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


@bp.route("/api/evaluate-cancel/<task_id>", methods=['POST'])
def evaluation_cancel(task_id):
    task = db.query(EvaluationTask).get(task_id)
    if not task or not task.task_id:
        abort(404)

    celery_app.control.revoke(task.task_id, terminate=True)

    # Delete the associated EvaluationTask.
    db.delete(task)
    db.commit()

    return jsonify(succes=True)
