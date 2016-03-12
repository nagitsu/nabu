from flask import Blueprint, jsonify, request, abort
from sqlalchemy import func

from nabu.core.models import db, Result
from nabu.web.serializers import serialize_result


bp = Blueprint('results', __name__, url_prefix='/results')


@bp.route('/', methods=['GET'])
def list_results():
    embedding_id = request.args.get('embedding', None)
    testset_id = request.args.get('testset', None)

    # Calculate the ranking of the embedding on the testset.
    partition = func.rank().over(
        partition_by=Result.testset_id,
        order_by=Result.accuracy.desc()
    ).label('rank')
    sq = db.query(Result, partition).subquery()
    query = db.query(sq)

    if embedding_id:
        query = query.filter(sq.c.embedding_id == int(embedding_id))
    if testset_id:
        query = query.filter(sq.c.testset_id == int(testset_id))

    results = query.all()

    data = [serialize_result(res) for res in results]
    meta = {'count': len(data)}

    return jsonify(data=data, meta=meta)


@bp.route('/<embedding_id>/<testset_id>/', methods=['GET'])
def view_result(embedding_id, testset_id):
    # Calculate the ranking of the embedding on the testset.
    partition = func.rank().over(
        partition_by=Result.testset_id,
        order_by=Result.accuracy.desc()
    ).label('rank')
    sq = db.query(Result, partition).subquery()

    result = db.query(sq).filter(
        sq.c.embedding_id == embedding_id,
        sq.c.testset_id == testset_id
    ).first()

    if not result:
        abort(404)

    return jsonify(data=serialize_result(result, summary=False))


@bp.route('/<embedding_id>/<testset_id>/', methods=['DELETE'])
def delete_result(embedding_id, testset_id):
    result = db.query(Result).get((embedding_id, testset_id))
    if not result:
        abort(404)

    # Delete its testing_job first.
    db.delete(result.testing_job)
    db.delete(result)

    db.commit()

    return '', 204
