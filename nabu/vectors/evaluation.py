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
            # One of the words is not present, ignore test.
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

        if report and (idx + 1) % 25 == 0:
            report(idx / len(analogies))

    if results:
        top1 = len(list(filter(lambda r: r[0], results))) / len(results)
        top5 = len(list(filter(lambda r: r[1], results))) / len(results)
        top10 = len(list(filter(lambda r: r[2], results))) / len(results)
    else:
        top1 = top5 = top10 = 0

    accuracy = top1
    extended = {
        'top1': top1,
        'top5': top5,
        'top10': top10,
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
