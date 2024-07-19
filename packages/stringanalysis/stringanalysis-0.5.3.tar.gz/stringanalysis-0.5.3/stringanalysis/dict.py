import pickle
from io import BytesIO
from typing import List, Optional, Mapping, Any, Iterable, Tuple
from stringanalysis.stringanalysis import stringanalysisdict_from_bytes, stringanalysisdict as rawstringanalysisdict  # type: ignore


class StringAnalysisDict:
    def __init__(self):
        self._dict = rawstringanalysisdict()
        self.__lookup = {}
        self._counter = 0

    def insert_keys_and_values(self, keys: List[str], values: List[Any]):
        indexes = []
        for v in values:
            self.__lookup[self._counter] = v
            indexes.append(self._counter)
            self._counter += 1
        self._dict.insert_keys_and_values(keys, indexes)

    def insert(self, key: str, value: Any):
        self.__lookup[self._counter] = value
        self._dict.insert(key, self._counter)
        self._counter += 1

    def insert_pairs(self, pairs: List[Tuple[str, Any]]):
        new_pairs = []
        for k, v in pairs:
            self.__lookup[self._counter] = v
            new_pairs.append((k, self._counter))
            self._counter += 1
        self._dict.insert_pairs(new_pairs)

    def _lookup(self, i: Optional[int]):
        return None if i is None else self.__lookup[i]

    def get_fuzzy(self, key: Optional[str], distance: int):
        return [(i[0], self._lookup(i[1])) for i in self._dict.get_fuzzy(key, distance)]

    def get_fuzzy_vectorized(self, keys: List[Optional[str]], distance: int):
        return [[(j[0], self._lookup(j[1])) for j in i] for i in self._dict.get_fuzzy_vectorized(keys, distance)]

    def keys(self) -> List[str]:
        return self._dict.keys()

    def get(self, key: str) -> Any:
        return self._lookup(self._dict.get(key))

    def get_by_prefix(self, key: str, length_diff: int = 0, min_length: int = 0) -> Any:
        return [(i[0], self._lookup(i[1])) for i in self._dict.get_by_prefix(key, length_diff, min_length)]

    def get_by_any_prefix(self, keys: List[Optional[str]], length_diff: int = 0, min_length: int = 0) -> Any:
        return [(i[0], self._lookup(i[1])) for i in self._dict.get_by_any_prefix(keys, length_diff, min_length)]

    def get_by_prefix_vectorized(self, keys: List[Optional[str]], length_diff: int = 0) -> Any:
        return [[(j[0], self._lookup(j[1])) for j in i] for i in self._dict.get_by_prefix_vectorized(keys, length_diff)]

    def get_by_overlap(self, key: str, min_overlap: int = 0) -> Any:
        return [(i[0], self._lookup(i[1])) for i in self._dict.get_by_overlap(key, min_overlap)]

    def get_by_overlap_vectorized(self, keys: List[Optional[str]], min_overlap: int = 0) -> Any:
        return [[(j[0], self._lookup(j[1])) for j in i] for i in self._dict.get_by_overlap_vectorized(keys, min_overlap)]

    def get_by_superstring(self, key: str, min_overlap: int = 0) -> Any:
        return [(i[0], self._lookup(i[1])) for i in self._dict.get_by_superstring(key, min_overlap)]

    def get_by_any_superstring(self, superstrings: List[Optional[str]], min_overlap: int = 0) -> Any:
        return [(i[0], self._lookup(i[1])) for i in self._dict.get_by_any_superstring(superstrings, min_overlap)]

    def get_by_any_superstring_vectorized(self, superstrings: List[List[Optional[str]]], min_length: int = 0):
        return [[(j[0], self._lookup(j[1])) for j in i] for i in self._dict.get_by_any_superstring_vectorized(superstrings, min_length)]

    def get_by_any_superstring_with_score(self, superstrings: List[Optional[str]], min_overlap: int = 0) -> Any:
        return [(i[0], self._lookup(i[1]), i[2]) for i in self._dict.get_by_any_superstring_with_score(superstrings, min_overlap)]

    def get_by_any_superstring_vectorized_with_score(self, superstrings: List[List[Optional[str]]], min_length: int = 0):
        return [[(j[0], self._lookup(j[1]), j[2]) for j in i] for i in self._dict.get_by_any_superstring_vectorized_with_score(superstrings, min_length)]

    def get_by_superstring_vectorized(self, keys: List[Optional[str]], min_overlap: int = 0) -> Any:
        return [[(j[0], self._lookup(j[1])) for j in i] for i in self._dict.get_by_superstring_vectorized(keys, min_overlap)]

    def finalize(self):
        self._dict.finalize()

    def get_by_any_prefix_vectorized(self, prefix: List[List[Optional[str]]], length_diff: int, min_length: int = 0):
        return [[(j[0], self._lookup(j[1])) for j in i] for i in self._dict.get_by_any_prefix_vectorized(prefix, length_diff, min_length)]

    def as_bytes(self):
        d = BytesIO()
        pickle.dump((self.__lookup, self._counter, bytes(self._dict.as_bytes())), d)
        return d.getvalue()

    @staticmethod
    def from_bytes(bytes):
        lookup, counter, dict_data = pickle.load(BytesIO(bytes))
        dict = StringAnalysisDict()
        dict._counter = counter
        dict.__lookup = lookup
        dict._dict = stringanalysisdict_from_bytes(dict_data)
        return dict


def stringanalysisdict(**kwargs: Any) -> StringAnalysisDict:
    d = StringAnalysisDict()
    for k, v in kwargs.items():
        d.insert(k, v)
    return d


class StringAnalysisDefaultDict:
    def __init__(self, default, **kwargs):
        self.dict = stringanalysisdict(**kwargs)
        self.default = default

    def get(self, k):
        out = self.dict.get(k)
        if out is None:
            out = self.default()
            self.dict.insert(k, out)
        return out

    def get_by_prefix(self, key, length_diff):
        return self.dict.get_by_prefix(key, length_diff)

    def get_by_superstring(self, key):
        return self.dict.get_by_superstring(key)

    def insert(self, k, v):
        self.dict.insert(k, v)

    def keys(self):
        return self.dict.keys()


def stringanalysisdefaultdict(default, **kwargs):
    return StringAnalysisDefaultDict(default, **kwargs)
