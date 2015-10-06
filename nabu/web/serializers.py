from nabu.core.models import Embedding


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
