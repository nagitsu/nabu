import json
import random


TESTSETS = [
    {'name': 'inf-cond-3pl', 'field1': 'infinitivo', 'field2': 'condicional.ellos'},
    {'name': 'inf-fut-3pl', 'field1': 'infinitivo', 'field2': 'futuro_1.ellos'},
    {'name': 'inf-gerund', 'field1': 'infinitivo', 'field2': 'gerundio'},
    {'name': 'inf-imp-3pl', 'field1': 'infinitivo', 'field2': 'imperativo_presente.ellos'},
    {'name': 'inf-pretimp-3pl', 'field1': 'infinitivo', 'field2': 'imperfecto.ellos'},
    {'name': 'inf-preindef-3sg', 'field1': 'infinitivo', 'field2': 'indefinido.el'},
    {'name': 'inf-participio', 'field1': 'infinitivo', 'field2': 'participio'},
    {'name': 'inf-pres-3sg', 'field1': 'infinitivo', 'field2': 'presente.el'},
    {'name': 'inf-pres-3pl', 'field1': 'infinitivo', 'field2': 'presente.ellos'},
    {'name': 'inf-subjf-3sg', 'field1': 'infinitivo', 'field2': 'subjuntivo_futuro.el'},
    {'name': 'inf-subjp-3sg', 'field1': 'infinitivo', 'field2': 'subjuntivo_p_i_1.el'},
    {'name': 'inf-subjp-3pl', 'field1': 'infinitivo', 'field2': 'subjuntivo_p_i_1.ellos'},

    {'name': 'inf-cond-sp', 'field1': 'infinitivo', 'field2': 'condicional.vosotros'},
    {'name': 'inf-fut-sp', 'field1': 'infinitivo', 'field2': 'futuro_1.vosotros'},
    {'name': 'inf-pret-sp', 'field1': 'infinitivo', 'field2': 'indefinido.vosotros'},
]


OOO_TESTSETS = [
    {'name': 'ooo-cond-3pl-inf', 'field1': 'condicional.ellos', 'field2': 'infinitivo'},
    {'name': 'ooo-pret-3sg-inf', 'field1': 'indefinido.el', 'field2': 'infinitivo'},
    {'name': 'ooo-fut-3pl-inf', 'field1': 'futuro_1.ellos', 'field2': 'infinitivo'},
    {'name': 'ooo-fut-3pl-pres-3pl', 'field1': 'futuro_1.ellos', 'field2': 'presente.ellos'},
    {'name': 'ooo-fut-3pl-subf-3sg', 'field1': 'futuro_1.ellos', 'field2': 'subjuntivo_futuro.el'},
]


def nested_get(d, key):
    for bit in key.split('.'):
        d = d[bit]
    return d


def analogies():
    with open('conjugate-verbs-ES.txt') as f:
        verbs = json.load(f)
        for verb, conjs in verbs.items():
            conjs['infinitivo'] = verb

    for testset in TESTSETS:
        tests = []
        for verb, conjs in verbs.items():
            field1 = nested_get(conjs, testset['field1'])
            field2 = nested_get(conjs, testset['field2'])

            others = list(set(verbs.keys()) - {verb})
            random.shuffle(others)
            for other in others[:10]:
                other_conjs = verbs[other]
                other_field1 = nested_get(other_conjs, testset['field1'])
                other_field2 = nested_get(other_conjs, testset['field2'])
                if random.randint(1, 2) == 1:
                    tests.append((field1, field2, other_field1, other_field2))
                else:
                    tests.append((field2, field1, other_field2, other_field1))

        testset_path = "tests/{}.txt".format(testset['name'])
        with open(testset_path, 'w') as f:
            for test in tests:
                print(" ".join(test), file=f)


def rp_analogies():
    with open('verbs-ES-RP.txt') as f:
        verbs = {}
        for line in f:
            conj, verb = line.strip().split()
            verbs[verb] = conj

    tests = []
    for verb, conj in verbs.items():
        others = list(set(verbs.keys()) - {verb})
        random.shuffle(others)
        for other in others[:10]:
            other_conj = verbs[other]
            if random.randint(1, 2) == 1:
                tests.append((verb, conj, other, other_conj))
            else:
                tests.append((conj, verb, other_conj, other))

    testset_path = "tests/inf-vos.txt"
    with open(testset_path, 'w') as f:
        for test in tests:
            print(" ".join(test), file=f)


def ooo():
    with open('conjugate-verbs-ES.txt') as f:
        verbs = json.load(f)
        by_conj = {}
        for verb, conjs in verbs.items():
            by_conj.setdefault('infinitivo', []).append(verb)
            for conjn, conjf in conjs.items():
                if isinstance(conjf, str):
                    by_conj.setdefault(conjn, []).append(conjf)
                else:
                    for nconjn, nconjf in conjf.items():
                        name = "{}.{}".format(conjn, nconjn)
                        by_conj.setdefault(name, []).append(nconjf)

    for testset in OOO_TESTSETS:
        tests = []
        odd = by_conj[testset['field1']]
        rest = by_conj[testset['field2']]

        # Twice each verb.
        for verb in odd * 2:
            current_test = [verb]
            random.shuffle(rest)
            current_test.extend(rest[:4])
            tests.append(tuple(current_test))

        testset_path = "ooo/{}.txt".format(testset['name'])
        with open(testset_path, 'w') as f:
            for test in tests:
                print(" ".join(test), file=f)


if __name__ == '__main__':
    # analogies()
    # ooo()
    rp_analogies()
