"""
Each module inside this package has three functions:
- `get_missing_ids`: returns the missing source-level IDs that need scraping.
- `get_content`: returns the content given a requests' `Response` object.
  (TODO: Could it return a list too? For forum threads, for example.)
- `get_metadata`: returns the document's metadata given a requests' `Response`
  object. May assume that the response is valid.
"""
from . import elobservador
from . import lanacion


SOURCES = {
    elobservador.SOURCE_DOMAIN: elobservador,
    lanacion.SOURCE_DOMAIN: lanacion,
}
