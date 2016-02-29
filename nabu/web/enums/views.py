from flask import Blueprint, jsonify


bp = Blueprint('enums', __name__, url_prefix='/enums')


@bp.route('/models/')
def model_enums():
    model_parameters = [
        {
            'model': 'word2vec',
            'verbose_name': 'word2vec',
            'parameters': [
                {'name': 'dimension', 'verbose_name': 'Dimension', 'type': 'int', 'description': "Size of word vectors", 'default': 300},
                {'name': 'min_count', 'verbose_name': 'Minimum Count', 'type': 'int', 'description': "Minimum times a word must appear on the corpus to be in the vocabulary", 'default': 5},
                {'name': 'window', 'verbose_name': 'Window', 'type': 'int', 'description': "Window size for the word's context", 'default': 5},
                {'name': 'subsampling', 'verbose_name': 'Subsampling', 'type': 'float', 'description': "Subsampling for words", 'default': 0.0},
                {
                    'name': 'algorithm',
                    'verbose_name': 'Algorithm',
                    'type': 'options',
                    'values': [
                        {'name': 'skipgram', 'verbose_name': 'Skipgram'},
                        {'name': 'cbow', 'verbose_name': 'CBOW'}
                    ],
                    'description': "Whether to use `cbow` or `skipgram`", 'default': 'skipgram'
                },
                {'name': 'hsoftmax', 'verbose_name': 'Hierarchical Softmax', 'type': 'bool', 'description': "Whether to use hierarchical softmax", 'default': True},
                {'name': 'negative', 'verbose_name': 'Negative Sampling', 'type': 'int', 'description': "Number of words to use for negative sampling", 'default': 0},
                {'name': 'epochs', 'verbose_name': 'Epochs', 'type': 'int', 'description': "Number of epochs to train with", 'default': 1},
                {'name': 'alpha', 'verbose_name': 'Alpha', 'type': 'float', 'description': "Learning rate for sgd", 'default': 0.025},
            ]
        },
        {
            'model': 'glove',
            'verbose_name': 'GloVe',
            'parameters': [
                {'name': 'dimension', 'verbose_name': 'Dimension', 'type': 'int', 'description': "Size of word vectors", 'default': 100},
                {'name': 'min_count', 'verbose_name': 'Minimum Count', 'type': 'int', 'description': "Minimum times a word must appear on the corpus to be in the vocabulary", 'default': 10},
                {'name': 'max_count', 'verbose_name': 'Maximum Count', 'type': 'int', 'description': "Upper bound for the vocabulary size (i.e. keep top N words)", 'default': None},
                {'name': 'x_max', 'verbose_name': 'X Max', 'type': 'float', 'description': "Cutoff for weighting function", 'default': 100.0},
                {'name': 'window', 'verbose_name': 'Window', 'type': 'int', 'description': "Window size for the word's context", 'default': 15},
                {'name': 'alpha', 'verbose_name': 'Alpha', 'type': 'float', 'description': "Exponent for weighting function", 'default': 0.75},
                {'name': 'eta', 'verbose_name': 'Eta', 'type': 'float', 'description': "Learning rate for sgd", 'default': 0.05},
                {'name': 'epochs', 'verbose_name': 'Epochs', 'type': 'int', 'description': "Number of epochs to train with", 'default': 15},
            ]
        },
        {
            'model': 'svd',
            'verbose_name': 'PPMI/SVD',
            'parameters': [
                {'name': 'dimension', 'verbose_name': 'Dimension', 'type': 'int', 'description': "Size of word vectors", 'default': 300},
                {'name': 'min_count', 'verbose_name': 'Minimum Count', 'type': 'int', 'description': "Minimum times a word must appear on the corpus to be in the vocabulary", 'default': 10},
                {'name': 'max_count', 'verbose_name': 'Maximum Count', 'type': 'int', 'description': "Upper bound for the vocabulary size (i.e. keep top N words)", 'default': None},
                {'name': 'window', 'verbose_name': 'Window', 'type': 'int', 'description': "Window size for the word's context", 'default': 5},
                {'name': 'subsampling', 'verbose_name': 'Subsampling', 'type': 'float', 'description': "Subsampling for words", 'default': 1e-5},
                {'name': 'cds', 'verbose_name': 'Context Distribution Smoothing', 'type': 'float', 'description': "Apply smoothing to counts for PPMI", 'default': 0.75},
                {'name': 'sum_context', 'verbose_name': 'Sum Context', 'type': 'bool', 'description': "Sum context vectors to main vectors", 'default': True},
            ]
        },
    ]

    return jsonify(data=model_parameters)


@bp.route('/corpus/')
def corpus_enums():
    corpus_parameters = [
        {
            'name': 'sentence_tokenizer',
            'verbose_name': 'Sentence Tokenizer',
            'description': "Tokenizer to use to create sentences from a document",
            'type': 'options',
            'values': [
                {'name': 'periodspace', 'description': "Separate sentences by splitting on `. `"},
            ],
            'default': 'periodspace',
        },
        {
            'name': 'word_tokenizer',
            'verbose_name': 'Word Tokenizer',
            'description': "Tokenizer to use to obtain tokens from a sentence",
            'type': 'options',
            'values': [
                {'name': 'alphanum', 'description': "Split the sentence into alphanumeric tokens, i.e. matching the regexp `\\w+`"},
            ],
            'default': 'alphanum',
        },
        {
            'name': 'lowercase_tokens',
            'verbose_name': 'Lowercase Tokens',
            'description': "Whether to lowercase tokens when building tokens",
            'type': 'bool',
            'default': True,
        },
        {
            'name': 'remove_accents',
            'verbose_name': 'Remove Accents',
            'description': "Whether to remove accents when building tokens",
            'type': 'bool',
            'default': True,
        },
    ]

    return jsonify(data=corpus_parameters)


@bp.route('/tests/')
def tests_enums():
    tests_parameters = [
        {'type': 'analogies', 'verbose_name': 'Analogies'},
        {'type': 'odd-one-out', 'verbose_name': 'Odd One Out'},
        {'type': 'similarity', 'verbose_name': 'Word Similarity'},
    ]

    return jsonify(data=tests_parameters)
