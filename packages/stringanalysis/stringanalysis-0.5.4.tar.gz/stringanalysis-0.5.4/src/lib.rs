use std::collections::{BTreeMap, HashMap, HashSet};
use pyo3::prelude::*;
use pyo3::{exceptions, PyObjectProtocol};
use fst::{IntoStreamer, Set, SetBuilder};
use fst::automaton::Levenshtein;
use rayon::prelude::*;
use regex::{Regex};
use std::cmp::Reverse;
use pyo3::types::{PyType, PyBytes};
use itertools::Itertools;
use std::error::Error;
use std::fmt;
use strsim::normalized_damerau_levenshtein;
use serde::{Serialize, Deserialize, Serializer};


#[macro_use]
extern crate itertools;


trait CharTrigrams {
    fn char_quadgrams(&self) -> Vec<&str>;
    fn char_trigrams(&self) -> Vec<&str>;
    fn without_first(&self, i: usize) -> &str;
}

impl CharTrigrams for &str {
    fn char_quadgrams(&self) -> Vec<&str> {
        let indices: Vec<usize> = self.char_indices().map(|(i, _)| i).collect();

        if indices.len() < 4 {
            return vec![self];
        }
        let mut t = vec![];
        for (start, end) in indices[..indices.len() - 3].iter().zip(indices[4..].iter().chain(vec![self.len()].iter())) {
            t.push(&self[*start..*end])
        }
        t
    }

    fn char_trigrams(&self) -> Vec<&str> {
        let indices: Vec<usize> = self.char_indices().map(|(i, _)| i).collect();

        if indices.len() < 3 {
            return vec![self];
        }
        let mut t = vec![];
        for (start, end) in indices[..indices.len() - 2].iter().zip(indices[2..].iter()) {
            t.push(&self[*start..*end])
        }
        t
    }

    fn without_first(&self, i: usize) -> &str {
        let indices: Vec<usize> = self.char_indices().map(|(i, _)| i).collect();

        if let Some(index) = indices.get(i) {
            &self[*index..]
        } else {
            ""
        }
    }
}

trait ImperfectLookup<U: Copy> {
    fn get_by_superstring(&self, key: &str) -> Vec<(&str, U, u8)>;
    fn get_by_overlap(&self, key: &str, min_overlap: usize) -> Vec<(&str, U)>;
    fn get_by_prefix(&self, key: &str, length_diff: usize) -> Vec<(&str, U)>;
}

impl<U: Copy> ImperfectLookup<U> for BTreeMap<String, U> {
    fn get_by_superstring(&self, key: &str) -> Vec<(&str, U, u8)> {
        key.char_quadgrams().iter()
            .flat_map(|sub_key| {
                let sub_key_cloned = sub_key.to_string();
                self.range((*sub_key).to_owned()..)
                    .take_while(move |(k, _v)| k.starts_with(sub_key_cloned.as_str()))
                    .filter(|(k, _v)| key.contains(k.as_str()))
            })
            .unique_by(|(k, _)| k.as_str())
            .map(|(k, v)| (
                k.as_str(),
                v.clone(),
                (100.0 * normalized_damerau_levenshtein(k, key)) as u8
            ))
            .sorted_by_key(|(k, v, distance)| Reverse(distance.clone()))
            .collect()
    }

    fn get_by_prefix(&self, key: &str, length_diff: usize) -> Vec<(&str, U)> {
        self
            .range(key.to_owned()..)
            .take_while(|(k, _v)| k.starts_with(key))
            .filter(|(k, _v)| k.len() == key.len() + length_diff)
            .map(|(k, v)| (k.as_str(), v.clone()))
            .collect()
    }

    fn get_by_overlap(&self, key: &str, min_overlap: usize) -> Vec<(&str, U)> {
        key
            .char_quadgrams().iter().enumerate()
            .filter(|(index, _sub_key)| key.len() - *index >= min_overlap)
            .flat_map(|(index, sub_key)| {
                let sub_key_cloned = sub_key.to_string();
                self.range((*sub_key).to_owned()..)
                    .take_while(move |(k, _v)| k.starts_with(sub_key_cloned.as_str()))
                    .filter(move |(k, _v)| k.starts_with(key.without_first(index)))
            })
            .unique_by(|(k, _)| k.as_str())
            .map(|(k, v)| (k.as_str(), v.clone()))
            .collect()
    }
}

#[pyclass]
struct StringAnalysisDict {
    map: BTreeMap<String, usize>,
    fst: Option<Set<Vec<u8>>>,
    fst_data: Option<Vec<u8>>,
}

