from flask import Blueprint, jsonify, request, abort

from nabu.core.models import db, Result
from nabu.web.serializers import serialize_result


bp = Blueprint('results', __name__, url_prefix='/results')


@bp.route('/', methods=['GET'])
def list_results():
    embedding_id = request.args.get('embedding', None)
    testset_id = request.args.get('testset', None)

    query = db.query(Result)
    if embedding_id:
        query = query.filter(Result.embedding_id == int(embedding_id))
    if testset_id:
        query = query.filter(Result.testset_id == int(testset_id))
    results = query.all()

    data = [serialize_result(res) for res in results]
    meta = {'count': len(data)}

    return jsonify(data=data, meta=meta)


@bp.route('/<embedding_id>/<testset_id>/', methods=['GET'])
def view_result(embedding_id, testset_id):
    result = db.query(Result).get((embedding_id, testset_id))
    if not result:
        abort(404)
    return jsonify(data=serialize_result(result))


@bp.route('/<embedding_id>/<testset_id>/', methods=['DELETE'])
def delete_result(embedding_id, testset_id):
    result = db.query(Result).get((embedding_id, testset_id))
    if not result:
        abort(404)

    db.delete(result)
    db.commit()

    return '', 204
