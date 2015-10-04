import os

from flask import Blueprint, jsonify, request, abort

from nabu.core import settings
from nabu.core.models import db, Embedding
from nabu.vectors.tasks import app as celery_app, train


bp = Blueprint('embeddings', __name__, url_prefix='/embeddings')


@bp.route("/api/embedding/", methods=['POST'])
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


@bp.route("/api/embedding/", methods=['GET'])
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


@bp.route("/api/embedding/<embedding_id>/")
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


@bp.route("/api/embedding/<embedding_id>/", methods=['DELETE'])
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
