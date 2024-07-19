from stringanalysis.token_alignment import order_by_token_alignment_vectorized
import random

def test_alignment():
    results = order_by_token_alignment_vectorized(['bunc of grapes'], [['bananas', 'grapes']])
    assert results == [[1]]


def test_alignment_mismatched_case():
    results = order_by_token_alignment_vectorized(['bunch of grapes'], [['bananas', 'bunch', 'GRAPES BUNCH']])
    assert results == [[2, 1]]


def test_empty_vectors():
    results = order_by_token_alignment_vectorized(['bunch of  grapes'], [['']])
    assert results == [[]]


def test_empty_vectors_2():
    results = order_by_token_alignment_vectorized(['    '], [['']])
    assert results == [[]]


def test_min_length_of_4():
    results = order_by_token_alignment_vectorized(['low point'], [['low', 'point']])
    assert results == [[1]]


def test_error():
    results = order_by_token_alignment_vectorized([
        'Catheter, infusion, inserted peripherally, centrally or midline (other than hemodialysis)',
        'Anchor/screw for opposing bone-to-bone or soft tissue-to-bone (implantable)'
    ], [[], []])
    assert results == [[], []]


def test_large_list():
    values = [[] if random.choice([0, 1]) == 0 else ['abcd'] for _ in range(60)]
    results = order_by_token_alignment_vectorized(
        ['abcd' for _ in range(60)],
        values
    )
    assert results == [[] if v == [] else [0] for v in values]

