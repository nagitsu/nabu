import numpy as np

from os.path import join
from subprocess import Popen, PIPE

from nabu.core import settings
from nabu.vectors.embedding import Embedding


class Glove(Embedding):
    pass


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

    @classmethod
    def load(cls, vectors_path):
        vocab = {}
        text_vectors = []
        with open('{}.txt'.format(vectors_path)) as f:
            for idx, line in enumerate(f):
                word, vector = line.split(' ', 1)
                vocab[word] = idx
                text_vectors.append(vector)
        vectors = np.loadtxt(text_vectors)
        return Glove(vocab, vectors)

    def build_vocabulary(self, corpus):
        self._build_vocab_count(corpus)

    def build_cooccurrence_matrix(self, corpus):
        self._build_cooccur_matrix(corpus)
        self._shuffle_cooccur_matrix()

    def train(self, vectors_path):
        self._run_glove(vectors_path)
        return self.load(vectors_path)

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
