import numpy as np
import logging

from collections import Counter

from math import sqrt
from random import random, randint
from scipy.sparse import dok_matrix, csr_matrix
from sparsesvd import sparsesvd

from nabu.vectors.embedding import Embedding


logger = logging.getLogger(__name__)


def multiply_by_rows(matrix, row_coefs):
    """
    Utility function to multiply a sparse matrix by rows.
    """
    normalizer = dok_matrix((len(row_coefs), len(row_coefs)))
    normalizer.setdiag(row_coefs)
    return normalizer.tocsr().dot(matrix)


def multiply_by_columns(matrix, col_coefs):
    """
    Utility function to multiply a sparse matrix by columns.
    """
    normalizer = dok_matrix((len(col_coefs), len(col_coefs)))
    normalizer.setdiag(col_coefs)
    return matrix.dot(normalizer.tocsr())


class SVD(Embedding):
    pass


class SVDFactory:

    def __init__(self, min_count=30, max_count=None, dim=300, window=5,
                 subsample=1e-5, cds=0.75, sum_context=True):

        self.min_count = min_count
        self.max_count = max_count
        self.dim = dim
        self.window = window
        self.subsample = subsample
        self.cds = cds
        self.sum_context = sum_context

    @classmethod
    def load(cls, path):
        vocab_file = '{}.txt'.format(path)
        matrix_file = '{}.npy'.format(path)

        with open(vocab_file, 'r', encoding='utf-8') as f:
            words = {word.strip(): idx for idx, word in enumerate(f)}

        vectors = np.load(matrix_file)

        return SVD(words, vectors)

    def build_vocabulary(self, corpus):
        logger.debug('building vocabulary from corpus')
        vocab = Counter()

        for tokens in corpus:
            if len(tokens) < 2:
                # Discard sentences that are too short.
                continue
            vocab.update(Counter(tokens))

        self.vocab = {
            k: v
            for k, v in vocab.most_common(self.max_count)
            if v >= self.min_count
        }
        logger.debug('%s words found', len(self.vocab))

    def build_svd(self, corpus, eig=0, normalize=True):
        ppmi = self._build_ppmi(corpus)

        logger.debug('building the SVD representation of the PPMI matrix')

        ut, s, vt = sparsesvd(ppmi.tocsc(), self.dim)

        m = ut.T
        if eig:
            m = np.dot(m, np.diag(s ** eig))

        if self.sum_context:
            m += vt.T

        if normalize:
            norm = np.linalg.norm(m, axis=1)
            m = m / norm.reshape(-1, 1)

        logger.debug('SVD representation obtained')

        self.vectors = m

    def train(self):
        return SVD(self.w2i, self.vectors)

    def save(self, path):
        vocab_file = '{}.txt'.format(path)
        matrix_file = '{}.npy'.format(path)

        with open(vocab_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.words))

        np.save(matrix_file, self.vectors)

    def _build_ppmi(self, corpus):
        cooccur = self._build_cooccurrence(corpus)

        logger.debug('building the explicit PPMI matrix of the coocc matrix')

        sum_w = np.array(cooccur.sum(axis=1))[:, 0]
        sum_c = np.array(cooccur.sum(axis=0))[0, :]
        if self.cds != 1:
            sum_c = sum_c ** self.cds
        sum_total = sum_c.sum()

        sum_w = np.reciprocal(sum_w)
        sum_c = np.reciprocal(sum_c)

        ppmi = csr_matrix(cooccur)
        ppmi = multiply_by_rows(ppmi, sum_w)
        ppmi = multiply_by_columns(ppmi, sum_c)
        ppmi = ppmi * sum_total

        # Apply log to non-zero entries.
        ppmi.data = np.log(ppmi.data)

        # We want the positive PMI matrix.
        ppmi.data[ppmi.data < 0] = 0
        ppmi.eliminate_zeros()

        logger.debug('%s non-zero entries', ppmi.nnz)

        return ppmi

    def _build_cooccurrence(self, corpus):
        logger.debug('building the cooccurrence matrix')

        pairs = self._build_pairs(corpus)

        self.words = sorted(list(self.vocab.keys()))
        self.w2i = {w: i for i, w in enumerate(self.words)}
        vocab_size = len(self.words)

        counts = csr_matrix((vocab_size, vocab_size), dtype=np.float32)
        tmp_counts = dok_matrix((vocab_size, vocab_size), dtype=np.float32)

        idx = 0
        update_threshold = 300000
        for word, context in pairs:
            if word in self.w2i and context in self.w2i:
                key = (self.w2i[word], self.w2i[context])
                if key in tmp_counts:
                    tmp_counts[key] += 1
                else:
                    tmp_counts[key] = 1

            idx += 1

            # Check if the main cooccurrence matrix must be updated.
            if idx == update_threshold:
                counts = counts + tmp_counts.tocsr()
                tmp_counts = dok_matrix(
                    (vocab_size, vocab_size),
                    dtype=np.float32
                )
                idx = 0

        counts = counts + tmp_counts.tocsr()
        logger.debug('%s non-zero entries', counts.nnz)

        return counts

    def _build_pairs(self, corpus):
        # Calculate the probability of removing each word in the vocabulary.
        # If count <= subsample, the probability will be negative, keep
        # positives only.
        corpus_size = sum(self.vocab.values())
        self.subsample = self.subsample * corpus_size
        subsampler = {
            word: 1 - sqrt(self.subsample / count)
            for word, count in self.vocab.items()
            if count > self.subsample
        }

        for sentence in corpus:

            tokens = [t for t in sentence if t in self.vocab]
            if self.subsample:
                # If the token is in the list of tokens to subsample, draw a
                # random number and see if we should keep it.
                tokens = [
                    t for t in tokens
                    if t not in subsampler or random() > subsampler[t]
                ]

            len_tokens = len(tokens)

            for i, token in enumerate(tokens):
                # Use dynamic windows.
                curr_win = randint(1, self.window)

                start = i - curr_win
                if start < 0:
                    start = 0
                end = i + curr_win + 1
                if end > len_tokens:
                    end = len_tokens

                for j in range(start, end):
                    if j == i:
                        continue
                    yield (token, tokens[j])
