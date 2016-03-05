import unicodedata

from nltk.tokenize import RegexpTokenizer


def read_analogies(path, preprocessor=lambda x: x):
    """
    Generator that yields analogies from the file at `path`.

    May receive a `preprocessor` function to process the test contents.
    """
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = preprocessor(line)
            w1, w2, w3, w4 = line.strip().split()
            yield (w1, w2, w3, w4)


def read_odd_one_outs(path, preprocessor=lambda x: x):
    """
    Generator that yields odd-one-outs from the file at `path`. Expects the
    first word to be the odd-one.

    May receive a `preprocessor` function to process the test contents.
    """
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            odd_one, *rest = preprocessor(line).strip().split()
            yield (odd_one, rest)


def read_similarities(path, preprocessor=lambda x: x):
    """
    Generator that yields similarity pairs from the file at `path`.

    May receive a `preprocessor` function to process the test contents.
    """
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            w1, w2, sim = line.strip().split()

            sim = float(sim)
            w1 = preprocessor(w1)
            w2 = preprocessor(w2)

            yield ((w1, w2), sim)


def remove_accents(word):
    no_acc = unicodedata.normalize('NFKD', word)\
                        .encode('ascii', 'ignore')\
                        .decode('ascii')
    return no_acc


def build_token_preprocessor(params):

    def preprocessor(text):
        if params['lowercase_tokens']:
            text = text.lower()

        if params['remove_accents']:
            text = unicodedata.normalize('NFKD', text)\
                              .encode('ascii', 'ignore')\
                              .decode('ascii')

        return text

    return preprocessor


def build_word_tokenizer(params):

    if params['word_tokenizer'] == 'alphanum':
        tokenizer = RegexpTokenizer(r'\w+')

        def word_tokenizer(sentence):
            return tokenizer.tokenize(sentence)

    return word_tokenizer


def build_sentence_tokenizer(params):

    if params['sentence_tokenizer'] == 'periodspace':

        def sentence_tokenizer(d):
            lines = []
            for line in d.split('\n'):
                lines.extend(line.split('. '))
            return lines

    return sentence_tokenizer
