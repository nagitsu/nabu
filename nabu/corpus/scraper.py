import asyncio
import concurrent
import logging

from datetime import datetime

from nabu.core import settings
from nabu.core.index import es, prepare_document
from nabu.core.models import db, DataSource, Entry

from nabu.corpus import sources
from nabu.corpus.utils import get


logger = logging.getLogger(__name__)


@asyncio.coroutine
def fill_entries(data_source):
    """
    Creates the missing entries for a Data Source. Assumes the DataSource
    exists.

    If the missing ids may not be retrieved, return False. Otherwise, return
    True.
    """
    module = sources.SOURCES[data_source.domain]

    # TODO: Offload database queries to an executor.
    existing_ids = db.query(Entry.source_id)\
                     .filter(Entry.data_source == data_source)\
                     .yield_per(10000)
    existing_ids = list(map(lambda r: r[0], existing_ids))

    logger.info("%s existing ids found for '%s'",
                len(existing_ids), data_source.domain)

    try:
        # Use an executor, so we can keep the modules asyncio-agnostic.
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            None, module.get_missing_ids, existing_ids
        )
        missing_ids = yield from future
        missing_ids = list(missing_ids)
    except:
        return False

    logger.info("%s entries for %s need to be created",
                len(missing_ids), data_source.domain)

    # Go around the SQLAlchemy ORM so we avoid loading over 1 million entries
    # on memory when first adding data sources. Also, add them in batches of
    # 100k.
    now = datetime.now()
    step = 100000
    for start in range(0, len(missing_ids), step):
        logger.info("adding batch #%s for %s",
                    int(start / step + 1), data_source.domain)

        end = start + step
        new_entries = []
        for missing_id in missing_ids[start:end]:
            new_entries.append({
                'outcome': 'pending',
                'source_id': missing_id,
                'added': now,
                'number_of_tries': 0,
                'data_source_id': data_source.id
            })
        db.execute(Entry.__table__.insert(), new_entries)
        db.commit()

    return True


