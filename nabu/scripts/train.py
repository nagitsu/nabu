import time
import gensim

from IPython import embed
from nltk.tokenize import RegexpTokenizer
from elasticsearch.helpers import scan

from nabu.corpus.indexing import es


def sentences(query):
    tokenizer = RegexpTokenizer(r'\w+')

    documents = scan(
        es, index="nabu",
        scroll='30m', fields='content',
        query=query
    )

    for document in documents:
        sentences = document['fields']['content'][0].lower().split('. ')
        for sentence in sentences:
            yield tokenizer.tokenize(sentence)


def train_model(min_count=10, size=100):
    query = {
        "size": 100,
        "query": {
            "range": {
                "date": {"lte": "2015-06-27"}
            }
        }
    }

    model = gensim.models.Word2Vec(workers=12, min_count=min_count, size=size)
    model.build_vocab(sentences(query))
    model.train(sentences(query))

    return model


if __name__ == '__main__':
    t0 = time.time()
    model = train_model(min_count=5, size=300)
    t1 = time.time()
    print("{} seconds elapsed".format(t1 - t0))
    model.save('full-300-5.w2v')

    embed(display_banner=False)
