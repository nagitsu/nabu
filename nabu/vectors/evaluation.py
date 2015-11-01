from nabu.core.models import db, Result
from nabu.vectors.utils import read_analogies, build_token_preprocessor


def evaluate_analogies(embedding, testset, report=None):
    """
    Evaluates the given embedding against an analogies testset.
    """
    model = embedding.load_model()
    preprocessor = build_token_preprocessor(embedding.preprocessing)
    analogies = list(read_analogies(testset.full_path, preprocessor))

    # Run the test and fill `accuracy`, `extended_results`. Report every
    # 25 analogies tested.
    results = []
    for idx, analogy in enumerate(analogies):
        if not all(w in model for w in analogy):
            # One of the words is not present, count as a failed test.
            results.append((False, False, False, False, False, False))
            continue

        w1, w2, w3, w4 = analogy

        # Calculate the results both with 3CosAdd and 3CosMul.
        result_mul, _ = zip(*model.most_similar_cosmul(
            positive=[w2, w3], negative=[w1], topn=10,
        ))
        result_add, _ = zip(*model.most_similar(
            positive=[w2, w3], negative=[w1], topn=10,
        ))

        results.append((
            w4 in result_mul[:1], w4 in result_mul[:5], w4 in result_mul[:10],
            w4 in result_add[:1], w4 in result_add[:5], w4 in result_add[:10],
        ))

        if report and (idx + 1) % 25 == 0:
            report(idx / len(analogies))

    if results:
        top1_mul = len(list(filter(lambda r: r[0], results))) / len(results)
        top5_mul = len(list(filter(lambda r: r[1], results))) / len(results)
        top10_mul = len(list(filter(lambda r: r[2], results))) / len(results)

        top1_add = len(list(filter(lambda r: r[3], results))) / len(results)
        top5_add = len(list(filter(lambda r: r[4], results))) / len(results)
        top10_add = len(list(filter(lambda r: r[5], results))) / len(results)
    else:
        top1_mul = top5_mul = top10_mul = 0
        top1_add = top5_add = top10_add = 0

    # We use 3CosMul as default accuracy, as it's the state-of-the-art.
    accuracy = top1_mul
    extended = {
        'top1_mul': top1_mul,
        'top5_mul': top5_mul,
        'top10_mul': top10_mul,

        'top1_add': top1_add,
        'top5_add': top5_add,
        'top10_add': top10_add,

        'tested': len(results),
        'total': len(analogies),
    }

    return accuracy, extended


def evaluate(embedding, testset, report=None):
    """
    Tests the given embedding against the given testset.
    """
    if testset.test_type == 'analogies':
        evaluator = evaluate_analogies

    accuracy, extended = evaluator(embedding, testset, report=report)

    # Get or create a `Result` instance for the <embedding, testset> pair.
    result = Result(
        embedding=embedding,
        testset=testset,
        accuracy=accuracy,
        extended=extended,
    )
    result = db.merge(result)

    return result
