# String Analysis
This package contains a set of data structures and functions used to perform
fast analyses for comparing strings.

## Installation
To build, you will need to have rust nightly installed on your machine:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default nightly
```

Then you can install via pip:
```bash
pip install <path>/shsdict
```

## Usage
The [tests](stringanalysis/shsdict_test.py) are a great way to se how to use the different available methods, 
but a summary is as follows.

### Creation
```python
from stringanalysis.shsdict import shsdict

my_dict = shsdict()
```

### Insertion
```python
my_dict.insert('key', 'value')
my_dict.insert_pairs([('key1', 'value1'), ('key2', 'value2')])
my_dict.insert_keys_and_values(['key1', 'otherkey'], ['value1', 'value3'])
```

### Retrieval
```python
my_dict.get('key1') # => 'value1'

my_dict.get_by_prefix('key') # => ['value1', 'value2']
my_dict.get_by_any_prefix(['key', 'other']) # => ['value1', 'value2', 'value3']
my_dict.get_by_any_prefix_vectorized([['key'], ['other']]) # => [['value1', 'value2'], ['value3']]

my_dict.get_by_superstring('prefix_key1_suffix') # => ['value1']
my_dict.get_by_any_superstring(['prefix_key1_suffix', 'prefix_key2_suffix']) # => ['value1', 'value2']
my_dict.get_by_any_superstring_vectorized([['prefix_key1_suffix', 'prefix_key2_suffix'], ['a_otherkey_b']]) # => [['value1', 'value2'], ['value3']]

# Use of `get_fuzzy` requires a call to `finalize`, which indexes the data for the fuzzy search
my_dict.finalize()
my_dict.get_fuzzy('key5', 1) # => ['value1', 'value2']
```
A few things to keep in mind:
* `get_fuzzy` can typically only handle distances of `1` or `2`. Beyond that it will error as the search space is too large.
* The prefix getters and the superstring getters accept an additional argument to limit minimum string lengths to retrieve values. If a key is shorter than that value, the method will return either `None` or `[]`

## Debugging
If you're getting seg faults and want to debug, you need a debug build of python via something like:
```
CONFIGURE_OPTS=--enable-shared pyenv install 3.7.2 -g
``` 
Create a virtualenv using that python version. You can just update `.python-version` to be
```
3.7.2-debug
```
and make a new virtualenv.

In `test.sh` comment the `maturin develop` command and uncomment the command it says to uncomment for a debug build.

Then when you get a segfault you should also get a python stacktrace to see where the seg fault occurred.