@asyncio.coroutine
def scrape_entries(data_source_id):
    """
    Coroutine tasked with orchestrating scraping for a certain source.

    Will first check for new entries to be created; then will get the list of
    all pending ones, scrape them and start over. If the process is finished
    too fast, will sleep for a while.
    """
    loop = asyncio.get_event_loop()
    data_source = db.query(DataSource).get(data_source_id)

    while True:
        loop_start = loop.time()

        # Create the new entries.
        logger.info("populating entries for '%s'", data_source.domain)
        success = yield from fill_entries(data_source)

        if not success:
            logger.info("error populating '%s'", data_source.domain)
            yield from asyncio.sleep(settings.LOOP_COOLDOWN)
            continue

        logger.info("all entries created for '%s'", data_source.domain)

        # See which entries need to be scraped, checking their status and
        # retries.
        statuses = ['failure', 'pending']
        entries_left = db.query(Entry.id).filter(
            Entry.outcome.in_(statuses),
            Entry.number_of_tries < settings.MAX_RETRIES,
            Entry.data_source == data_source
        ).yield_per(50000)

        entries_left = list(map(lambda e: e[0], entries_left))
        logger.info(
            "%s entries to scrape found for '%s'",
            len(entries_left), data_source.domain
        )

        # Perform the scraping.
        current_tasks = set()
        while entries_left and len(current_tasks) < data_source.concurrency:
            entry_id = entries_left.pop()
            task = loop.create_task(scrape_entry(entry_id))
            current_tasks.add(task)

            # If the concurrency limit for the data source is reached, wait
            # until at least one of them finishes.
            if len(current_tasks) >= data_source.concurrency:
                done, pending = yield from asyncio.wait(
                    current_tasks,
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                current_tasks = pending
            else:
                # No need to wait for entries; wait for a cooldown anyways.
                yield from asyncio.sleep(settings.REQUEST_COOLDOWN)

        loop_end = loop.time()
        # If the loop took less than the default cooldown time, sleep the rest
        # of the time to avoid busy-waiting.
        if loop_end - loop_start < settings.LOOP_COOLDOWN:
            wait_time = int(settings.LOOP_COOLDOWN - (loop_end - loop_start))
            logger.info(
                "finished the loop too fast for '%s', sleeping %ss",
                data_source.domain, wait_time
            )
            yield from asyncio.sleep(wait_time)


@asyncio.coroutine
def scrape_entry(entry_id):
    """
    Scrapes the Entry identified by `entry_id` and updates its info, also
    storing the document in Elasticsearch if successful.
    """
    entry = db.query(Entry).get(entry_id)
    module = sources.SOURCES[entry.data_source.domain]

    # Fetch the entry's content.
    # `source_id` may be composite, separating parts with `@@`.
    source_id = entry.source_id.split('@@')
    url = module.DOCUMENT_URL.format(*source_id)

    headers = settings.REQUEST_HEADERS
    source_headers = getattr(module, 'HEADERS', None)
    if source_headers:
        headers = headers.copy()
        headers.update(source_headers)

    try:
        response = yield from get(url, headers=headers)
    except Exception as e:
        # Capture all exceptions, as the `requests` library may raise
        # arbitrary exceptions; not all of them are wrapped.
        logger.info("entry_id = %s failed when requesting url; %s",
                    entry_id, repr(e))
        entry.outcome = 'failure'
        entry.last_tried = datetime.now()
        entry.number_of_tries += 1
        db.merge(entry)
        db.commit()
        return

    # TODO: Improve error handling; code may fail silently.
    try:
        content = module.get_content(response)
    except Exception as e:
        logger.info("entry_id = %s failed when getting content; %s",
                    entry_id, repr(e))
        entry.outcome = 'failure'
        entry.last_tried = datetime.now()
        entry.number_of_tries += 1
        db.merge(entry)
        db.commit()
        return

    if content['outcome'] == 'success':
        min_words = settings.MIN_WORDS_PER_DOCUMENT
        if not content['content'] or len(content['content']) < min_words:
            # Parsing was marked as successful, but no (or too little) content
            # returned; mark as unparseable instead.
            content['outcome'] = 'unparseable'

    outcome = content['outcome']
    entry.outcome = outcome
    entry.last_tried = datetime.now()
    entry.number_of_tries += 1
    db.merge(entry)

    if outcome not in ['multiple', 'success', 'more_entries']:
        # Finished already.
        logger.info("entry_id = %s finished with outcome = %s",
                    entry_id, outcome)
        db.commit()
        return

    # The `multiple` case returns a dict like this:
    # {'outcome': 'multiple', 'new_entries': [...], 'documents': [...]}
    if outcome in ['more_entries', 'multiple']:
        # Create new entries, only if not needed.
        new_ids = content['new_entries']
        if new_ids:
            existing = db.query(Entry.source_id)\
                        .filter(Entry.source_id.in_(new_ids))
            existing = set(map(lambda r: r[0], existing))
            missing = set(new_ids) - existing

            if missing:
                now = datetime.now()
                new_entries = []
                for new_id in missing:
                    new_entries.append({
                        'outcome': 'pending',
                        'source_id': new_id,
                        'added': now,
                        'number_of_tries': 0,
                        'data_source_id': entry.data_source.id,
                    })
                db.execute(Entry.__table__.insert(), new_entries)
        elif outcome == 'more_entries':
            logger.warning(
                "entry_id = %s (outcome = %s) returned no additional entries",
                entry_id, outcome
            )

    # If successful, fetch the metadata of the entry and store in
    # Elasticsearch.
    if outcome in ['multiple', 'success']:
        # `get_metadata` must return the same number of documents as
        # `get_content`.
        metadata = module.get_metadata(response)
        metadata['url'] = response.url

        if outcome == 'success':
            results = [content]
            metadatas = [metadata]
        else:
            results = content['documents']
            metadatas = metadata

        new_docs = []
        for content, metadata in zip(results, metadatas):
            min_words = settings.MIN_WORDS_PER_DOCUMENT
            if not content['content'] or len(content['content']) < min_words:
                continue

            doc = prepare_document(content, metadata, entry)
            new_docs.append(doc)

    logger.info("entry_id = %s finished with outcome = %s", entry_id, outcome)
    db.commit()

    # Finally, store document on Elasticsearch too.
    for doc in new_docs:
        es.index(index='nabu', doc_type='document', body=doc)


def scrape():
    logger.info("starting session")

    # Create the missing DataSources.
    existing_domains = [ds[0] for ds in db.query(DataSource.domain).all()]
    for domain in sources.SOURCES.keys():
        if domain not in existing_domains:
            logger.info("creating new data source, domain = %s", domain)
            new_ds = DataSource(domain=domain)
            db.merge(new_ds)
    db.commit()

    active_ds = db.query(DataSource.id).filter(DataSource.active == True).all()
    data_sources = [ds[0] for ds in active_ds]

    loop = asyncio.get_event_loop()

    # Change the default executor so there are enough workers to handle the
    # request concurrency.
    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=settings.REQUEST_CONCURRENCY + 5
    )
    loop.set_default_executor(executor)
    loop.request_semaphore = asyncio.Semaphore(settings.REQUEST_CONCURRENCY)

    for data_source_id in data_sources:
        loop.create_task(scrape_entries(data_source_id))

    loop.run_forever()
    loop.close()
