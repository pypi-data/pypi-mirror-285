from stringanalysis.dict import stringanalysisdict, StringAnalysisDict
from stringanalysis.dict import stringanalysisdefaultdict


def test_it_gets():
    d = stringanalysisdict()
    d.insert('a', ['b'])
    assert d.get('a') == ['b']


def test_it_gets_by_prefix():
    d = stringanalysisdict()
    d.insert('abc', ['b'])
    assert d.get_by_prefix('ab', 1) == [('abc', ['b'])]
    assert d.get_by_prefix('ab', 2) == []
    assert d.get_by_prefix('abc', 1) == []

    d.insert('abg', ['c'])
    assert d.get_by_prefix('ab', 1) == [('abc', ['b']), ('abg', ['c'])]


def test_it_gets_by_prefix_vectorized():
    d = stringanalysisdict()
    d.insert('abc', ['b'])
    assert d.get_by_prefix_vectorized(['ab', 'abc'], 1) == [[('abc', ['b'])], []]


def test_it_gets_by_prefix_with_min_length():
    d = stringanalysisdict()
    d.insert('abc', ['b'])
    assert d.get_by_prefix('ab', 1, 3) == []


def test_it_gets_by_any_prefix():
    d = stringanalysisdict()
    d.insert('abc', 'b')
    d.insert('cd', 'f')
    assert d.get_by_any_prefix(['ab', 'c'], 1) == [('abc', 'b'), ('cd', 'f')]


def test_it_gets_by_any_prefix_vectorized():
    d = stringanalysisdict()
    d.insert('abc', 'b')
    d.insert('cd', 'f')
    assert d.get_by_any_prefix_vectorized([['ab', 'c'], ['ab', 'c']], 1) == \
           [[('abc', 'b'), ('cd', 'f')], [('abc', 'b'), ('cd', 'f')]]


def test_it_gets_by_superstring():
    d = stringanalysisdict()
    d.insert('abcd', ['b'])
    assert d.get_by_superstring('0abcde') == [('abcd', ['b'])]
    assert d.get_by_superstring('ab') == []

    d.insert('bcde', ['c'])
    assert d.get_by_superstring('0abcde') == [('abcd', ['b']), ('bcde', ['c'])]


def test_it_gets_by_superstring_closer_first():
    d = stringanalysisdict()
    d.insert('abcd', ['b'])
    d.insert('abcdefgh', ['c'])
    assert d.get_by_superstring('abcdefghgfh') == [('abcdefgh', ['c']), ('abcd', ['b'])]


def test_it_gets_by_superstring_does_not_duplicate():
    d = stringanalysisdict()
    d.insert('abca', ['b'])
    assert d.get_by_superstring('0abcabcad') == [('abca', ['b'])]
    assert d.get_by_superstring('ab') == []


def test_it_gets_by_superstring_vectorized():
    d = stringanalysisdict()
    d.insert('abcd', ['b'])
    assert d.get_by_superstring_vectorized(['0abcde', 'ab']) == [[('abcd', ['b'])], []]

    d.insert('bcde', ['c'])
    assert d.get_by_superstring_vectorized(['0abcde']) == [[('abcd', ['b']), ('bcde', ['c'])]]


def test_it_gets_by_superstring_min_length():
    d = stringanalysisdict()
    d.insert('abc', ['b'])
    assert d.get_by_superstring('0abcde', 10) == []


def test_it_gets_by_any_superstring():
    d = stringanalysisdict()
    d.insert('abcd', ['b'])
    d.insert('cdef', ['f'])
    assert d.get_by_any_superstring(['0abcde', 'cdefg']) == [('cdef', ['f']), ('abcd', ['b'])]
    assert d.get_by_any_superstring(['ab', 'c']) == []


