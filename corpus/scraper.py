import json
import logging
import multiprocessing.dummy as mp
import requests
import time

from datetime import datetime

from sqlalchemy.sql.expression import func

from . import settings, sources
from .models import db, DataSource, Document, Entry
from .utils import custom_encoder


logger = logging.getLogger(__name__)


def fill_entries(data_source_id):
    """
    Creates the missing entries for a Data Source.

    Assumes the DataSource exists.
    """
    data_source = db.query(DataSource).get(data_source_id)
    module = sources.SOURCES[data_source.domain]

    existing_ids = db.query(Entry.source_id)\
                     .join(DataSource)\
                     .filter(DataSource.id == data_source.id)
    existing_ids = map(lambda r: r[0], existing_ids)
    logger.info("%s existing ids found for %s",
                len(existing_ids), data_source.domain)

    missing_ids = module.get_missing_ids(existing_ids)
    logger.info("%s entries for %s need to be created",
                len(missing_ids), data_source.domain)
    for missing_id in missing_ids:
        entry = Entry(
            source_id=missing_id,
            data_source_id=data_source.id
        )
        db.merge(entry)

    db.commit()


def scrape_entry(entry_id):
    """
    Scrapes the Entry identified by `entry_id` and updates its info, also
    creating a Document if successful.
    """
    entry = db.query(Entry).get(entry_id)
    module = sources.SOURCES[entry.data_source.domain]

    # Fetch the entry's content.
    url = module.DOCUMENT_URL.format(entry.source_id)
    # TODO: Better error handling.
    try:
        response = requests.get(url, timeout=settings.REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        # Clean up.
        logger.info("entry_id = %s failed when requesting url; %s",
                    entry_id, repr(e))
        entry.outcome = 'failure'
        entry.last_tried = datetime.now()
        entry.number_of_tries += 1
        db.merge(entry)
        db.commit()
        return

    content = module.get_content(response)

    if content['outcome'] == 'success' and not content['content']:
        # Parsing was marked as successful, but no content returned; mark as
        # unparseable instead.
        content['outcome'] = 'unparseable'

    entry.outcome = content['outcome']
    entry.last_tried = datetime.now()
    entry.number_of_tries += 1
    db.merge(entry)

    # If successful, fetch the metadata of the entry and create the Document
    # instance.
    if content['outcome'] == 'success':
        metadata = module.get_metadata(response)
        doc = Document(
            content=content['content'],
            # If a `content_type` was provided, use it; else assume `clean`.
            content_type=content.get('content_type', 'clean'),
            metadata_=json.dumps(metadata, default=custom_encoder),
            # TODO: Should it be `get_contents` the one to return the tags?
            # TODO: Shouldn't tags be per DataSource instead?
            tags=json.dumps(content.get('tags', [])),
            entry=entry
        )
        db.merge(doc)

    logger.info("entry_id = %s finished with outcome = %s",
                entry_id, content['outcome'])

    db.commit()

    time.sleep(settings.THREAD_COOLDOWN)


def main_loop():
    logger.info("starting session")
    pool = mp.Pool(settings.POOL_SIZE)

    while True:
        loop_start = time.time()

        # Populate the entries.
        logger.debug("populating entries for all data sources...")
        data_sources = [ds[0] for ds in db.query(DataSource.id).all()]
        pool.map(fill_entries, data_sources)
        logger.debug("all necessary entries created")

        # See which entries need to be scraped, checking their status and
        # retries. Scrape them randomly so the load is distributed evenly
        # between all the data sources. Also, scrape 200k entries per loop
        # to avoid loading every entry into memory.
        statuses = ['failure', 'pending']
        entries_to_scrape = db.query(Entry.id).filter(
            Entry.outcome.in_(statuses) &
            (Entry.number_of_tries < settings.MAX_RETRIES)
        ).order_by(func.random()).limit(200000).all()

        entries_to_scrape = map(lambda e: e[0], entries_to_scrape)
        logger.info("%s entries to scrape found", len(entries_to_scrape))

        # Scrape all the entries.
        pool.map(scrape_entry, entries_to_scrape)

        loop_end = time.time()
        # If the loop took less than the default cooldown time, sleep the rest
        # of the time to avoid busy-waiting.
        if loop_end - loop_start < settings.LOOP_COOLDOWN:
            wait_time = int(settings.LOOP_COOLDOWN - (loop_end - loop_start))
            logger.info("finished the loop too fast, sleeping %ss", wait_time)
            time.sleep(wait_time)
