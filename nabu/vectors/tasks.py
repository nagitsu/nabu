import time

from functools import partial

from celery import Celery

from nabu.core import settings
from nabu.core.models import db, Embedding, TestSet, Result, EvaluationTask, TrainingJob
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
    'nabu.vectors.tasks.test_single': {'queue': 'testing'},
    'nabu.vectors.tasks.test_full': {'queue': 'testing'},
    'nabu.vectors.tasks.test_missing': {'queue': 'testing'},
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
def test_single(self, evaluationtask_id, embedding_id, testset_id):
    evaluationtask = db.query(EvaluationTask).get(evaluationtask_id)
    embedding = db.query(Embedding).get(embedding_id)
    testset = db.query(TestSet).get(testset_id)

    existing_result = db.query(Result).filter(
        Result.testset == testset,
        Result.embedding == embedding
    ).first()

    if existing_result:
        db.delete(existing_result)
        db.commit()

    def report(progress):
        self.update_state(state='PROGRESS', meta={'progress': progress})

    evaluate(embedding, testset, report=report)

    # Delete the associated EvaluationTask when finished.
    db.delete(evaluationtask)
    db.commit()


@app.task(bind=True)
def test_full(self, evaluationtask_id, embedding_id):
    evaluationtask = db.query(EvaluationTask).get(evaluationtask_id)
    embedding = db.query(Embedding).get(embedding_id)

    # Remove existing results for the embedding.
    db.query(Result).filter(Result.embedding == embedding)\
                    .delete(synchronize_session=False)
    db.commit()

    def report(base, scale, progress):
        self.update_state(
            state='PROGRESS',
            meta={'progress': base + scale * progress}
        )

    testsets = db.query(TestSet).all()
    model = embedding.load_model()  # Preload the model.
    for idx, testset in enumerate(testsets):
        report_func = partial(report, idx / len(testsets), 1 / len(testsets))
        evaluate(embedding, testset, model=model, report=report_func)

    # Delete the associated EvaluationTask when finished.
    db.delete(evaluationtask)
    db.commit()


@app.task(bind=True)
def test_missing(self, evaluationtask_id, embedding_id):
    evaluationtask = db.query(EvaluationTask).get(evaluationtask_id)
    embedding = db.query(Embedding).get(embedding_id)

    existing = db.query(TestSet.id).join(Result).join(Embedding)\
                 .filter(Embedding.id == embedding_id)
    testsets = db.query(TestSet).filter(~TestSet.id.in_(existing))
    if not testsets:
        # Avoid loading the model if nothing to test.
        return []

    def report(base, scale, progress):
        self.update_state(
            state='PROGRESS',
            meta={'progress': base + scale * progress}
        )

    model = embedding.load_model()  # Preload the model.
    for idx, testset in enumerate(testsets):
        report_func = partial(report, idx / len(testsets), 1 / len(testsets))
        evaluate(embedding, testset, model=model, report=report_func)

    # Delete the associated EvaluationTask when finished.
    db.delete(evaluationtask)
    db.commit()