impl StringAnalysisDict {
    fn new() -> Self {
        StringAnalysisDict {
            map: Default::default(),
            fst: Default::default(),
            fst_data: Default::default(),
        }
    }
}

fn err<S: ToString>(message: S) -> PyErr {
    exceptions::PyTypeError::new_err(message.to_string())
}

struct FuzzyError {
    msg: String,
}

impl fmt::Display for FuzzyError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Fuzzy err {}", self.msg) // user-facing output
    }
}

impl fmt::Debug for FuzzyError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{{ msg: {}, file: {}, line: {} }}", self.msg, file!(), line!()) // programmer-facing output
    }
}

impl StringAnalysisDict {
    fn _get_fuzzy(&self, key: Option<&str>, distance: u32) -> Result<Vec<(String, usize)>, FuzzyError> {
        if let Some(key) = key {
            if let Some(map) = &self.fst {
                let lev = Levenshtein::new(key, distance).map_err(|e| FuzzyError { msg: "Could not create fst".to_string() })?;
                let keys = map.search(lev).into_stream().into_strs().map_err(|e| FuzzyError { msg: "Could not stream keys".to_string() })?;
                return Ok(keys.iter().filter_map(|k| self.get(Some(k)).map(|v| (k.to_string(), v))).collect());
            }
        }
        Ok(vec![])
    }

    fn _get_by_superstring(&self, k: Option<&str>, min_length: usize) -> Vec<(&str, usize, u8)> {
        if let Some(unwrapped) = k {
            if unwrapped.len() < min_length {
                return vec![];
            }
        }

        k.map(|k| self.map.get_by_superstring(k).into_iter().map(|(k, v, d)| (k, v.clone(), d)).collect()).unwrap_or(vec![])
    }
}

#[pymethods]
impl StringAnalysisDict {
    fn as_bytes(&self) -> PyResult<Vec<u8>> {
        Ok(bincode::serialize(&(&self.map, &self.fst_data)).map_err(|_e| err("could not serialize map"))?)
    }

    fn get(&self, k: Option<&str>) -> Option<usize> {
        k.and_then(|k| self.map.get(k).map(|i| i.clone()))
    }

    #[args(min_length = 0)]
    fn get_by_prefix(&self, k: Option<&str>, length_diff: usize, min_length: usize) -> Vec<(&str, usize)> {
        if let Some(unwrapped) = k {
            if unwrapped.len() < min_length {
                return vec![];
            }
        }

        k.map(|k| self.map.get_by_prefix(k, length_diff).into_iter().map(|(k, v)| (k, v.clone())).collect()).unwrap_or(vec![])
    }

    #[args(min_length = 0)]
    fn get_by_prefix_vectorized(&self, py: Python, kss: Vec<Option<&str>>, length_diff: usize, min_length: usize) -> Vec<Vec<(&str, usize)>> {
        py.allow_threads(move || kss.par_iter().map(|ks| self.get_by_prefix(ks.as_ref().map(|i| *i), length_diff, min_length)).collect())
    }

    #[args(min_length = 0)]
    fn get_by_any_prefix(&self, ks: Vec<Option<&str>>, length_diff: usize, min_length: usize) -> Vec<(&str, usize)> {
        ks.iter().flat_map(|k| self.get_by_prefix(k.as_ref().map(|i| *i), length_diff, min_length)).collect()
    }

    #[args(min_length = 0)]
    fn get_by_any_prefix_vectorized(&self, py: Python, kss: Vec<Vec<Option<&str>>>, length_diff: usize, min_length: usize) -> Vec<Vec<(&str, usize)>> {
        py.allow_threads(move || kss.iter().map(|ks| self.get_by_any_prefix(ks.to_vec(), length_diff, min_length)).collect())
    }

    #[args(min_overlap = 0)]
    fn get_by_overlap(&self, k: Option<&str>, min_overlap: usize) -> Vec<(&str, usize)> {
        k.map(|k| self.map.get_by_overlap(k, min_overlap)).unwrap_or(vec![])
    }

    #[args(min_overlap = 0)]
    fn get_by_overlap_vectorized(&self, py: Python, k: Vec<Option<&str>>, min_overlap: usize) -> Vec<Vec<(&str, usize)>> {
        py.allow_threads(move || k.par_iter().map(|ks| self.get_by_overlap(ks.as_ref().map(|i| *i), min_overlap)).collect())
    }

    #[args(min_length = 0)]
    fn get_by_superstring(&self, k: Option<&str>, min_length: usize) -> Vec<(&str, usize)> {
        self
            ._get_by_superstring(k, min_length)
            .iter()
            .map(|(k, v, d)| (*k, *v))
            .collect()
    }

