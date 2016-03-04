import logging

from datetime import date, datetime, timedelta
from elasticsearch.helpers import bulk
from scrapy import Request, Spider
from urllib.parse import urljoin

from nabu.core import settings
from nabu.core.index import es, calculate_doc_id
from nabu.corpus.utils import parse_date


logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


LAST_DAYS_QUERY = {
    "query": {
        "filtered": {
            "query": {"match": {"data_source": "elpais.com"}},
            "filter": {"range": {"date": {
                "lt": "now/d", "gt": "now/d-8d"
            }}}
        }
    },
    "aggs": {
        "counts_per_day": {
            "date_histogram": {
                "field": "date",
                "format": "yyyy-MM-dd",
                "interval": "1d",
                "min_doc_count": 0,
                "extended_bounds": {
                    "max": "now/d-1d",
                    "min": "now/d-7d",
                },
            }
        }
    }
}


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
                'elpais.com',
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


class ElPaisSpainSpider(Spider):

    name = 'elpais.com'
    custom_settings = {'ITEM_PIPELINES': {
        'nabu.corpus.spiders.elpais_spain.ArticlePipeline': 300
    }}

    def start_requests(self):
        base_url = "http://elpais.com/tag/fecha/{}"

        response = es.search(
            index=settings.ES_INDEX,
            doc_type=settings.ES_DOCTYPE,
            body=LAST_DAYS_QUERY,
            search_type='count',
        )

        start_urls = []
        buckets = response['aggregations']['counts_per_day']['buckets']
        for bucket in buckets:
            if bucket['doc_count'] == 0:
                logger.info("missing_date=%s", bucket['key_as_string'])
                missing_date = bucket['key_as_string'].replace('-', '')

                request = Request(
                    base_url.format(missing_date),
                    callback=self.parse_tag_page
                )
                start_urls.append(request)

        # If no documents returned from Elasticsearch, add all the articles,
        # back from 1976/5/4 to bootstrap the spider.
        if not sum([b['doc_count'] for b in buckets]):
            start_urls = []
            logger.info("missing all dates, starting from beginning")
            first_date = date(1976, 5, 4)
            last_date = date.today()

            current_date = first_date
            while current_date < last_date:
                date_str = current_date.isoformat().replace('-', '')
                request = Request(
                    base_url.format(date_str),
                    callback=self.parse_tag_page
                )
                start_urls.append(request)
                current_date = current_date + timedelta(days=1)

        return start_urls

    def parse_tag_page(self, response):
        # Go through the list of news articles.
        for href in response.xpath("//a[@title='Ver noticia']/@href"):
            yield Request(href.extract(), callback=self.parse_article)

        # Go to the next page.
        next_page = response.xpath(
            "//a[@title='Página siguiente']"
            "[not(contains(@class, 'inactivo'))]"
            "/@href"
        ).extract_first()

        full_url = urljoin("http://elpais.com", next_page.extract())
        yield Request(full_url, callback=self.parse_tag_page)

    def parse_article(self, response):
        article_id = response.url.split('/')[-1].split('.')[0]

        title = response.xpath(
            "//h1[contains(@class, 'articulo-titulo') or "
            "contains(@id, 'titulo_noticia')]//text()"
        ).extract_first()

        summary = response.xpath(
            "//div[contains(@class, 'articulo-subtitulos') or "
            "contains(@id, 'subtitulo_noticia')]//text()"
        ).extract()
        summary = "\n".join([s.strip() for s in summary if s.strip()])

        content = response.xpath(
            "//div[contains(@id, 'cuerpo_noticia')]//text()"
        ).extract()
        content = "\n".join([c.strip() for c in content if c.strip()])

        pub_date = response.xpath(
            "//a[@title='Ver todas las noticias de esta fecha']/text()"
        ).extract()
        pub_date = " ".join([c.strip() for c in pub_date if c.strip()])
        pub_date = parse_date(pub_date)

        logger.info(
            "parsed article_id=%s pub_date=%s",
            article_id, pub_date.isoformat().split('T')[0]
        )

        # Prepare the parsed article.
        full_content = "\n".join([title, summary, content])
        word_count = len(full_content.split())
        article = {
            'content': full_content,
            'content_type': 'clean',
            'tags': ['news', 'Spain', 'spanish'],
            'word_count': word_count,

            'data_source': 'elpais.com',
            'entry': {
                'date_scraped': datetime.now(),
                'source_id': article_id,
            },

            'title': title,
            'url': response.url,
            'date': pub_date,
        }

        yield article
