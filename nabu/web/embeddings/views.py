import os
import zipstream

from flask import Blueprint, jsonify, request, abort, Response

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


@bp.route('/<embedding_id>/download/', methods=['GET'])
def download_embedding(embedding_id):
    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        abort(404)

    def content_streamer():
        z = zipstream.ZipFile(
            mode='w',
            compression=zipstream.ZIP_DEFLATED
        )

        open_files = []
        for path in embedding.get_all_files():
            current_file = open(path, 'rb')
            open_files.append(current_file)

            # Get the actual file name.
            file_name = os.path.split(path)[-1]
            z.write_iter(file_name, current_file)

        for chunk in z:
            yield chunk

        for f in open_files:
            f.close()

    response = Response(content_streamer(), mimetype="application/zip")
    disposition = "attachment; filename={}.zip".format(embedding.file_name)
    response.headers['Content-Disposition'] = disposition
    return response


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