    #[args(min_length = 0)]
    fn get_by_superstring_with_score(&self, k: Option<&str>, min_length: usize) -> Vec<(&str, usize, f64)> {
        self
            ._get_by_superstring(k, min_length)
            .iter()
            .map(|(k, v, d)| (*k, *v, (*d as f64) / 100.0))
            .collect()
    }

    #[args(min_length = 0)]
    fn get_by_superstring_vectorized(&self, py: Python, k: Vec<Option<&str>>, min_length: usize) -> Vec<Vec<(&str, usize)>> {
        py.allow_threads(move || k.par_iter().map(|ks| self.get_by_superstring(ks.as_ref().map(|i| *i), min_length)).collect())
    }

    #[args(min_length = 0)]
    fn get_by_superstring_with_score_vectorized(&self, py: Python, k: Vec<Option<&str>>, min_length: usize) -> Vec<Vec<(&str, usize, f64)>> {
        py.allow_threads(move || k.par_iter().map(|ks| self.get_by_superstring_with_score(ks.as_ref().map(|i| *i), min_length)).collect())
    }

    #[args(min_length = 0)]
    fn get_by_any_superstring(&self, ks: Vec<Option<&str>>, min_length: usize) -> Vec<(&str, usize)> {
        ks
            .iter()
            .flat_map(|k| {
                self._get_by_superstring(k.as_ref().map(|i| *i), min_length)
            })
            .sorted_by_key(|(k, v, d)| Reverse(d.clone()))
            .map(|(k, v, d)| (k, v))
            .unique_by(|(k, _)| *k)
            .collect()
    }

    #[args(min_length = 0)]
    fn get_by_any_superstring_vectorized(&self, py: Python, kss: Vec<Vec<Option<&str>>>, min_length: usize) -> Vec<Vec<(&str, usize)>> {
        py.allow_threads(move || kss.par_iter().map(|ks| {
            self.get_by_any_superstring(ks.to_vec(), min_length)
        }).collect())
    }

    #[args(min_length = 0)]
    fn get_by_any_superstring_with_score(&self, ks: Vec<Option<&str>>, min_length: usize) -> Vec<(&str, usize, f64)> {
        ks
            .iter()
            .flat_map(|k| {
                self._get_by_superstring(k.as_ref().map(|i| *i), min_length)
            })
            .sorted_by_key(|(k, v, d)| Reverse(d.clone()))
            .map(|(k, v, d)| (k, v, (d as f64) / 100.0))
            .unique_by(|(k, _, _)| *k)
            .collect()
    }

    #[args(min_length = 0)]
    fn get_by_any_superstring_vectorized_with_score(&self, py: Python, kss: Vec<Vec<Option<&str>>>, min_length: usize) -> Vec<Vec<(&str, usize, f64)>> {
        py.allow_threads(move || kss.par_iter().map(|ks| {
            self.get_by_any_superstring_with_score(ks.to_vec(), min_length)
        }).collect())
    }

    fn insert(&mut self, k: Option<&str>, v: usize) {
        if let Some(k) = k {
            self.map.insert(k.to_string(), v);
        }
    }

    fn insert_pairs(&mut self, pairs: Vec<(Option<&str>, usize)>) {
        for (k, v) in pairs {
            self.insert(k, v);
        }
    }

    fn insert_keys_and_values(&mut self, keys: Vec<Option<&str>>, values: Vec<usize>) {
        for (k, v) in keys.iter().zip(values) {
            self.insert(k.as_ref().map(|i| *i), v);
        }
    }

    fn keys(&self) -> Vec<String> {
        self.map.keys().map(|i| i.to_string()).collect()
    }

    fn finalize(&mut self) -> PyResult<()> {
        if self.fst.is_some() {
            return Ok(());
        }

        let mut data = vec![];
        let mut build = SetBuilder::new(&mut data).map_err(|_e| err("could not create SetBuilder"))?;
        for (k, v) in &self.map {
            build.insert(k.as_str()).map_err(|_e| err("could not insert into fst Set"))?;
        }
        build.finish().map_err(|_e| err("could not finish fst Set"))?;
        let fst = Set::new(data.clone()).map_err(|_e| err("could not create fst Set"))?;

        self.fst = Some(fst);
        self.fst_data = Some(data);

        Ok(())
    }

    fn get_fuzzy(&self, key: Option<&str>, distance: u32) -> PyResult<Vec<(String, usize)>> {
        self._get_fuzzy(key, distance).map_err(|e| err(format!("{:?}", e)))
    }

