import os

from flask import Flask, jsonify
from flask.ext.cors import CORS

from nabu.web import corpus, embeddings, enums, jobs, results, testsets


DEFAULT_BLUEPRINTS = (
    corpus.bp,
    embeddings.bp,
    enums.bp,
    jobs.bp,
    testsets.bp,
    results.bp,
)


def create_app(config=None):
    blueprints = DEFAULT_BLUEPRINTS

    app = Flask(__name__)
    configure_app(app, config)
    configure_extensions(app)
    configure_blueprints(app, blueprints)
    configure_error_handlers(app)

    return app


def configure_app(app, config):
    environment = os.environ.get('NABU_ENV')
    app.config['ENV'] = 'DEV' if environment == 'DEV' else 'PROD'

    if app.config['ENV'] == 'DEV':
        app.debug = True


def configure_extensions(app):
    if app.config['ENV'] == 'DEV':
        CORS(app)


def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(
            {'message': error.description, 'error': 'Bad Request'}
        ), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify(
            {'message': error.description, 'error': 'Unauthorized'}
        ), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify(
            {'message': error.description, 'error': 'Forbidden'}
        ), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify(
            {'message': error.description, 'error': 'Not found'}
        ), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify(
            {'message': error.description, 'error': 'Method Not Allowed'}
        ), 405

    @app.errorhandler(500)
    def server_error(error):
        error_json = {'error': 'Internal Server Error'}
        if hasattr(error, 'description'):
            error_json['message'] = error.description
        return jsonify(), 500


app = create_app()
