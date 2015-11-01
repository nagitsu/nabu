import numpy as np

from itertools import islice


class Embedding:
    """
    Base class that implements common functions for all embeddings.
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

    def most_similar_cosmul(self, positive=[], negative=[], topn=10):
        if isinstance(positive, str) and not negative:
            positive = [positive]

        all_words = set()

        def word_vec(word):
            if isinstance(word, np.ndarray):
                return word
            elif word in self.vocab:
                all_words.add(self.vocab[word])
                return self[word]
            else:
                raise KeyError("Word '{}' not in vocabulary".format(word))

        positive = [word_vec(word) for word in positive]
        negative = [word_vec(word) for word in negative]

        if not positive:
            raise ValueError("Cannot compute similarity with no input")

        def distance(vector):
            return np.dot(self.vectors, vector)\
                / np.linalg.norm(self.vectors, axis=1)\
                / np.linalg.norm(vector)

        # Shift to [0, 1] so we don't have negative distances.
        pos_dists = [((1 + distance(vector)) / 2) for vector in positive]
        neg_dists = [((1 + distance(vector)) / 2) for vector in negative]
        distances = (
            np.prod(pos_dists, axis=0) /
            (np.prod(neg_dists, axis=0) + 0.0001)
        )
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
        if not words:
            raise ValueError("None of the words is in the vocabulary")

        vectors = self[words]
        mean = np.mean(vectors, axis=0)

        distances = np.dot(vectors, mean)\
            / np.linalg.norm(vectors)\
            / np.linalg.norm(mean)

        return sorted(zip(distances, words))[0][1]