    fn get_fuzzy_vectorized(&self, py: Python, key: Vec<Option<&str>>, distance: u32) -> PyResult<Vec<Vec<(String, usize)>>> {
        py.allow_threads(move || key.par_iter().map(|ks| self._get_fuzzy(ks.as_ref().map(|i| *i), distance)).collect::<Result<_, _>>().map_err(|e| err(format!("{:?}", e).as_str())))
    }
}

fn _order_by_token_alignment_vectorized(truths: &Vec<Option<&str>>, vecs: &Vec<Vec<Option<&str>>>) -> Vec<Vec<usize>> {
    let re = Regex::new(r"[\s\-/(),+]+").unwrap();

    return truths.par_iter().zip(vecs.par_iter()).map(|(truth, options)| {
        if let Some(truth) = truth {
            let upper_tokens: Vec<String> = re.split(truth)
                .filter(|i| i.len() > 3)
                .map(|i| i.to_uppercase())
                .collect();
            let truth_tokens: Vec<&str> = upper_tokens.iter().map(|i| i.as_str()).collect();
            let mut sorted: Vec<_> = options.iter()
                .enumerate()
                .filter_map(|(index, option)| option.as_ref().map(|o| (index, o)))
                .map(|(index, o)| {
                    let upper = o.to_uppercase();
                    let c = re.split(&upper)
                        .filter(|i| i.len() > 3)
                        .filter(|i| truth_tokens.contains(i))
                        .count();
                    (index, o, c)
                })
                .filter(|(_, _, count)| *count > 0)
                .collect();
            sorted.sort_by_key(|(_, _, count)| Reverse(*count));

            sorted.iter().map(|(index, _, _)| *index).collect()
        } else {
            vec![]
        }
    }).collect();
}

fn _sort_list_of_lists<'a, T: Sync + Send>(list: Vec<Vec<(T, i32)>>) -> Vec<Vec<T>> {
    list.into_par_iter().map(|mut i| {
        i.sort_by_key(|(_, i)| Reverse(*i));
        i.into_iter().map(|(v, _)| v).collect()
    }).collect()
}

