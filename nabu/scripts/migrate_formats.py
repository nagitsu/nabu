import gensim
import numpy as np
import os

from os.path import exists

from nabu.core.models import db, Embedding


def migrate_glove(embedding):
    vocab_file = "{}.txt".format(embedding.full_path)
    matrix_file = "{}.npy".format(embedding.full_path)

    if exists(matrix_file):
        print("embedding_id={} already migrated".format(embedding.id))
        return

    old_file = embedding.get_all_files()[0]

    # Load old file.
    words = []
    text_vectors = []
    with open("{}.txt".format(embedding.full_path)) as f:
        for line in f:
            word, vector = line.split(' ', 1)
            words.append(word)
            text_vectors.append(vector)
    vectors = np.loadtxt(text_vectors)

    # Normalize vectors and save to new locations.
    vectors /= np.linalg.norm(vectors, axis=1).reshape(-1, 1)

    # Backup the old file.
    os.rename(old_file, old_file + '.backup')

    with open(vocab_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(words))

    np.save(matrix_file, vectors)

    # Finally, display which files to delete.
    print("delete={}.backup".format(old_file))


def migrate_word2vec(embedding):
    vocab_file = "{}.txt".format(embedding.full_path)
    matrix_file = "{}.npy".format(embedding.full_path)

    if exists(matrix_file):
        print("embedding_id={} already migrated".format(embedding.id))
        return

    old_files = embedding.get_all_files()

    # Load old file.
    model = gensim.models.Word2Vec.load(embedding.full_path)

    # Normalize vectors and save to new locations.
    model.init_sims(replace=True)
    vectors = model.syn0
    words = model.index2word

    with open(vocab_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(words))

    np.save(matrix_file, vectors)

    # Finally, display which files to delete.
    for f in old_files:
        print("delete={}".format(f))


def main():
    embeddings = db.query(Embedding).all()
    for embedding in embeddings:
        if embedding.model == 'glove':
            migrate_glove(embedding)
        elif embedding.model == 'word2vec':
            migrate_word2vec(embedding)


if __name__ == '__main__':
    main()
