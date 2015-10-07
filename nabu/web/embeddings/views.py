from flask import Blueprint, jsonify, request, abort

from nabu.core.models import db, Embedding
from nabu.web.serializers import serialize_embedding, deserialize_embedding


bp = Blueprint('embeddings', __name__, url_prefix='/embeddings')


@bp.route('/', methods=['GET'])
def list_embeddings():
    embeddings = db.query(Embedding).all()

    data = [serialize_embedding(emb) for emb in embeddings]
    meta = {'count': len(data)}

    return jsonify(data=data, meta=meta)


@bp.route('/', methods=['POST'])
def create_embedding():
    data = request.get_json(force=True)
    embedding, error = deserialize_embedding(data)

    if error:
        return jsonify(error='Bad Request', message=error), 400

    db.add(embedding)
    db.commit()

    return jsonify(data=serialize_embedding(embedding, summary=False)), 201


@bp.route('/<embedding_id>/', methods=['GET'])
def view_embedding(embedding_id):
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        abort(404)
    return jsonify(data=serialize_embedding(embedding, summary=False))


@bp.route('/<embedding_id>/', methods=['POST'])
def update_embedding(embedding_id):
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        abort(404)

    data = request.get_json(force=True)
    embedding.description = data['description']
    embedding = db.merge(embedding)
    db.commit()

    return jsonify(data=serialize_embedding(embedding, summary=False))


@bp.route('/<embedding_id>/', methods=['DELETE'])
def delete_embedding(embedding_id):
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        abort(404)

    embedding.clean_up()
    db.delete(embedding)
    db.commit()

    return '', 204
