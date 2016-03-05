import logging

from datetime import datetime
from elasticsearch.helpers import bulk
from scrapy import Request, Spider

from nabu.core import settings
from nabu.core.index import es, calculate_doc_id
from nabu.corpus.utils import parse_date


logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ArticlePipeline(object):

    def __init__(self):
        self._dirty_articles = []

    def process_item(self, item, spider):
        # Don't insert into Elasticsearch for every item received.
        self._dirty_articles.append(item)
        if len(self._dirty_articles) > 300:
            self.flush()

    def close_spider(self, spider):
        self.flush()

    def flush(self):
        if not self._dirty_articles:
            return

        actions = []
        for article in self._dirty_articles:
            doc_id = calculate_doc_id(
                'gxzone.com',
                article['entry']['source_id']
            )

            actions.append({
                '_op_type': 'index',
                '_index': settings.ES_INDEX,
                '_type': settings.ES_DOCTYPE,
                '_id': doc_id,
                '_source': article
            })

        bulk(es, actions)
        logger.info('flushed count=%s', len(actions))

        self._dirty_articles = []


class GxZoneSpider(Spider):
    """
    The spider is intended to be run just once, won't check if the data is
    already on Elasticsearch, though it will generate consistent document IDs
    just in case.
    """

    name = 'gxzone.com'
    start_urls = ["http://foros.gxzone.com"]
    custom_settings = {'ITEM_PIPELINES': {
        'nabu.corpus.spiders.gxzone.ArticlePipeline': 300
    }}

    def parse(self, response):
        # From the main page, obtain the last thread ID and add all the
        # previous ones.
        last_thread = response.xpath(
            "//h5[@class='widget_post_header']/a/@href"
        ).extract_first()
        last_thread_id = int(last_thread.split('/')[1].split('-')[0])

        base_url = "http://foros.gxzone.com/threads/{}-alallal?pp=40"
        for thread_id in range(1, last_thread_id + 1):
            thread_url = base_url.format(thread_id)
            request = Request(thread_url, callback=self.parse_thread)
            request.meta['thread_id'] = thread_id
            request.meta['page_id'] = 1
            yield request

    def parse_thread(self, response):
        thread_id = response.meta['thread_id']
        page_id = response.meta['page_id']

        is_error = response.xpath("//div[@class='standard_error']")
        if is_error or len(response.body) < 500:
            logger.info(
                "not_found thread_id=%s page_id=%s",
                thread_id, page_id
            )
            return

        title = response.xpath(
            "//span[@class='threadtitle']//text()"
        ).extract()
        title = " ".join([t.strip() for t in title if t.strip()])

        content = response.xpath("//div[@class='content']//text()").extract()
        content = "\n".join([t.strip() for t in content if t.strip()])

        pub_date = response.xpath(
            "(//span[@class='date'])[1]//text()"
        ).extract()
        pub_date = " ".join([c.strip() for c in pub_date if c.strip()])
        pub_date = parse_date(pub_date)

        logger.info("parsed thread_id=%s page_id=%s", thread_id, page_id)

        # Prepare and yield the parsed article.
        document_id = "{}@@{}".format(thread_id, page_id)
        full_content = "\n".join([title, content])
        word_count = len(full_content.split())
        article = {
            'content': full_content,
            'content_type': 'clean',
            'tags': ['forum', 'Argentina', 'spanish'],
            'word_count': word_count,

            'data_source': 'gxzone.com',
            'entry': {
                'date_scraped': datetime.now(),
                'source_id': document_id,
            },

            'title': title,
            'url': response.url,
            'date': pub_date,
        }

        yield article

        # Go to the next page too.
        next_page = response.xpath("//a[@rel='next']/@href").extract_first()
        if next_page:
            request = Request(
                response.urljoin(next_page),
                callback=self.parse_thread
            )
            request.meta['thread_id'] = thread_id
            request.meta['page_id'] = page_id + 1
            yield request
