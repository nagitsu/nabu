"""
Each module inside this package has three functions:
- `get_missing_ids`: returns the missing source-level IDs that need scraping.
- `get_content`: returns the content given a requests' `Response` object.
  (TODO: Could it return a list too? For forum threads, for example.)
- `get_metadata`: returns the document's metadata given a requests' `Response`
  object. May assume that the response is valid.
"""
from os.path import dirname

import importlib
import pkgutil

SOURCES = {}

# Iterate on all the modules found on the `sources` (this) package, import
# them and store their `SOURCE_DOMAIN` for easier access.
for importer, modname, _ in pkgutil.iter_modules([dirname(__file__)]):
    m = importlib.import_module('.{}'.format(modname), package=__name__)
    SOURCES[m.SOURCE_DOMAIN] = m
