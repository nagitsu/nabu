from datetime import datetime

from sqlalchemy import (
    create_engine, Column, DateTime, ForeignKey, Integer, String, Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

from . import settings


engine = create_engine(settings.DATABASE_ENGINE)

Base = declarative_base()


class DataSource(Base):
    """
    A source of documents.
    """
    __tablename__ = 'data_sources'

    id = Column(Integer, primary_key=True, nullable=False)
    domain = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return "<DataSource('{}')>".format(self.domain)


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
    # E.g. `['news', 'uruguay']`.
    tags = Column(Text, nullable=False, default="[]")

    # Document derived from this Entry, if any.
    entry_id = Column(Integer, ForeignKey('entries.id'), nullable=False)
    entry = relationship('Entry', backref=backref('documents', lazy='dynamic'))

    def __repr__(self):
        return "<Document('{}')>".format(self.id)


class Entry(Base):
    """
    An entry for an online document to be scraped.
    """
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True, nullable=False)
    # May be `success`, `timeout`, `notfound`, `pending`, `unparseable`.
    outcome = Column(String, nullable=False, default='pending')
    # DataSource-level ID (e.g. Observador's article ID).
    # TODO: Add a unique constraint between this and data_source_id.
    source_id = Column(String, nullable=False)

    added = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_tried = Column(DateTime, nullable=True)
    number_of_tries = Column(Integer, nullable=False, default=0)

    # DataSource from which this Entry originates.
    data_source_id = Column(Integer, ForeignKey('data_sources.id'))
    data_source = relationship('DataSource',
                               backref=backref('entries', lazy='dynamic'))

    def __repr__(self):
        return "<Entry('{}')>".format(self.id)


# TODO: Shouldn't be done like this. Should be done in alembic.
# Create the schema if it doesn't already.
Base.metadata.create_all(engine)


# Default database session.
Session = sessionmaker(bind=engine)
db = Session()
