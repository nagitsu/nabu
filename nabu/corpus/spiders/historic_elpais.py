import logging
import re

from datetime import datetime
from elasticsearch.helpers import bulk
from scrapy import Request, Spider

from nabu.core import settings
from nabu.core.index import es, calculate_doc_id


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


class HistoricElPaisSpider(Spider):

    name = 'historic.elpais.com.uy'
    start_urls = ['http://www.elpais.com.uy/ediciones-anteriores/']
    custom_settings = {'ITEM_PIPELINES': {
        'nabu.corpus.spiders.historic_elpais.ArticlePipeline': 300
    }}

    OLD_DATE_RE = re.compile(r'/(?P<year>\d{2})/(?P<month>\d{2})/(?P<day>\d{2})/')  # noqa
    NEW_DATE_RE = re.compile(r'/ediciones-anteriores/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)')  # noqa
    ARTICLE_ID_RE = re.compile(r'.*((p[A-Za-z]+|ultmo))[-_](?P<article_id>\d+)((\.asp)|/)')  # noqa
    PRINT_VERSION_URL = "http://historico.elpais.com.uy/Paginas/ImprimirNota2.asp?i={}"  # noqa

    def parse(self, response):
        for href in response.css('.days a::attr(href)'):
            full_url = response.urljoin(href.extract())
            if full_url.endswith('index.asp'):
                base_url = full_url[:-len('index.asp')]
                yield Request(
                    base_url + 'todoslostitulos.asp',
                    callback=self.parse_old_index
                )
                yield Request(
                    base_url + 'indexultimomomento.asp',
                    callback=self.parse_old_index
                )
            else:
                yield Request(
                    full_url,
                    callback=self.parse_new_index
                )

        for href in response.css('.month a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield Request(full_url, callback=self.parse)

    def parse_old_index(self, response):
        m = self.OLD_DATE_RE.search(response.url)
        pub_date = datetime(
            int('20' + m.group('year')),
            int(m.group('month')),
            int(m.group('day')),
        )

        for href in response.css('a::attr(href)'):
            m = self.ARTICLE_ID_RE.match(href.extract())
            if m and m.group('article_id'):
                article_id = m.group('article_id')
                logger.debug(
                    "found article_id=%s pub_date=%s",
                    article_id, pub_date.isoformat().split('T')[0]
                )

                real_url = response.urljoin(href.extract())
                full_url = self.PRINT_VERSION_URL.format(article_id)
                request = Request(full_url, callback=self.parse_article)
                request.meta['article_id'] = article_id
                request.meta['pub_date'] = pub_date
                request.meta['url'] = real_url

                yield request

    def parse_new_index(self, response):
        m = self.NEW_DATE_RE.search(response.url)
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
            yield Request(new_page, callback=self.parse_new_index)

    def parse_article(self, response):
        article_id = response.meta['article_id']
        pub_date = response.meta['pub_date']
        url = response.meta['url']

        if 'ImprimirNota' in response.url:
            title, full_content = self.parse_printed(response)
        else:
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

    def parse_printed(self, response):
        title = u"\n".join(response.css('span.not_titulo::text').extract())
        summary = u"\n".join(response.css('span.not_acapite::text').extract())
        content = u"\n".join(response.css(
            '.not_texto > p > font::text'
        ).extract())
        full_content = u"\n".join([title, summary, content])

        return title, full_content

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
