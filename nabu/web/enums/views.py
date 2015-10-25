from flask import Blueprint, jsonify


bp = Blueprint('enums', __name__, url_prefix='/enums')


@bp.route('/models/')
def model_enums():
    model_parameters = [
        {
            'model': 'word2vec',
            'verbose_name': 'word2vec',
            'parameters': [
                {'name': 'dimension', 'verbose_name': 'Dimension', 'type': 'int', 'description': "size of word vectors", 'default': 300},
                {'name': 'min_count', 'verbose_name': 'Minimum Count', 'type': 'int', 'description': "minimum times a word must appear on the corpus to be in the vocabulary", 'default': 5},
                {'name': 'window', 'verbose_name': 'Window', 'type': 'int', 'description': "window size for the word's context", 'default': 5},
                {'name': 'subsampling', 'verbose_name': 'Subsampling', 'type': 'float', 'description': "subsampling for words", 'default': 0.0},
                {'name': 'algorithm', 'verbose_name': 'Algorithm', 'type': 'str', 'description': "whether to use `cbow` or `skipgram`", 'default': 'skipgram'},
                {'name': 'hsoftmax', 'verbose_name': 'Hierarchical Softmax', 'type': 'bool', 'description': "whether to use hierarchical softmax", 'default': True},
                {'name': 'negative', 'verbose_name': 'Negative Sampling', 'type': 'int', 'description': "number of words to use for negative sampling", 'default': 0},
                {'name': 'epochs', 'verbose_name': 'Epochs', 'type': 'int', 'description': "number of epochs to train with", 'default': 1},
                {'name': 'alpha', 'verbose_name': 'Alpha', 'type': 'float', 'description': "learning rate for sgd", 'default': 0.025},
            ]
        },
        {
            'model': 'glove',
            'verbose_name': 'GloVe',
            'parameters': [
                {'name': 'dimension', 'verbose_name': 'Dimension', 'type': 'int', 'description': "size of word vectors", 'default': 100},
                {'name': 'min_count', 'verbose_name': 'Minimum Count', 'type': 'int', 'description': "minimum times a word must appear on the corpus to be in the vocabulary", 'default': 10},
                {'name': 'max_count', 'verbose_name': 'Maximum Count', 'type': 'int', 'description': "upper bound for the vocabulary size (i.e. keep top N words)", 'default': None},
                {'name': 'x_max', 'verbose_name': 'X Max', 'type': 'float', 'description': "cutoff for weighting function", 'default': 100.0},
                {'name': 'window', 'verbose_name': 'Window', 'type': 'int', 'description': "window size for the word's context", 'default': 15},
                {'name': 'alpha', 'verbose_name': 'Alpha', 'type': 'float', 'description': "exponent for weighting function", 'default': 0.75},
                {'name': 'eta', 'verbose_name': 'Eta', 'type': 'float', 'description': "learning rate for sgd", 'default': 0.05},
                {'name': 'epochs', 'verbose_name': 'Epochs', 'type': 'int', 'description': "number of epochs to train with", 'default': 15},
            ]
        }
    ]

    return jsonify(data=model_parameters)


@bp.route('/corpus/')
def corpus_enums():
    corpus_parameters = [
        {
            'name': 'sentence_tokenizer',
            'verbose_name': 'Sentence Tokenizer',
            'description': "tokenizer to use to create sentences from a document",
            'values': [
                {'name': 'periodspace', 'description': "separate sentences by splitting on `. `"},
            ],
            'default': 'periodspace',
        },
        {
            'name': 'word_tokenizer',
            'verbose_name': 'Word Tokenizer',
            'description': "tokenizer to use to obtain tokens from a sentence",
            'values': [
                {'name': 'alphanum', 'description': "split the sentence into alphanumeric tokens, i.e. matching the regexp `\\w+`"},
            ],
            'default': 'alphanum',
        },
        {
            'name': 'lowercase_tokens',
            'verbose_name': 'Lowercase Tokens',
            'description': "whether to lowercase tokens when building tokens",
            'values': [
                {'name': 'true', 'description': "lowercase tokens"},
                {'name': 'false', 'description': "don't lowercase tokens"},
            ],
            'default': 'true',
        },
        {
            'name': 'remove_accents',
            'verbose_name': 'Remove Accents',
            'description': "whether to remove accents when building tokens",
            'values': [
                {'name': 'true', 'description': "remove accents"},
                {'name': 'false', 'description': "don't remove accents"},
            ],
            'default': 'true',
        },
    ]

    return jsonify(data=corpus_parameters)


@bp.route('/tests/')
def tests_enums():
    tests_parameters = [
        {
            'type': 'analogies',
            'verbose_name': 'Analogies',
        }
    ]

    return jsonify(data=tests_parameters)
