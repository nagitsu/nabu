import gensim
import os

from nltk.tokenize import RegexpTokenizer
from elasticsearch.helpers import scan

from nabu.core import settings
from nabu.core.index import es


def word2vec_params(params):
    existing_keys = set(params.keys())
    needed_keys = {
        'dimension', 'min_count', 'window', 'subsampling', 'algorithm',
        'negative_sampling', 'hierarchical_softmax', 'epochs', 'alpha',
    }
    if existing_keys != needed_keys:
        raise ValueError(
            "Invalid parameters for word2vec: {}".format(existing_keys)
        )

    model_params = {
        'size': params['dimension'],
        'min_count': params['min_count'],
        'window': params['window'],
        'sample': params['subsampling'],
        'sg': 1 if params['algorithm'] == 'skipgram' else 0,
        'hs': params['hierarchical_softmax'],
        'negative': params['negative_sampling'],
        'iter': params['epochs'],
        'alpha': params['alpha'],
    }

    return model_params


def _sentences(query, parameters=None, report=None):
    """
    Generator returning all the documents that match `query`.

    Can receive additional parameters on `parameters` to indicate how to
    process the documents when turning them into sentences.

    Optionally, a `report` callback may be specified, which will be called with
    the completion percentage 1000 times during the training.
    """
    parameters = parameters or {}
    if parameters['word_tokenizer'] == 'alphanum':
        word_tokenizer = RegexpTokenizer(r'\w+')

    if parameters['lowercase_tokens']:
        lower = lambda d: d.lower()
    else:
        lower = lambda d: d

    if parameters['sentence_tokenizer'] == 'periodspace':
        sentence_tokenizer = lambda d: lower(d).split('. ')

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
        sentences = sentence_tokenizer(document['fields']['content'][0])
        for sentence in sentences:
            yield word_tokenizer.tokenize(sentence)
            processed += 1
            # Report how many documents have been processed, if necessary.
            if report and processed % step == 0:
                report(processed / count)


def train(params, query, file_name, report=None):
    sentences_params = {
        'word_tokenizer': params.pop('word_tokenizer'),
        'sentence_tokenizer': params.pop('sentence_tokenizer'),
        'lowercase_tokens': params.pop('lowercase_tokens'),
    }

    report(0.0)  # Update the state before creating the vocabulary.
    vocabulary_sentences = _sentences(query, sentences_params)
    training_sentences = _sentences(query, sentences_params, report)

    model_params = word2vec_params(params)
    model = gensim.models.Word2Vec(workers=12, **model_params)
    model.build_vocab(vocabulary_sentences)
    model.train(training_sentences)

    if file_name:
        model_path = os.path.join(settings.EMBEDDING_PATH, file_name)
        model.save(model_path)

    return model
