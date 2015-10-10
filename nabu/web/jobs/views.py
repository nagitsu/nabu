from flask import Blueprint, jsonify, abort, request

from nabu.core.models import (
    db, Embedding, Result, TestSet, TrainingJob, TestingJob,
)
from nabu.vectors.tasks import app as celery_app, train, test
from nabu.web.serializers import serialize_training_job, serialize_testing_job


bp = Blueprint('jobs', __name__, url_prefix='/jobs')


@bp.route('/training/', methods=['POST'])
def create_training_job():
    embedding_id = request.get_json(force=True)['embedding_id']
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        abort(404)

    # Check if it has been trained already first.
    training_job = db.query(TrainingJob)\
                     .filter_by(embedding_id=embedding_id).first()
    if training_job:
        message = "The embedding is already trained or being trained."
        return jsonify(error='Bad Request', message=message), 400

    training_job = TrainingJob(embedding_id=embedding_id)
    db.add(training_job)
    db.commit()

    train.delay(training_job.id)

    return jsonify(data={'training_job_id': training_job.id})


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

    # Use the embedding's `clean_up` function, which will take care of
    # everything, including the deletion of the training job.
    embedding = training_job.embedding
    embedding.clean_up()

    return '', 204


@bp.route('/testing/', methods=['POST'])
def create_testing_job():
    data = request.get_json(force=True)
    if 'embedding_id' not in data or 'testset_id' not in data:
        abort(400)

    embedding_id = data['embedding_id']
    testset_id = data['testset_id']

    if not (embedding_id.isdigit() or testset_id.isdigit):
        return jsonify({
            'message': "At least one ID must be specified",
            'error': 'Bad Request'
        }), 400

    # Build a list of embeddings and testsets to test.
    embeddings = []
    testsets = []
    if embedding_id.isdigit():
        embedding = db.query(Embedding).get(embedding_id)
        if not embedding:
            abort(404)
        embeddings.append(embedding)

        if testset_id.isdigit():
            testset = db.query(TestSet).get(testset_id)
            testsets.append(testset)
        elif testset_id == 'full':
            testsets.extend(db.query(TestSet).all())
        elif testset_id == 'missing':
            existing = db.query(TestSet.id).join(Result).join(Embedding)\
                         .filter(Embedding.id == embedding_id)
            query = db.query(TestSet).filter(~TestSet.id.in_(existing))
            testsets.extend(query.all())

    elif testset_id.isdigit():
        testset = db.query(TestSet).get(testset_id)
        if not testset:
            abort(404)
        testsets.append(testset)

        if embedding_id.isdigit():
            embedding = db.query(Embedding).get(embedding_id)
            embeddings.append(embedding)
        elif embedding_id == 'full':
            embeddings.extend(db.query(Embedding.id).all())
        elif embedding_id == 'missing':
            existing = db.query(Embedding.id).join(Result).join(TestSet)\
                         .filter(TestSet.id == testset_id)
            query = db.query(Embedding).filter(~Embedding.id.in_(existing))
            embeddings.extend(query.all())

    # Make sure there are no Nones (i.e. all the models exist).
    if any([emb is None for emb in embeddings]):
        abort(404)
    if any([ts is None for ts in testsets]):
        abort(404)

    # Make sure the embeddings are trained already.
    embeddings = filter(lambda e: e.status == 'TRAINED', embeddings)

    # For each pair <embedding, testset>, create the necessary TestingJob,
    # deleting it first if it already exists. The result will be deleted inside
    # the task, so no need to do it here.
    jobs = []
    for embedding in embeddings:
        for testset in testsets:
            job = db.query(TestingJob)\
                    .filter_by(embedding=embedding, testset=testset)\
                    .first()
            if job and job.status in ['PENDING', 'PROGRESS']:
                # Only overwrite TestingJobs that have already run. If it's
                # still pending or running right now, we want to keep it.
                continue
            elif job:
                db.delete(job)

            job = TestingJob(testset=testset, embedding=embedding)
            jobs.append(job)
            db.add(job)

    db.commit()

    for job in jobs:
        test.delay(job.id)

    return jsonify(data={'testing_job_id': [job.id for job in jobs]})


@bp.route('/testing/', methods=['GET'])
def list_testing_jobs():
    status = request.args.get('status', None)

    # Failed jobs are included in `queued`, as their `elapsed_time` will be
    # None too.
    query = db.query(TestingJob)
    if status == 'finished':
        query = query.filter(~TestingJob.elapsed_time.is_(None))
    elif status == 'queued':
        query = query.filter(TestingJob.elapsed_time.is_(None))
    testing_jobs = query.all()

    data = [serialize_testing_job(tj) for tj in testing_jobs]
    meta = {'count': len(data)}

    return jsonify(data=data, meta=meta)


@bp.route('/testing/<testing_job_id>/', methods=['GET'])
def view_testing_job(testing_job_id):
    testing_job = db.query(TestingJob).get(testing_job_id)
    if not testing_job:
        abort(404)
    return jsonify(data=serialize_testing_job(testing_job))


@bp.route('/testing/<testing_job_id>/', methods=['DELETE'])
def delete_testing_job(testing_job_id):
    testing_job = db.query(TestingJob).get(testing_job_id)
    if not testing_job:
        abort(404)

    # If it has any result associated, delete it.
    result = db.query(Result).get(
        embedding_id=testing_job.embedding_id,
        testset_id=testing_job.testset_id
    )
    if result:
        db.delete(result)

    if testing_job.task_id:
        celery_app.control.revoke(testing_job.task_id, terminate=True)

    db.delete(testing_job)
    db.commit()

    return '', 204
