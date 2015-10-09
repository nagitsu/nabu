import unicodedata

from nltk.tokenize import RegexpTokenizer


def read_analogies(path, preprocessor=lambda x: x):
    """
    Generator that yields analogies from the file at `path`.

    May receive a `preprocessor` function to process the test contents.
    """
    with open(path, 'r') as f:
        for line in f.readlines():
            line = preprocessor(line)
            w1, w2, w3, w4 = line.strip().split()
            yield (w1, w2, w3, w4)


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
            return d.split('. ')

    return sentence_tokenizer
