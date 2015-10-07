from nabu.core.models import Embedding, TestSet


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
        serialized = {
            'id': embedding.id,
            'name': embedding.name,
            'description': embedding.description,

            'model': embedding.model,
            'parameters': embedding.parameters,
            'corpus': {
                'size': 12345678,  # TODO: Will be `corpus_size`.
                'query': embedding.query,
                'preprocessing': {},  # TODO: Will be `preprocessing`.
            },

            'status': embedding.status,
            # TODO: Will be the TrainingJob model ID, which will never cease to
            # exist.
            'training_job_id': embedding.task_id,
            # TODO: Needs to add model downloading functionality.
            'download_link': 'not-available',
        }

    return serialized


def deserialize_embedding(data):
    existing = set(data.keys())
    needed = {'model', 'description', 'parameters', 'query', 'preprocessing'}
    if existing != needed:
        message = "missing keys: {}".format(needed - existing)
        return None, message

    # TODO: May raise exception once corpus_size is auto-filled.
    embedding = Embedding(
        description=data['description'],
        model=data['model'],
        parameters=data['parameters'],
        query=data['query'],
        preprocessing=data['preprocessing'],
    )

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
        serialized = {
            'id': testset.id,
            'name': testset.name,
            'description': testset.description,
            'type': testset.test_type,
            'sample_entry': testset.sample_entry,
            # TODO: Needs to point to the correct link.
            'download_link': 'not-available',
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


def serialize_result(result):
    serialized = {
        'embedding_id': result.embedding_id,
        'testset_id': result.testset_id,
        'creation_date': result.creation_date,
        'elapsed_time': result.elapsed_time,
        'accuracy': result.accuracy,
        'extended': result.extended,
    }
    return serialized
