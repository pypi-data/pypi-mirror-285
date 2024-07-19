import pytest  # type: ignore

from stringanalysis.regex_parts import regex_parts


@pytest.mark.skip
def test_regex_parts():
    results = regex_parts([
        ('7987954-U56', '7987954-56'),
        ('7987984-U58', '7987984-58')
    ], 100)
    assert results == ([r'\d+', '-', 'U', r'\d+'], [1, 2, 4])


@pytest.mark.skip
def test_full_string():
    results = regex_parts([
        ('GEM1124', 'GEM1124T'),
        ('DYNJP8401UG', 'DYNJP8401'),
        ('NON27382FR', 'NON27382'),
        ('GEM3124', 'GEM3124T'),
        ('GEM5148', 'GEM5148T'),
    ], 100)
    assert results is None
