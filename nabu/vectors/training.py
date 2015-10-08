import gensim
import os
import unicodedata

from nltk.tokenize import RegexpTokenizer
from elasticsearch.helpers import scan

from nabu.core import settings
from nabu.core.index import es


def word2vec_params(parameters):
    """
    Turns the parameters as stored on the Embedding model to the Gensim
    equivalents.
    """
    model_params = {
        'size': parameters['dimension'],
        'min_count': parameters['min_count'],
        'window': parameters['window'],
        'sample': parameters['subsampling'],
        'sg': 1 if parameters['algorithm'] == 'skipgram' else 0,
        'hs': parameters['hsoftmax'],
        'negative': parameters['negative'],
        'iter': parameters['epochs'],
        'alpha': parameters['alpha'],
    }

    return model_params


def _sentences(query, preprocessing, report=None):
    """
    Generator returning all the documents that match `query`.

    Receives additional parameters on `preprocessing` indicating how to process
    the documents when turning them into sentences.

    Optionally, a `report` callback may be specified, which will be called with
    the completion percentage 1000 times during the training.
    """
    # TODO: Should be a factory function for the preprocessing, so it may be
    # reused when evaluating.
    if preprocessing['word_tokenizer'] == 'alphanum':
        word_tokenizer = RegexpTokenizer(r'\w+')

    if preprocessing['lowercase_tokens']:
        lower = lambda d: d.lower()
    else:
        lower = lambda d: d

    if preprocessing['remove_accents']:
        accents = lambda d: unicodedata.normalize('NFKD', d)\
                                       .encode('ascii', 'ignore')\
                                       .decode('ascii')
    else:
        accents = lambda d: d

    if preprocessing['sentence_tokenizer'] == 'periodspace':
        sentence_tokenizer = lambda d: accents(lower(d)).split('. ')

    if report:
        # Get the approximate number of results.
        result = es.search(index='nabu', search_type='count', body=query)
        count = result['hits']['total']
        step = int(count / 1000)

    documents = scan(
        es, index='nabu',
        scroll='30m', fields='content',
        query=query
    )

    processed = 0
    for document in documents:
        processed += 1
        sentences = sentence_tokenizer(document['fields']['content'][0])

        for sentence in sentences:
            yield word_tokenizer.tokenize(sentence)
            # Report how many documents have been processed, if necessary.

        if report and processed % step == 0:
            report(processed / count)


def train(query, preprocessing, parameters, file_name, report=None):
    # Gathering the vocabulary is around 20% of the total work.
    vocabulary_sentences = _sentences(
        query, preprocessing,
        lambda p: report(p * 0.2)
    )
    training_sentences = _sentences(
        query, preprocessing,
        lambda p: report(0.2 + p * 0.8)
    )

    # TODO: Separate logic out for different models.
    model_params = word2vec_params(parameters)
    model = gensim.models.Word2Vec(workers=12, **model_params)
    model.build_vocab(vocabulary_sentences)
    model.train(training_sentences)

    if file_name:
        model_path = os.path.join(settings.EMBEDDING_PATH, file_name)
        model.save(model_path)

    return model
