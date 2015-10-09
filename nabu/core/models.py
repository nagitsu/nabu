import gensim

from celery.result import AsyncResult

from datetime import datetime

from sqlalchemy import (
    create_engine, Boolean, Column, DateTime, ForeignKey, Integer, String,
    Text, Float,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker, scoped_session

from nabu.core import settings
from nabu.core.index import es
from nabu.vectors.utils import read_analogies


engine = create_engine(
    settings.DATABASE_ENGINE,
    pool_size=50,
    max_overflow=100
)

Base = declarative_base()


class DataSource(Base):
    """
    A source of documents.
    """
    __tablename__ = 'data_sources'

    id = Column(Integer, primary_key=True, nullable=False)
    domain = Column(String, unique=True, nullable=False)

    # Number of concurrent requests to perform for this DataSource.
    concurrency = Column(Integer, nullable=False, default=5)

    # Whether to scrape entries from this source.
    active = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return "<DataSource('{}')>".format(self.domain)


def document_word_count(context):
    """
    Calculate the word count for a document.
    """
    return len(context.current_parameters['content'].split())


# TODO: Will live in ElasticSearch in the future.
class Document(Base):
    """
    A document with usable data.
    """
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, nullable=False)
    # The document's actual content.
    content = Column(Text, nullable=False)
    # May be `clean`, `html`. State the content is in.
    content_type = Column(String, nullable=False)
    # Metadata for the Document, may have a date, an author, a title, etc.
    # TODO: Use some kind of JSONField, or PostgreSQL's json field.
    metadata_ = Column(Text, nullable=False, default="{}")
    # E.g. `['news', 'Uruguay']`.
    tags = Column(Text, nullable=False, default="[]")

    # Document derived from this Entry, if any.
    entry_id = Column(Integer, ForeignKey('entries.id'),
                      nullable=False, index=True)
    entry = relationship('Entry', backref=backref('documents', lazy='dynamic'))

    # Denormalized fields.
    word_count = Column(Integer, nullable=False, default=document_word_count)

    def __repr__(self):
        return "<Document('{}')>".format(self.id)


class Entry(Base):
    """
    An entry for an online document to be scraped.
    """
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True, nullable=False)
    # May be `success`, `failure`, `notfound`, `pending`, `unparseable`,
    # `more_entries`, `multiple`.
    outcome = Column(String, nullable=False, default='pending')
    # DataSource-level ID (e.g. Observador's article ID).
    # TODO: Add a unique constraint between this and data_source_id.
    source_id = Column(String, nullable=False, index=True)

    added = Column(DateTime, nullable=False, default=datetime.now)
    last_tried = Column(DateTime, nullable=True)
    number_of_tries = Column(Integer, nullable=False, default=0)

    # DataSource from which this Entry originates.
    data_source_id = Column(Integer, ForeignKey('data_sources.id'), index=True)
    data_source = relationship('DataSource',
                               backref=backref('entries', lazy='dynamic'))

    def __repr__(self):
        return "<Entry('{}')>".format(self.id)


def get_corpus_size(context):
    """
    Calculate the word count for a document.
    """
    corpus_query = context.current_parameters['query']
    query = {
        'query': corpus_query,
        'aggs': {
            'words': {
                'sum': {
                    'field': 'word_count'
                }
            }
        }
    }
    response = es.search(
        index='nabu', doc_type='document',
        search_type='count', body=query
    )
    return response['aggregations']['words']['value']


class Embedding(Base):
    __tablename__ = 'embeddings'

    id = Column(Integer, primary_key=True, nullable=False)

    description = Column(Text, nullable=False)

    model = Column(String, nullable=False)  # May be `word2vec` or `glove`.
    parameters = Column(JSONB, default={})
    query = Column(JSONB, default={})
    preprocessing = Column(JSONB, default={})
    corpus_size = Column(Integer, nullable=False, default=get_corpus_size)

    creation_date = Column(DateTime, nullable=False, default=datetime.now)
    # May be `UNTRAINED`, `TRAINING`, or `TRAINED`.
    status = Column(String, nullable=False, default='UNTRAINED')

    def __repr__(self):
        return "<Embedding('{}', '{}')>".format(
            self.model,
            self.id,
        )

    @property
    def name(self):
        if self.model == 'word2vec':
            name = "{} algo={} dim={} win={} alpha={} hs={} neg={}".format(
                self.model,
                self.parameters.get('algorithm'),
                self.parameters.get('dimension'),
                self.parameters.get('window'),
                self.parameters.get('alpha'),
                self.parameters.get('hsoftmax'),
                self.parameters.get('negative'),
            )
        else:
            name = self.model

        return name

    @property
    def file_name(self):
        return "emb{}-{}".format(self.id, self.model)

    @property
    def full_path(self):
        return '{}{}'.format(settings.EMBEDDING_PATH, self.file_name)

    @property
    def status(self):
        # TODO: Return the status correctly.
        if self.elapsed_time:
            return 'TRAINED'
        elif self.task_id:
            return 'TRAINING'
        else:
            return 'UNTRAINED'

    @property
    def trained(self):
        return self.elapsed_time

    def load_model(self):
        if self.model == 'word2vec':
            model = gensim.models.Word2Vec.load(self.full_path)
        else:
            raise Exception("Cannot load model type.")
        return model

    def clean_up(self):
        """
        Cleans up all data related to the Embedding.

        Will delete all its files, cancel any ongoing tasks, and delete
        Results, TrainingJobs and TestingJobs. After this method is called, the
        Embedding will stay in an inconsistent state, be careful.
        """
        # TODO: Implement.