fn _regex_parts(examples: Vec<(&str, &str)>, percent_required: i32) -> Result<Option<(Vec<String>, Vec<i32>)>, Box<Error>> {
    let separators = vec!["\\.", "-", "/", "_", ""];
    let not_separators_regex = "[^\\.\\-._]+?";

    let specificity_1: Vec<(&str, u16)> = vec!["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "Q", "X", "Y", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        .iter()
        .filter(|i| (&examples).iter().all(|(actual, expected)| (*actual).contains(**i)))
        .map(|l| (*l, 100)).collect();
    let specificity_2: Vec<(&str, u16)> = vec!["\\d", "[A-Z]"].iter().map(|l| (*l, 10)).collect();
    let specificity_3: Vec<(&str, u16)> = vec!["\\d+", "[A-Z]+"].iter().map(|l| (*l, 1)).collect();
    let specificity_4: Vec<(&str, u16)> = vec![not_separators_regex, ""].iter().map(|l| (*l, 0)).collect();

    let all_seps: Vec<_> = iproduct!(&separators, &separators).map(|(a, b)| (*a, *b)).collect();

    let all: Vec<&(&str, u16)> = specificity_1.iter()
        .chain(specificity_2.iter())
        .chain(specificity_3.iter())
        .chain(specificity_4.iter())
        .collect();

//    let sets: Result<Vec<_>, _> = iproduct!(&all, &all, &all, &all_seps)
//        .filter(|(p0, p1, p2, _)| p0.1 + p1.1 + p2.1 < 220)
//        .map(|(p0, p1, p2, (sep1, sep2))| format!("^({})({})({})({})({})$", p0.0, sep1, p1.0, sep2, p2.0))
//        .chunks(100)
//        .into_iter()
//        .map(|s| RegexSet::new(s))
//        .collect();
//    let sets = sets?;

    let best = iproduct!(&all, &all, &all, all_seps)
        .filter(|(p0, p1, p2, _)| p0.1 + p1.1 + p2.1 < 220)
        .par_bridge()
        .map(|(p0, p1, p2, (sep1, sep2))| {
            let re = Regex::new(format!("^({})({})({})({})({})$", p0.0, sep1, p1.0, sep2, p2.0).as_str()).unwrap();
            let parts = (p0.0, p1.0, p2.0);
            let score = p0.1 + p1.1 + p2.1;
            (re, parts, score, sep1, sep2)
        })
        .filter_map(move |(re, parts, score, sep1, sep2)| {
            vec![
                vec![1usize, 2usize, 3usize],
                vec![1usize, 2usize, 4usize],
                vec![1usize, 2usize, 5usize],
                vec![1usize, 2usize, 3usize, 4usize],
                vec![1usize, 2usize, 3usize, 5usize]
            ]
                .iter()
                .find(|indices| {
                    examples
                        .iter()
                        .filter(|(actual, expected)| {
                            let all_groups = re.captures_iter(actual).collect::<Vec<_>>();
                            if let Some(groups) = all_groups.get(0) {
                                let non_blank_groups: Vec<_> = groups.iter().filter_map(|g| g).map(|i| i.as_str()).filter(|g| !g.is_empty()).collect();
                                let transformed = indices.iter().filter_map(|i| non_blank_groups.get(*i)).join("");
                                &transformed.as_str() == expected
                            } else {
                                false
                            }
                        })
                        .count() >= (examples.len() as f32 * (0.01 * percent_required as f32)) as usize
                })
                .map(|indices| {
                    (parts, score, sep1, sep2, indices.to_vec())
                })
        })
        .reduce(
            || (Default::default(), Default::default(), Default::default(), Default::default(), vec![]),
            |a, b| if a.1 > b.1 { a } else { b },
        );

    if best.1 == 0 {
        return Ok(None);
    }

    let mut results: Vec<String> = vec![(best.0).0.to_string()];
    if best.2 != "" {
        results.push(best.2.to_string());
    }
    results.push((best.0).1.to_string());
    if best.3 != "" {
        results.push(best.3.to_string());
    }
    results.push((best.0).2.to_string());
    Ok(Some((results, best.4.iter().map(|i| (*i) as i32).collect())))
}

#[pymodule]
fn stringanalysis(_py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn(m, "stringanalysisdict")]
    fn stringanalysisdict(_py: Python) -> PyResult<StringAnalysisDict> {
        Ok(StringAnalysisDict::new())
    }

    #[pyfn(m, "stringanalysisdict_from_bytes")]
    fn stringanalysisdict_from_bytes(_py: Python, bytes: &[u8]) -> PyResult<StringAnalysisDict> {
        let deserialized: (BTreeMap<String, usize>, Option<Vec<u8>>) = bincode::deserialize(bytes).map_err(|_e| err("could not deserialize map"))?;
        Ok(StringAnalysisDict {
            map: deserialized.0,
            fst: deserialized.1.as_ref().map(|i| Set::new(i.to_vec()).map_err(|_e| err("could not create fst Set"))).transpose()?,
            fst_data: deserialized.1.as_ref().map(|i| i.to_vec()),
        })
    }

    #[pyfn(m, "order_by_token_alignment_vectorized")]
    fn order_by_token_alignment_vectorized(py: Python, truths: Vec<Option<&str>>, vecs: Vec<Vec<Option<&str>>>) -> Vec<Vec<usize>> {
        py.allow_threads(move || {
            _order_by_token_alignment_vectorized(&truths, &vecs)
        })
    }

    #[pyfn(m, "sort_list_of_lists")]
    fn sort_list_of_list<'a>(py: Python, list: Vec<Vec<(&'a PyAny, i32)>>) -> Vec<Vec<&'a PyAny>> {
        let indexes = list.iter().map(|i| {
            i.iter().enumerate().map(|(index, value)| {
                (index, value.1)
            }).collect()
        }).collect();

        let orderings = py.allow_threads(move || {
            _sort_list_of_lists(indexes)
        });

        list.into_iter()
            .zip(orderings)
            .map(|(v, order)| {
                order.into_iter().map(|i| v.get(i).unwrap().0).collect()
            })
            .collect()
    }

    #[pyfn(m, "regex_parts")]
    fn regex_parts<'a>(py: Python, examples: Vec<(&str, &str)>, percent_required: i32) -> PyResult<Option<(Vec<String>, Vec<i32>)>> {
        py.allow_threads(move || {
            _regex_parts(examples, percent_required).map_err(|e| exceptions::PyValueError::new_err(format!("{:?}", e)))
        })
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use crate::CharTrigrams;

    #[test]
    fn gets_quadgrams() {
        assert_eq!("abcde".char_quadgrams(), vec!["abcd", "bcde"])
    }

    #[test]
    fn gets_quadgrams_for_fancy_string() {
        assert_eq!("AS74229ÿÿÿ".char_quadgrams().len(), 7)
    }
}