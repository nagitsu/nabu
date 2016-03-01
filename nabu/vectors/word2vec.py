import numpy as np

from nabu.vectors.embedding import Embedding


class Word2Vec(Embedding):
    pass


class Word2VecFactory:

    def __init__(self, model):
        """
        Receives a *trained* gensim Word2Vec model.

        Ideally would train it itself, but we'd need to juggle around corpus
        generators for that.
        """
        self.model = model

    @classmethod
    def load(cls, path):
        vocab_file = '{}.txt'.format(path)
        matrix_file = '{}.npy'.format(path)

        with open(vocab_file, 'r', encoding='utf-8') as f:
            words = {word.strip(): idx for idx, word in enumerate(f)}

        vectors = np.load(matrix_file)

        return Word2Vec(words, vectors)

    def save(self, path):
        # Normalize the model's vectors and save with the numpy format.
        self.model.init_sims(replace=True)
        vectors = self.model.syn0
        words = self.model.index2word

        vocab_file = '{}.txt'.format(path)
        matrix_file = '{}.npy'.format(path)

        with open(vocab_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(words))

        np.save(matrix_file, vectors)
