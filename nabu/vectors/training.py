import gensim
import json
import os

from elasticsearch.helpers import scan
from hashlib import sha512

from nabu.core import settings
from nabu.core.index import es
from nabu.vectors.utils import (
    build_token_preprocessor, build_word_tokenizer, build_sentence_tokenizer,
)
from nabu.vectors.glove import GloveFactory
from nabu.vectors.svd import SVDFactory


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
        'alpha': parameters['alpha'],
    }

    return model_params


def glove_params(parameters):
    """
    Turns the parameters as stored on the Embedding model to the GloveFactory
    equivalents.
    """
    model_params = {
        'vector_size': parameters['dimension'],
        'min_count': parameters['min_count'],
        'max_count': parameters['max_count'],
        'window_size': parameters['window'],
        'alpha': parameters['alpha'],
        'eta': parameters['eta'],
        'x_max': parameters['x_max'],
        'epochs': parameters['epochs'],
    }

    return model_params


def svd_params(parameters):
    """
    Turns the parameters as stored on the Embedding model to the SVDFactory
    equivalents.
    """
    model_params = {
        'dim': parameters['dimension'],
        'min_count': parameters['min_count'],
        'max_count': parameters['max_count'],
        'window': parameters['window'],
        'subsample': parameters['subsampling'],
        'cds': parameters['cds'],
        'sum_context': parameters['sum_context'],
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
    model_path = os.path.join(settings.EMBEDDING_PATH, file_name)

    if model == 'word2vec':
        model_params = word2vec_params(parameters)
        model = gensim.models.Word2Vec(
            workers=settings.TRAINING_WORKERS,
            **model_params
        )

        # Gathering the vocabulary is around 20% of the total work.
        vocabulary_sentences = sentence_generator(
            query, preprocessing,
            lambda p: report(p * 0.2)
        )
        model.build_vocab(vocabulary_sentences)

        # Multiple epochs is not correctly supported by gensim, must be done
        # manually.
        base_alpha = model.alpha
        min_alpha = model.min_alpha
        total_epochs = parameters['epochs']

        for epoch in range(1, total_epochs + 1):
            lower_ratio = (epoch - 1) / total_epochs
            upper_ratio = epoch / total_epochs

            model.alpha = base_alpha - (base_alpha - min_alpha) * lower_ratio
            model.min_alpha = base_alpha - (base_alpha - min_alpha) * upper_ratio

            training_sentences = sentence_generator(
                query, preprocessing,
                lambda p: report(0.2 + 0.8 * (lower_ratio + p / total_epochs))
            )
            model.train(training_sentences)

        model.save(model_path)

    elif model == 'glove':
        model_params = glove_params(parameters)

        # Obtain the query's hash, so we don't create repeated cooccurrence
        # matrices the same query and parameter combinations.
        content = json.dumps(query) + " " + \
            str(parameters['min_count']) + " " + \
            str(parameters['max_count']) + " " + \
            str(parameters['window'])
        query_hash = sha512(content.encode('utf-8')).hexdigest()[:20]
        base_path = '{}{}'.format(settings.EMBEDDING_PATH, query_hash)
        env = {
            'vocab_path': '{}.vocab.txt'.format(base_path),
            'cooccur_path': '{}.cooccur.bin'.format(base_path),
            'shuf_cooccur_path': '{}.cooccur.shuf.bin'.format(base_path),
        }

        factory = GloveFactory(
            env=env,
            threads=settings.TRAINING_WORKERS,
            memory=settings.TRAINING_MEMORY,
            **model_params
        )

        # Check if the shuffled cooccurrence matrix and vocabulary files exists
        # for this query. If they do, don't create them again.
        if not (os.path.exists(env['vocab_path']) and
                os.path.exists(env['shuf_cooccur_path'])):

            vocabulary_sentences = sentence_generator(
                query, preprocessing,
                lambda p: report(p * 0.05)
            )
            factory.build_vocabulary(vocabulary_sentences)

            matrix_sentences = sentence_generator(
                query, preprocessing,
                lambda p: report(0.05 + 0.2 * p)
            )
            factory.build_cooccurrence_matrix(matrix_sentences)

            # Delete the non-shuffled cooccurrence matrix.
            os.remove(env['cooccur_path'])

        report(0.35)
        model = factory.train(model_path)

    elif model == 'svd':
        model_params = svd_params(parameters)
        factory = SVDFactory(**model_params)

        vocabulary_sentences = sentence_generator(
            query, preprocessing,
            lambda p: report(p * 0.1)
        )
        factory.build_vocab(vocabulary_sentences)

        matrix_sentences = sentence_generator(
            query, preprocessing,
            lambda p: report(0.1 + 0.7 * p)
        )
        factory.build_svd(matrix_sentences)

        model = factory.train()
        factory.save(model_path)

    return model
