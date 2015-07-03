import requests

from IPython import embed
from lxml import html

from nabu.corpus import sources, settings

SOURCE_NAME = 'clarin'
SOURCE_ID = '1384061731'

module = getattr(sources, SOURCE_NAME)

missing_ids = module.get_missing_ids([])
url = module.DOCUMENT_URL.format(SOURCE_ID)
response = requests.get(url, headers=settings.REQUEST_HEADERS)
content = module.get_content(response)
metadata = module.get_metadata(response)

root = html.fromstring(response.content)

print(content)
print()
print(metadata)

embed(display_banner=False)
