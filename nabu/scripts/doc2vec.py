import logging
import nltk
import unicodedata

from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.getLogger('gensim').setLevel(logging.INFO)

es = Elasticsearch(http_auth=('nabu', 'nabunabu'))
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')


def create_model(epochs=1):
    model = Doc2Vec(
        size=300,
        window=7,
        min_count=3,
        workers=12,
        negative=7
    )
    model.build_vocab(sentence_generator())

    alpha, min_alpha, passes = (0.025, 0.001, epochs)
    alpha_delta = (alpha - min_alpha) / passes
    for epoch in range(0, passes):
        model.alpha, model.min_alpha = alpha, alpha
        model.train(sentence_generator())
        alpha -= alpha_delta

    model.save('doc2vec_model_300_neg5')


def sentence_generator():
    documents = scan(
        es, index='nabu',
        scroll='30m', fields='content',
    )

    for document in documents:
        sentences = sentence_tokenizer(document['fields']['content'][0])

        for idx, sentence in enumerate(sentences):
            sentence_id = "{}_{}".format(document['_id'], idx)
            yield TaggedDocument(words=sentence, tags=[sentence_id])


def sentence_tokenizer(document):
    sentences = nltk.sent_tokenize(document.strip())
    for sentence in sentences:
        yield tokenize(sentence)


def tokenize(sentence):
    token_list = []
    for token in tokenizer.tokenize(sentence):
        nkfd_form = unicodedata.normalize('NFKD', token)
        only_ascii = nkfd_form.encode('ascii', 'ignore').decode('ascii')
        token_list.append(only_ascii.strip().lower())

    return token_list


if __name__ == '__main__':
    create_model()