def test_it_gets_by_any_superstring_vectorized():
    d = stringanalysisdict()
    d.insert('abcd', 'b')
    d.insert('cdef', 'f')
    assert d.get_by_any_superstring_vectorized([['0abcdef', 'cdef'], ['0abcdef', 'cdef']]) == \
           [[('cdef', 'f'), ('abcd', 'b')], [('cdef', 'f'), ('abcd', 'b')]]


def test_it_gets_by_any_superstring_vectorized_with_score():
    d = stringanalysisdict()
    d.insert('abcd', 'b')
    d.insert('cdef', 'f')
    assert d.get_by_any_superstring_vectorized_with_score([['0abcdef', 'cdef'], ['0abcdef', 'cdef']]) == \
           [[('cdef', 'f', 1.0), ('abcd', 'b', 0.57)], [('cdef', 'f', 1.0), ('abcd', 'b', 0.57)]]


def test_it_gets_by_superstring_4_chars():
    d = stringanalysisdict()
    d.insert('AFTU', ['b'])
    assert d.get_by_superstring('AFTU') == [('AFTU', ['b'])]


def test_it_can_star_with_values():
    d = stringanalysisdict(abcd='b')
    assert d.get_by_superstring('0abcd0') == [('abcd', 'b')]
    assert d.get('abcd') == 'b'


def test_it_gets_by_overlap():
    d = stringanalysisdict()
    d.insert('abcdef', ['b'])
    assert d.get_by_overlap('0abcd') == [('abcdef', ['b'])]
    assert d.get_by_overlap('0abce') == []

    d.insert('abcd888', ['c'])
    assert sorted(d.get_by_overlap('0abcd')) == sorted([('abcdef', ['b']), ('abcd888', ['c'])])


def test_it_gets_by_overlap_vectorized():
    d = stringanalysisdict()
    d.insert('abcdef', ['b'])
    d.insert('ghjkl', ['c'])
    assert d.get_by_overlap_vectorized(['0abcd', '0ghjk']) == [[('abcdef', ['b'])], [('ghjkl', ['c'])]]


def test_it_gets_by_overlap_with_min():
    d = stringanalysisdict()
    d.insert('abcdefghijklm', ['b'])
    assert d.get_by_overlap('00abcdefghi', 5) == [('abcdefghijklm', ['b'])]
    assert d.get_by_overlap('00abcd', 5) == []


def test_keys():
    d = stringanalysisdict(abcd='b')
    assert d.keys() == ['abcd']


def test_keys_stringanalysisdefaultdict():
    d = stringanalysisdefaultdict(abcd='b', default=lambda: [])
    assert d.keys() == ['abcd']


def test_it_inserts_pairs():
    d = stringanalysisdict()
    d.insert_pairs([('a', ('b', 'c')), ('b', ('d'))])
    assert d.get('a') == ('b', 'c')
    assert d.get('b') == ('d')


def test_it_inserts_keys_and_values():
    d = stringanalysisdict()
    d.insert_keys_and_values(['a', 'b'], [('b', 'c'), 'd'])
    assert d.get('a') == ('b', 'c')
    assert d.get('b') == ('d')


def test_it_gets_fuzzy():
    d = stringanalysisdict()
    d.insert('abc', 'b')
    d.insert('akc', 'c')
    d.finalize()
    assert d.get_fuzzy('adc', 1) == [('abc', 'b'), ('akc', 'c')]


def test_it_gets_fuzzy_vectorized():
    d = stringanalysisdict()
    d.insert('abc', 'b')
    d.insert('akc', 'c')
    d.insert('bcd', 'f')
    d.finalize()
    assert d.get_fuzzy_vectorized(['adc', 'bcd'], 1) == [[('abc', 'b'), ('akc', 'c')], [('bcd', 'f')]]


def test_can_get_bytes_and_recreate():
    d = stringanalysisdict()
    d.insert('abc', 'b')
    d.finalize()
    d = StringAnalysisDict.from_bytes(d.as_bytes())
    assert d.get('abc') == 'b'
    assert d.get_fuzzy('ab', 1)
