import requests
import sys

from IPython import embed
from lxml import html

from nabu.core import settings
from nabu.corpus import sources

SOURCE_NAME = sys.argv[1]
SOURCE_ID = sys.argv[2]

module = getattr(sources, SOURCE_NAME)

missing_ids = list(module.get_missing_ids([]))
url = module.DOCUMENT_URL.format(SOURCE_ID)
response = requests.get(url, headers=settings.REQUEST_HEADERS)
content = module.get_content(response)
metadata = module.get_metadata(response)

root = html.fromstring(response.content)

print(content)
print()
print(metadata)

embed(display_banner=False)
