import time

from celery import Celery

from nabu.core import settings
from nabu.core.models import db, Embedding
from nabu.vectors.training import train as train_model


app = Celery(
    'tasks',
    broker=settings.BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)


@app.task(bind=True)
def train(self, embedding_id):

    embedding = db.query(Embedding).get(embedding_id)
    if not embedding:
        raise Exception("Embedding doesn't exist")

    # Set the task ID for the embedding.
    embedding.task_id = self.request.id
    db.merge(embedding)
    db.commit()

    def report(progress):
        self.update_state(state='PROGRESS', meta={'progress': progress})

    start_time = time.time()
    train_model(
        embedding.parameters,
        embedding.query,
        embedding.file_name,
        report
    )
    end_time = time.time()

    # Update elapsed time and ready status on Embedding model.
    embedding.task_id = None
    embedding.elapsed_time = int(end_time - start_time)
    db.merge(embedding)
    db.commit()

    return embedding_id
