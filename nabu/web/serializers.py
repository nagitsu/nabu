from elasticsearch import ElasticsearchException
from flask import url_for

from nabu.core.models import Embedding, TestSet


def serialize_testing_job(testing_job):
    serialized = {
        'id': testing_job.id,
        'embedding_id': testing_job.embedding.id,
        'testset_id': testing_job.testset.id,
        'embedding_name': testing_job.embedding.name,
        'testset_name': testing_job.testset.name,

        'progress': testing_job.progress,
        'status': testing_job.status,

        'scheduled_date': testing_job.scheduled_date,
        'elapsed_time': testing_job.elapsed_time,
    }
    return serialized


def serialize_training_job(training_job):
    serialized = {
        'id': training_job.id,
        'embedding_id': training_job.embedding.id,
        'name': training_job.embedding.name,

        'progress': training_job.progress,
        'status': training_job.status,

        'scheduled_date': training_job.scheduled_date,
        'elapsed_time': training_job.elapsed_time,
    }
    return serialized


def serialize_embedding(embedding, summary=True):
    if summary:
        serialized = {
            'id': embedding.id,
            'name': embedding.name,
            'description': embedding.description,
            'model': embedding.model,
            'status': embedding.status,
        }

    else:
        if embedding.training_job:
            training_job = serialize_training_job(embedding.training_job)
        else:
            training_job = None

        url = url_for('.download_embedding', embedding_id=embedding.id)
        serialized = {
            'id': embedding.id,
            'name': embedding.name,
            'description': embedding.description,

            'model': embedding.model,
            'parameters': embedding.parameters,
            'corpus': {
                'size': embedding.corpus_size,
                'query': embedding.query,
                'preprocessing': embedding.preprocessing,
            },

            'status': embedding.status,
            'training_job': training_job,
            'download_link': url,
        }

    return serialized


def deserialize_embedding(data):
    existing = set(data.keys())
    needed = {'model', 'description', 'parameters', 'query', 'preprocessing'}
    if existing != needed:
        message = "missing keys: {}".format(needed - existing)
        return None, message

    # TODO: Validate parameters and/or preprocessing.
    try:
        embedding = Embedding(
            description=data['description'],
            model=data['model'],
            parameters=data['parameters'],
            query=data['query'],
            preprocessing=data['preprocessing'],
        )
    except ElasticsearchException:
        return None, "invalid query"

    return embedding, None


def serialize_testset(testset, summary=True):
    if summary:
        serialized = {
            'id': testset.id,
            'name': testset.name,
            'description': testset.description,
            'type': testset.test_type,
        }

    else:
        url = url_for('.download_testset', testset_id=testset.id)
        serialized = {
            'id': testset.id,
            'name': testset.name,
            'description': testset.description,
            'type': testset.test_type,
            'sample_entry': testset.sample_entry,
            'download_link': url,
        }

    return serialized


def deserialize_testset(data):
    existing = set(data.keys())
    needed = {'description', 'type', 'file', 'name'}
    if existing != needed:
        message = "missing keys: {}".format(needed - existing)
        return None, message

    testset = TestSet(
        name=data['name'],
        description=data['description'],
        test_type=data['type'],
    )

    try:
        data['file'].save(testset.full_path)
    except Exception as e:
        return None, str(e)

    return testset, None


def serialize_result(result, summary=True):
    if summary:
        serialized = {
            'embedding_id': result.embedding_id,
            'testset_id': result.testset_id,
            'creation_date': result.creation_date,
            'accuracy': result.accuracy,
            'embedding_rank': result.rank,
        }
    else:
        serialized = {
            'embedding_id': result.embedding_id,
            'testset_id': result.testset_id,
            'creation_date': result.creation_date,
            'accuracy': result.accuracy,
            'extended': result.extended,
            'embedding_rank': result.rank,
        }
    return serialized
