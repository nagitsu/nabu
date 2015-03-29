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
from . import _180
from . import republica
from . import lared21
from . import espectador
from . import univision
from . import informador
from . import elmercurio


SOURCES = {
    elobservador.SOURCE_DOMAIN: elobservador,
    lanacion.SOURCE_DOMAIN: lanacion,
    _180.SOURCE_DOMAIN: _180,
    republica.SOURCE_DOMAIN: republica,
    lared21.SOURCE_DOMAIN: lared21,
    espectador.SOURCE_DOMAIN: espectador,
    univision.SOURCE_DOMAIN: univision,
    informador.SOURCE_DOMAIN: informador,
    elmercurio.SOURCE_DOMAIN: elmercurio,
}
