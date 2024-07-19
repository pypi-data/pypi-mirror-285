from dataclasses import dataclass

from stringanalysis.sort_list_of_lists import sort_list_of_lists


def test_sort_list_of_lists():
    results = sort_list_of_lists([
        [("a", 2), ("b", 3)]
    ])
    assert results == [["b", "a"]]


@dataclass
class O:
    a: int


def test_sort_list_of_lists2():
    def do_it():
        results = sort_list_of_lists([
            [((O(9), 2), 2), (("b", 3), 3)]
        ])
        assert results == [[("b", 3), (O(9), 2)]]

    for _ in range(100):
        do_it()


def test_sort_list_of_lists_keep_scores():
    results = sort_list_of_lists([
        [("a", 2), ("b", 3)]
    ], keep_scores=True)
    assert results == [[("b", 3), ("a", 2)]]
