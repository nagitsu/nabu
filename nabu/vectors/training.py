import gensim
import os

from elasticsearch.helpers import scan

from nabu.core import settings
from nabu.core.index import es
from nabu.vectors.utils import (
    build_token_preprocessor, build_word_tokenizer, build_sentence_tokenizer,
)


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


def sentence_generator(query, preprocessing_params, report=None):
    """
    Generator returning all the documents that match `query`.

    Receives additional parameters on `preprocessing_params` indicating how to
    process the documents when turning them into sentences.

    Optionally, a `report` callback may be specified, which will be called with
    the completion percentage 1000 times during the training.
    """
    preprocessor = build_token_preprocessor(preprocessing_params)
    word_tokenizer = build_word_tokenizer(preprocessing_params)
    sentence_tokenizer = build_sentence_tokenizer(preprocessing_params)

    if report:
        # Get the approximate number of results.
        result = es.search(
            index='nabu', search_type='count',
            body={'query': query}
        )
        count = result['hits']['total']
        # If there aren't even 1000 results, report for every document.
        step = int(count / 1000) if count > 1000 else 1

    documents = scan(
        es, index='nabu',
        scroll='30m', fields='content',
        query={'query': query}
    )

    processed = 0
    for document in documents:
        processed += 1

        content = preprocessor(document['fields']['content'][0])
        for sentence in sentence_tokenizer(content):
            yield word_tokenizer(sentence)
            # Report how many documents have been processed, if necessary.

        if report and processed % step == 0:
            report(processed / count)


def train(model, query, preprocessing, parameters, file_name, report=None):
    # Gathering the vocabulary is around 20% of the total work.
    vocabulary_sentences = sentence_generator(
        query, preprocessing,
        lambda p: report(p * 0.2)
    )
    training_sentences = sentence_generator(
        query, preprocessing,
        lambda p: report(0.2 + p * 0.8)
    )

    if model == 'word2vec':
        model_params = word2vec_params(parameters)
        model = gensim.models.Word2Vec(workers=12, **model_params)
        model.build_vocab(vocabulary_sentences)
        model.train(training_sentences)

    if file_name:
        model_path = os.path.join(settings.EMBEDDING_PATH, file_name)
        model.save(model_path)

    return model
