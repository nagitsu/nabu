import time

from celery import Celery

from nabu.core import settings
from nabu.core.models import db, Result, TrainingJob, TestingJob
from nabu.vectors.training import train as train_model
from nabu.vectors.evaluation import evaluate


app = Celery(
    'tasks',
    broker=settings.BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)


# Task routing configuration.
app.conf.CELERY_ROUTES = {
    'nabu.vectors.tasks.train': {'queue': 'training'},
    'nabu.vectors.tasks.test': {'queue': 'testing'},
}

# (Almost) disable visibility timeout.
app.conf.BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 432000
}


@app.task(bind=True)
def train(self, training_job_id):

    training_job = db.query(TrainingJob).get(training_job_id)
    if not training_job:
        raise Exception("TrainingJob doesn't exist")

    training_job.task_id = train.request.id
    embedding = training_job.embedding
    embedding.status = 'TRAINING'
    db.commit()

    def report(progress):
        self.update_state(state='PROGRESS', meta={'progress': progress})

    start_time = time.time()
    train_model(
        embedding.model,
        embedding.query,
        embedding.preprocessing,
        embedding.parameters,
        embedding.file_name,
        report
    )
    end_time = time.time()

    training_job.task_id = None
    training_job.elapsed_time = int(end_time - start_time)
    embedding = training_job.embedding
    embedding.status = 'TRAINED'
    db.commit()


@app.task(bind=True)
def test(self, testing_job_id):
    testing_job = db.query(TestingJob).get(testing_job_id)
    if not testing_job:
        raise Exception("TestingJob doesn't exist")

    # Update testing job's task_id.
    testing_job.task_id = test.request.id
    embedding = testing_job.embedding
    testset = testing_job.testset

    # Delete existing results, if any.
    existing_result = db.query(Result).filter(
        Result.testset == testset,
        Result.embedding == embedding
    ).first()

    if existing_result:
        db.delete(existing_result)

    db.commit()

    def report(progress):
        self.update_state(state='PROGRESS', meta={'progress': progress})

    # Initial progress report so it happens before loading the model.
    report(0.0)

    start_time = time.time()
    result = evaluate(embedding, testset, report=report)
    end_time = time.time()

    result.testing_job = testing_job
    testing_job.task_id = None
    testing_job.elapsed_time = int(end_time - start_time)
    db.commit()
