import numpy as np
import unicodedata
import logging

from collections import Counter

from math import sqrt
from random import random, randint
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from nltk.tokenize import RegexpTokenizer
from scipy.sparse import dok_matrix, csr_matrix
from sparsesvd import sparsesvd


es = Elasticsearch()

logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def read_corpus():
    documents = scan(
        es, index='nabu',
        scroll='30m', fields='content',
        # query={'query': {'match_all': {}}}
        # query={'query': {'match': {'data_source': '180.com.uy'}}}
        query={'query': {'match': {'data_source': 'lanacion.com.ar'}}}
    )

    for document in documents:
        content = document['fields']['content'][0]
        content = content.lower()
        content = unicodedata.normalize('NFKD', content)\
                             .encode('ascii', 'ignore')\
                             .decode('ascii')

        tokenizer = RegexpTokenizer(r'\w+')
        for sentence in content.split('. '):
            tokens = tokenizer.tokenize(sentence)
            yield " ".join(tokens)


def build_vocab(corpus, min_count=10, max_count=None):
    vocab = Counter()

    for sentence in corpus:
        vocab.update(Counter(sentence.split()))

    return {k: v for k, v in vocab.most_common(max_count) if v >= min_count}


def build_pairs(vocab, corpus, window=5, subsample=10e-5, dynamic_window=True):
    # Calculate the probability of removing each word in the vocabulary.
    # If count <= subsample, the probability will be negative, keep positives
    # only.
    corpus_size = sum(vocab.values())
    subsample = subsample * corpus_size
    subsampler = {
        word: 1 - sqrt(subsample / count)
        for word, count in vocab.items()
        if count > subsample
    }

    for sentence in corpus:

        tokens = [t for t in sentence.split() if t in vocab]
        if subsample:
            # If the token is in the list of tokens to subsample, draw a random
            # number and see if we should keep it.
            tokens = [
                t for t in tokens
                if t not in subsampler or random() > subsampler[t]
            ]

        len_tokens = len(tokens)

        for i, token in enumerate(tokens):
            if dynamic_window:
                curr_win = randint(1, window)
            else:
                curr_win = window

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


def build_cooccurrence(vocab, corpus, window=5, subsample=10e-5):
    pairs = build_pairs(vocab, corpus, window=window, subsample=subsample)

    words = sorted(list(vocab.keys()))
    w2i = {w: i for i, w in enumerate(words)}
    vocab_size = len(words)

    counts = csr_matrix((vocab_size, vocab_size), dtype=np.float32)
    tmp_counts = dok_matrix((vocab_size, vocab_size), dtype=np.float32)

    idx = 0
    update_threshold = 300000  # TODO: See how much bigger this can be.
    for word, context in pairs:
        if word in w2i and context in w2i:
            key = (w2i[word], w2i[context])
            if key in tmp_counts:
                tmp_counts[key] += 1
            else:
                tmp_counts[key] = 1

        idx += 1

        # Check if the main cooccurrence matrix must be updated.
        if idx == update_threshold:
            counts = counts + tmp_counts.tocsr()
            tmp_counts = dok_matrix((vocab_size, vocab_size), dtype=np.float32)
            idx = 0

    counts = counts + tmp_counts.tocsr()

    return counts, words, w2i


def build_ppmi(cooccur, cds=0.75):
    sum_w = np.array(cooccur.sum(axis=1))[:, 0]
    sum_c = np.array(cooccur.sum(axis=0))[0, :]
    if cds != 1:
        sum_c = sum_c ** cds
    sum_total = sum_c.sum()

    sum_w = np.reciprocal(sum_w)
    sum_c = np.reciprocal(sum_c)

    ppmi = csr_matrix(cooccur)
    ppmi = multiply_by_rows(ppmi, sum_w)
    ppmi = multiply_by_columns(ppmi, sum_c)
    ppmi = ppmi * sum_total

    # We want the positive PMI matrix.
    ppmi.data[ppmi.data < 0] = 0
    ppmi.eliminate_zeros()

    return ppmi


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


def build_svd(ppmi, dim=100, sum_context=True, eig_weight=0, normalize=True):
    ut, s, vt = sparsesvd(ppmi.tocsc(), dim)

    u = ut.T
    if eig_weight:
        u = np.dot(u, np.diag(s ** eig_weight))

    if sum_context:
        u += vt.T

    if normalize:
        norm = np.linalg.norm(u, axis=1)
        u = u / norm.reshape(-1, 1)

    return u


def main():
    min_count = 10
    max_count = None
    dim = 200
    window = 5
    subsample = 10e-5
    sum_context = True

    logger.debug('building vocabulary from corpus')
    vocab = build_vocab(
        read_corpus(),
        min_count=min_count,
        max_count=max_count,
    )
    logger.debug('%s words found', len(vocab))

    logger.debug('building the cooccurrence matrix')
    cooccur, words, w2i = build_cooccurrence(
        vocab, read_corpus(),
        window=window,
        subsample=subsample
    )
    logger.debug('%s non-zero entries', cooccur.nnz)

    logger.debug('building the explicit PPMI matrix of the coocc matrix')
    ppmi = build_ppmi(cooccur)
    logger.debug('%s non-zero entries', ppmi.nnz)

    logger.debug('building the SVD representation of the PPMI matrix')
    u = build_svd(ppmi, dim=dim, sum_context=sum_context)
    logger.debug('SVD representation obtained')

    # Sanity check.
    def nearest(vec):
        dists = np.dot(u, vec) / np.linalg.norm(vec)
        word_ids = np.argsort(-dists)
        for idx in word_ids[:15]:
            print(words[idx], dists[idx])
    # vec = u[w2i['uruguay']]
    vec = u[w2i['rey']] - u[w2i['reina']] + u[w2i['mujer']]
    nearest(vec)

    # mul = (np.dot(u, a_) * np.dot(u, b)) * np.reciprocal(np.dot(u, a) + 0.001
    # word_ids = np.argsort(mul)[::-1]

    from IPython import embed
    embed(display_banner=False)


if __name__ == '__main__':
    main()
