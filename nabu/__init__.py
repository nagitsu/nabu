from logging.config import dictConfig

from nabu.core import settings
from nabu.corpus.scraper import scrape  # noqa
from nabu.web.app import app as webapp  # noqa


# Set up logging.
dictConfig(settings.LOGGING_CONFIG)
