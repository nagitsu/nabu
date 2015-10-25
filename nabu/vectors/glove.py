import numpy as np

from itertools import islice
from os.path import join
from subprocess import Popen, PIPE

from nabu.core import settings


class Glove:
    """
    An instance of `Glove` represents a particular Glove model already trained.
    """

    def __init__(self, vocab, vectors):
        self.vocab = vocab
        self.vectors = vectors

        self.inv_vocab = {v: k for k, v in self.vocab.items()}

    def __getitem__(self, words):
        """
        Allows retrieving a vector by any of the following:

        >>> model['uruguay']
        array([ -1.2012412e-02, ...])

        >>> model[['uruguay', 'argentina']]
        array([ -1.2012412e-02, ...]
              [  4.2012412e-01, ...])
        """
        if isinstance(words, str):
            return self.vectors[self.vocab[words]]
        return np.vstack([self.vectors[self.vocab[word]] for word in words])

    def __contains__(self, word):
        return word in self.vocab

    def most_similar(self, positive=[], negative=[], topn=10):
        if isinstance(positive, str) and not negative:
            positive = [positive]

        all_words = set()
        vectors = []
        for word in positive:
            if isinstance(word, np.ndarray):
                vectors.append(word)
            elif word in self.vocab:
                all_words.add(self.vocab[word])
                vectors.append(self[word])
            else:
                raise KeyError("Word '{}' not in vocabulary".format(word))

        for word in negative:
            if isinstance(word, np.ndarray):
                vectors.append(-1.0 * word)
            elif word in self.vocab:
                all_words.add(self.vocab[word])
                vectors.append(-1.0 * self[word])
            else:
                raise KeyError("Word '{}' not in vocabulary".format(word))

        mean = np.mean(np.array(vectors), axis=0)
        distances = np.dot(self.vectors, mean)\
            / np.linalg.norm(self.vectors, axis=1)\
            / np.linalg.norm(mean)
        word_ids = np.argsort(-distances)

        result = (
            (self.inv_vocab[idx], distances[idx])
            for idx in word_ids
            if idx not in all_words
        )

        return list(islice(result, topn))

    def analogy(self, w1, w2, w3):
        return self.most_similar(positive=[w2, w3], negative=[w1])

    def doesnt_match(self, words):
        # Filter words that aren't in the vocabulary.
        words = [word for word in words if word in self.vocab]
        vectors = self[words]
        mean = np.mean(vectors, axis=0)

        distances = np.dot(vectors, mean)\
            / np.linalg.norm(vectors)\
            / np.linalg.norm(mean)

        return sorted(zip(distances, words))[0][1]


class GloveFactory:
    """
    Class tasked with training a Glove model, centralizing all the necessary
    information to do so. When trained, outputs a `Glove` class.
    """

    def __init__(self, vector_size=100, alpha=0.75, eta=0.05, window_size=15,
                 min_count=10, max_count=None, x_max=100.0, epochs=15,
                 threads=4, memory=4.0, env=None):
        # Model parameters.
        self.min_count = min_count
        self.max_count = max_count
        self.window_size = window_size
        self.memory = memory
        self.vector_size = vector_size
        self.alpha = alpha
        self.eta = eta
        self.epochs = epochs
        self.x_max = x_max
        self.threads = threads

        # Set up the running environment.
        env = env or {}
        self.executable_path = settings.GLOVE_PATH
        self.vocab_path = env.get('vocab_path', 'vocab.txt')
        self.cooccur_path = env.get('cooccur_path', 'cooccurrence.bin')
        self.shuf_cooccur_path = env.get('shuf_cooccur_path',
                                         'cooccurrence.shuf.bin')

    def load(self, vectors_path):
        return self._load_vectors(vectors_path)

    def build_vocabulary(self, corpus):
        self._build_vocab_count(corpus)

    def build_cooccurrence_matrix(self, corpus):
        self._build_cooccur_matrix(corpus)
        self._shuffle_cooccur_matrix()

    def train(self, vectors_path):
        self._run_glove(vectors_path)
        return self._load_vectors(vectors_path)

    def _build_vocab_count(self, corpus):
        output = open(self.vocab_path, 'w')

        base_command = join(self.executable_path, 'vocab_count')
        command = [base_command, '-min-count', str(self.min_count)]
        if self.max_count:
            command.extend(['-max-count', str(self.max_count)])

        process = Popen(
            command,
            stdin=PIPE, stdout=output, stderr=None,
            universal_newlines=True
        )

        for document in corpus:
            # Accept either a list of tokens or a string.
            if isinstance(document, list):
                document = " ".join(document)
            process.stdin.write(document)

        process.stdin.close()
        process.wait()
        output.close()

    def _build_cooccur_matrix(self, corpus):
        output = open(self.cooccur_path, 'wb')

        base_command = join(self.executable_path, 'cooccur')
        process = Popen([
            base_command, '-window-size', str(self.window_size), '-memory',
            str(self.memory), '-vocab-file', self.vocab_path,
        ], stdin=PIPE, stdout=output, stderr=None, universal_newlines=True)

        for document in corpus:
            # Accept either a list of tokens or a string.
            if isinstance(document, list):
                document = " ".join(document)
            process.stdin.write(document)

        process.stdin.close()
        process.wait()
        output.close()

    def _shuffle_cooccur_matrix(self):
        matrix = open(self.cooccur_path, 'rb')
        output = open(self.shuf_cooccur_path, 'wb')

        base_command = join(self.executable_path, 'shuffle')
        process = Popen(
            [base_command, '-memory', str(self.memory)],
            stdin=matrix, stdout=output, stderr=None,
            universal_newlines=True
        )

        process.wait()
        matrix.close()
        output.close()

    def _run_glove(self, vectors_path):
        base_command = join(self.executable_path, 'glove')
        process = Popen([
            base_command, '-vector-size', str(self.vector_size), '-threads',
            str(self.threads), '-iter', str(self.epochs), '-eta',
            str(self.eta), '-alpha', str(self.alpha), '-x-max',
            str(self.x_max), '-binary', '0', '-model', '2', '-input-file',
            self.shuf_cooccur_path, '-vocab-file', self.vocab_path,
            '-save-file', vectors_path
        ])
        process.wait()

    def _load_vectors(self, vectors_path):
        vocab = {}
        text_vectors = []
        with open('{}.txt'.format(vectors_path)) as f:
            for idx, line in enumerate(f):
                word, vector = line.split(' ', 1)
                vocab[word] = idx
                text_vectors.append(vector)
        vectors = np.loadtxt(text_vectors)
        return Glove(vocab, vectors)
