from itertools import chain

from flask import Blueprint, jsonify, request, abort, Response

from nabu.core.models import db, TestSet
from nabu.web.serializers import serialize_testset, deserialize_testset


bp = Blueprint('testsets', __name__, url_prefix='/testsets')


@bp.route('/', methods=['GET'])
def list_testsets():
    testsets = db.query(TestSet).all()

    data = [serialize_testset(tst) for tst in testsets]
    meta = {'count': len(data)}

    return jsonify(data=data, meta=meta)


@bp.route('/', methods=['POST'])
def create_testset():
    full_data = chain(request.form.items(), request.files.items())
    data = {k: v for k, v in full_data}
    testset, error = deserialize_testset(data)

    if error:
        return jsonify(error='Bad Request', message=error), 400

    db.add(testset)
    db.commit()

    return jsonify(data=serialize_testset(testset, summary=False)), 201


@bp.route('/<testset_id>/', methods=['GET'])
def view_testset(testset_id):
    testset = db.query(TestSet).get(testset_id)
    if not testset:
        abort(404)
    return jsonify(data=serialize_testset(testset, summary=False))


@bp.route('/<testset_id>/download/', methods=['GET'])
def download_testset(testset_id):
    testset = db.query(TestSet).get(testset_id)
    if not testset:
        abort(404)

    def content_streamer():
        with open(testset.full_path) as f:
            for line in f:
                yield line

    response = Response(content_streamer(), mimetype="text/plain")
    content_disposition = "attachment; filename={}".format(testset.file_name)
    response.headers['Content-Disposition'] = content_disposition
    return response


@bp.route('/<testset_id>/', methods=['POST'])
def update_testset(testset_id):
    testset = db.query(TestSet).get(testset_id)
    if not testset:
        abort(404)

    data = request.get_json(force=True)
    testset.name = data['name']
    testset.description = data['description']
    testset = db.merge(testset)
    db.commit()

    return jsonify(data=serialize_testset(testset, summary=False))


@bp.route('/<testset_id>/', methods=['DELETE'])
def delete_testset(testset_id):
    testset = db.query(TestSet).get(testset_id)
    if not testset:
        abort(404)

    testset.clean_up()
    db.delete(testset)
    db.commit()

    return '', 204