class TestSet(Base):
    __tablename__ = 'testsets'

    id = Column(Integer, primary_key=True, nullable=False)

    name = Column(String, nullable=False, unique=True)  # A01, <type><num>.
    test_type = Column(String, nullable=False)  # May be `analogies`.
    description = Column(Text, nullable=False)

    def __repr__(self):
        return "<TestSet('{}')>".format(self.name)

    @property
    def file_name(self):
        """Path relative to test folder."""
        return "{}-{}.txt".format(self.name, self.test_type)

    @property
    def full_path(self):
        return "{}{}".format(settings.TEST_PATH, self.file_name)

    @property
    def sample_entry(self):
        if self.test_type == 'analogies':
            first_analogy = next(read_analogies(self.full_path))
            entry = "{} is to {} as {} is to... ({})".format(*first_analogy)
        else:
            entry = ""

        return entry

    def clean_up(self):
        """
        Cleans up all data related to the TestSet.

        Will delete all its files, cancel any ongoing tasks, and delete
        Results, TrainingJobs and TestingJobs. After this method is called, the
        Embedding will stay in an inconsistent state, be careful.
        """
        # TODO: Implement.


class Result(Base):
    __tablename__ = 'results'

    testset_id = Column(
        Integer,
        ForeignKey('testsets.id'),
        primary_key=True
    )
    testset = relationship(
        'TestSet',
        backref=backref('results', lazy='dynamic')
    )
    embedding_id = Column(
        Integer,
        ForeignKey('embeddings.id'),
        primary_key=True
    )
    embedding = relationship(
        'Embedding',
        backref=backref('results', lazy='dynamic')
    )

    creation_date = Column(DateTime, nullable=False, default=datetime.now)
    testing_job_id = Column(Integer, ForeignKey('testingjobs.id'), unique=True)
    testing_job = relationship(
        'TestingJob',
        backref=backref('results', lazy='dynamic')
    )

    accuracy = Column(Float, nullable=False)
    # `extended` stores further evaluation results (e.g. F1 score, etc.).
    extended = Column(JSONB, default={})

    def __repr__(self):
        return "<Result('{}', '{}')>".format(
            self.embedding_id,
            self.testset_id,
        )


class TestingJob(Base):
    __tablename__ = 'testingjobs'

    id = Column(Integer, primary_key=True, nullable=False)

    scheduled_date = Column(DateTime, nullable=False, default=datetime.now)
    elapsed_time = Column(Integer, nullable=True, default=None)  # In seconds.
    task_id = Column(String, nullable=True, default=None)

    testset_id = Column(Integer, ForeignKey('testsets.id'))
    testset = relationship(
        'TestSet',
        backref=backref('test_jobs', lazy='dynamic')
    )

    embedding_id = Column(Integer, ForeignKey('embeddings.id'))
    embedding = relationship(
        'Embedding',
        backref=backref('training_jobs', lazy='dynamic')
    )

    def __repr__(self):
        return "<TestingJob('{}')>".format(self.id)

    @property
    def status(self):
        # `task_id` only when the task is actually running. If not present,
        # it's either finished or not started yet.
        if self.task_id:
            result = AsyncResult(self.task_id)
            status = result.state
        elif self.elapsed_time:
            status = 'SUCCESS'
        else:
            status = 'PENDING'

        return status

    @property
    def progress(self):
        if self.task_id:
            result = AsyncResult(self.task_id)
            # TODO: See if there's a cleaner way of obtaining the progress.
            try:
                progress = result.result.get('progress')
            except AttributeError:
                progress = 0.0
        elif self.elapsed_time:
            progress = 100.0
        else:
            progress = 0.0

        return progress


class TrainingJob(Base):
    __tablename__ = 'trainingjobs'

    id = Column(Integer, primary_key=True, nullable=False)

    scheduled_date = Column(DateTime, nullable=False, default=datetime.now)
    elapsed_time = Column(Integer, nullable=True, default=None)  # In seconds.
    task_id = Column(String, nullable=True, default=None)

    embedding_id = Column(Integer, ForeignKey('embeddings.id'), unique=True)
    embedding = relationship(
        'Embedding',
        backref=backref('training_job', lazy='dynamic')
    )

    def __repr__(self):
        return "<TrainingJob('{}')>".format(self.id)

    @property
    def status(self):
        # `task_id` only when the task is actually running. If not present,
        # it's either finished or not started yet.
        if self.task_id:
            result = AsyncResult(self.task_id)
            status = result.state
        elif self.elapsed_time:
            status = 'SUCCESS'
        else:
            status = 'PENDING'

        return status

    @property
    def progress(self):
        if self.task_id:
            result = AsyncResult(self.task_id)
            # TODO: See if there's a cleaner way of obtaining the progress.
            try:
                progress = result.result.get('progress')
            except AttributeError:
                progress = 0.0
        elif self.elapsed_time:
            progress = 100.0
        else:
            progress = 0.0

        return progress


# TODO: Shouldn't be done like this. Should be done in alembic.
# Create the schema if it doesn't already.
Base.metadata.create_all(engine)


# Default database session.
session_factory = sessionmaker(bind=engine)
db = scoped_session(session_factory)
