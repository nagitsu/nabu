from flask import Blueprint, jsonify, abort, request

from nabu.core.models import (
    db, Embedding, TestSet, EvaluationTask, TrainingJob,
)
from nabu.vectors.tasks import (
    app as celery_app, train, test_full, test_missing, test_single,
)
from nabu.web.serializers import serialize_training_job


bp = Blueprint('jobs', __name__, url_prefix='/jobs')


@bp.route('/training/', methods=['POST'])
def create_training_job():
    embedding_id = request.get_json(force=True)['embedding_id']
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        abort(404)

    # Check if it has been trained already first.
    training_job = db.query(TrainingJob).get_by(embedding_id=embedding_id)
    if training_job:
        message = "The embedding is already trained or being trained."
        return jsonify(error='Bad Request', message=message), 400

    training_job = TrainingJob(embedding_id=embedding_id)
    db.add(training_job)
    db.commit()

    train.delay(training_job.id)

    return jsonify(data={'started': True})


@bp.route('/training/', methods=['GET'])
def list_training_jobs():
    status = request.args.get('status', None)

    # Failed jobs are included in `queued`, as their `elapsed_time` will be
    # None too.
    query = db.query(TrainingJob)
    if status == 'finished':
        query = query.filter(~TrainingJob.elapsed_time.is_(None))
    elif status == 'queued':
        query = query.filter(TrainingJob.elapsed_time.is_(None))
    training_jobs = query.all()

    data = [serialize_training_job(tj) for tj in training_jobs]
    meta = {'count': len(data)}

    return jsonify(data=data, meta=meta)


@bp.route('/training/<training_job_id>/', methods=['GET'])
def view_training_job(training_job_id):
    training_job = db.query(TrainingJob).get(training_job_id)
    if not training_job:
        abort(404)
    return jsonify(data=serialize_training_job(training_job))


@bp.route('/training/<training_job_id>/', methods=['DELETE'])
def delete_training_job(training_job_id):
    training_job = db.query(TrainingJob).get(training_job_id)
    if not training_job:
        abort(404)

    if training_job.task_id:
        celery_app.control.revoke(training_job.task_id, terminate=True)

    db.delete(training_job)
    db.commit()

    return '', 204


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
