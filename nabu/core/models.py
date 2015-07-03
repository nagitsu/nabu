from datetime import datetime

from sqlalchemy import (
    create_engine, Boolean, Column, DateTime, ForeignKey, Integer, String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker, scoped_session

from nabu.core import settings


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
    entry_id = Column(Integer, ForeignKey('entries.id'), nullable=False)
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
    # May be `success`, `failure`, `notfound`, `pending`, `unparseable`.
    outcome = Column(String, nullable=False, default='pending')
    # DataSource-level ID (e.g. Observador's article ID).
    # TODO: Add a unique constraint between this and data_source_id.
    source_id = Column(String, nullable=False)

    added = Column(DateTime, nullable=False, default=datetime.now)
    last_tried = Column(DateTime, nullable=True)
    number_of_tries = Column(Integer, nullable=False, default=0)

    # DataSource from which this Entry originates.
    data_source_id = Column(Integer, ForeignKey('data_sources.id'), index=True)
    data_source = relationship('DataSource',
                               backref=backref('entries', lazy='dynamic'))

    def __repr__(self):
        return "<Entry('{}')>".format(self.id)


class Statistic(Base):
    """
    An object storing statistics about the scraping being performed.
    """
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True, nullable=False)

    # Date up to which this statistic considers.
    date = Column(DateTime, nullable=False)

    document_count = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    entry_count_total = Column(Integer, nullable=False)
    entry_count_tried = Column(Integer, nullable=False)

    # DataSource to which this statistic refers.
    data_source_id = Column(Integer, ForeignKey('data_sources.id'), index=True)
    data_source = relationship('DataSource',
                               backref=backref('statistics', lazy='dynamic'))

    def __repr__(self):
        return "<Statistic('{}', '{}')>".format(
            self.data_source_id,
            self.date.isoformat()
        )


# TODO: Shouldn't be done like this. Should be done in alembic.
# Create the schema if it doesn't already.
Base.metadata.create_all(engine)


# Default database session.
session_factory = sessionmaker(bind=engine)
db = scoped_session(session_factory)
