import numpy as np
import unicodedata
import random
import logging

from collections import Counter
from itertools import islice
from os.path import join
from subprocess import Popen, PIPE

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
        query={'query': {'match': {'data_source': '180.com.uy'}}}
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


def build_vocab(corpus):
    vocab = Counter()

    for sentence in corpus:
        tokens = sentence.split()
        if len(tokens) < 2:
            # If there aren't at least two words, discard the sentence.
            continue
        vocab.update(Counter(tokens))

    # TODO: min_count
    return dict(vocab)


def build_pairs(vocab, corpus, window=5):
    pairs = Counter()

    # TODO: subsampling
    # TODO: dynamic window
    for sentence in corpus:

        tokens = [t for t in sentence.split() if t in vocab]
        len_tokens = len(tokens)

        for i, token in enumerate(tokens):
            start = i - window
            if start < 0:
                start = 0
            end = i + window + 1
            if end > len_tokens:
                end = len_tokens

            for j in range(start, end):
                if j == i:
                    continue
                pairs[(token, tokens[j])] += 1

    return dict(pairs)


def build_cooccurrence(vocab, pairs):
    words = sorted(list(vocab.keys()))
    w2i = {w: i for i, w in enumerate(words)}
    vocab_size = len(words)

    counts = csr_matrix((vocab_size, vocab_size), dtype=np.float32)
    tmp_counts = dok_matrix((vocab_size, vocab_size), dtype=np.float32)

    idx = 0
    update_threshold = 100000
    for (word, context), count in pairs.items():
        if word in w2i and context in w2i:
            tmp_counts[w2i[word], w2i[context]] = count
        idx += 1

        # Check if the main cooccurrence matrix must be updated.
        if idx == update_threshold:
            counts = counts + tmp_counts.tocsr()
            tmp_counts = dok_matrix((vocab_size, vocab_size), dtype=np.float32)
            idx = 0

    counts = counts + tmp_counts.tocsr()

    return counts, words


def build_ppmi(cooccur):
    # TODO: cds

    # TODO: sum_w and sum_c have some zero entries; why?
    sum_w = np.array(cooccur.sum(axis=1))[:, 0]
    sum_c = np.array(cooccur.sum(axis=0))[0, :]
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


def build_svd(ppmi, dim=100):
    ut, s, vt = sparsesvd(ppmi.tocsc(), dim)
    return ut, s, vt


def main():
    logger.debug('building vocabulary from corpus')
    vocab = build_vocab(read_corpus())
    logger.debug('%s words found', len(vocab))

    logger.debug('building the pair counts')
    pairs = build_pairs(vocab, read_corpus())
    logger.debug('%s pairs generated', len(pairs))

    logger.debug('building the cooccurrence matrix')
    cooccur, words = build_cooccurrence(vocab, pairs)
    logger.debug('%s non-zero entries', cooccur.nnz)

    logger.debug('building the explicit PPMI matrix of the coocc matrix')
    ppmi = build_ppmi(cooccur)
    logger.debug('%s non-zero entries', ppmi.nnz)

    logger.debug('building the SVD representation of the PPMI matrix')
    ut, s, vt = build_svd(ppmi)
    logger.debug('SVD representation obtained')

    from IPython import embed
    embed(display_banner=False)


if __name__ == '__main__':
    main()
