from time import time

from nabu.core.models import db, Result


def evaluate(embedding, testset):
    start_time = time()
    if testset.test_type == 'analogies':
        # Open testset file and preprocess with embedding's options.
        with open(testset.full_path, 'r') as f:
            analogies = []
            for line in f.readlines():
                # Preprocess the line like the embedding.
                if embedding.parameters['lowercase_tokens']:
                    line = line.lower()

                w1, w2, w3, w4 = line.strip().split()
                analogies.append((w1, w2, w3, w4))

        # Load the embedding model on memory.
        # TODO: Make sure the GloVe model has a similar interface.
        model = embedding.load_model()

        # Run the test and fill `accuracy`, `extended_results`.
        results = []
        for analogy in analogies:
            if not all(w in model for w in analogy):
                # One of the words is not present, ignore test.
                # TODO: Is it OK to ignore it?
                continue

            w1, w2, w3, w4 = analogy
            result, _ = zip(*model.most_similar(
                positive=[w2, w3],
                negative=[w1],
                topn=10,
            ))

            results.append((
                w4 in result[:1],
                w4 in result[:5],
                w4 in result[:10],
            ))

        top1 = len(list(filter(lambda r: r[0], results))) / len(results)
        top5 = len(list(filter(lambda r: r[1], results))) / len(results)
        top10 = len(list(filter(lambda r: r[2], results))) / len(results)

        accuracy = top1
        extended = {
            'top1': top1,
            'top5': top5,
            'top10': top10,
            'tested': len(results),
            'total': len(analogies),
        }

    else:
        return

    end_time = time()

    # Get or create a `Result` instance for the <embedding, testset> pair.
    elapsed = int(end_time - start_time)
    result = Result(
        embedding=embedding,
        testset=testset,
        accuracy=accuracy,
        extended=extended,
        elapsed_time=elapsed
    )

    db.merge(result)
    db.commit()

    # Return the instance.
    return result
