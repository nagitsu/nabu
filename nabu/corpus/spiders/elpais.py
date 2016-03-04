import logging
import re

from datetime import datetime, timedelta
from elasticsearch.helpers import bulk
from scrapy import Request, Spider

from nabu.core import settings
from nabu.core.index import es, calculate_doc_id


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


LAST_DAYS_QUERY = {
    "query": {
        "filtered": {
            "query": {"match": {"data_source": "elpais.com.uy"}},
            "filter": {"range": {"date": {
                "lt": "now/d", "gt": "now/d-8d"
            }}}
        }
    },
    "aggs": {
        "counts_per_day": {
            "date_histogram": {
                "field": "date",
                "format": "yyyy/M/d",
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
                'elpais.com.uy',
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


class ElPaisSpider(Spider):

    name = 'elpais.com.uy'
    custom_settings = {'ITEM_PIPELINES': {
        'nabu.corpus.spiders.elpais.ArticlePipeline': 300
    }}

    DATE_RE = re.compile(
        r'/ediciones-anteriores/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)'
    )

    def start_requests(self):
        base_url = 'http://www.elpais.com.uy/ediciones-anteriores/{}'

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
                logger.info('missing_date=%s', bucket['key_as_string'])
                missing_date = bucket['key_as_string']
                start_urls.append(Request(base_url.format(missing_date)))

        if not buckets:
            # If no buckets returned from Elasticsearch, add yesterday's date
            # to bootstrap the spider.
            now = datetime.now() - timedelta(days=1)
            strnow = '{}/{}/{}'.format(now.year, now.month, now.day)
            start_urls.append(Request(base_url.format(strnow)))

        return start_urls

    def parse(self, response):
        m = self.DATE_RE.search(response.url)
        pub_date = datetime(
            int(m.group('year')),
            int(m.group('month')),
            int(m.group('day')),
        )

        for href in response.css('li.article > h1 > a::attr(href)'):
            article_id = href.extract()
            logger.debug(
                "found article_id=%s pub_date=%s",
                article_id, pub_date.isoformat().split('T')[0]
            )

            full_url = response.urljoin(href.extract())
            request = Request(full_url, callback=self.parse_article)
            request.meta['article_id'] = article_id
            request.meta['pub_date'] = pub_date
            request.meta['url'] = full_url

            yield request

        for href in response.css('div.pagination a::attr(href)'):
            new_page = response.urljoin(href.extract())
            yield Request(new_page, callback=self.parse)

    def parse_article(self, response):
        article_id = response.meta['article_id']
        pub_date = response.meta['pub_date']
        url = response.meta['url']

        title, full_content = self.parse_standard(response)

        logger.info(
            "parsed article_id=%s pub_date=%s",
            article_id, pub_date.isoformat().split('T')[0]
        )

        word_count = len(full_content.split())
        article = {
            'content': full_content,
            'content_type': 'clean',
            'tags': ['news', 'Uruguay', 'spanish'],
            'word_count': word_count,

            'data_source': 'elpais.com.uy',
            'entry': {
                'date_scraped': datetime.now(),
                'source_id': article_id,
            },

            'title': title,
            'url': url,
            'date': pub_date,
        }

        yield article

    def parse_standard(self, response):
        title = u"\n".join(response.css('div.title > h1::text').extract())
        summary = u"\n".join(response.css('div.pc > p::text').extract())
        content = u"\n".join(response.css(
            'div.article-content > p::text'
        ).extract())

        # Small snippet of context sometimes located at the bottom of the
        # articles.
        nutgraph_title = u"\n".join(response.css(
            'div.nutgraph > div::text'
        ).extract())
        nutgraph = u"\n".join(response.css(
            'div.nutgraph > p::text'
        ).extract())

        full_content = u"\n".join([
            title, summary, content, nutgraph_title, nutgraph
        ])

        return title, full_content
