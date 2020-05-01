rand
====

[![Travis (.org)](https://img.shields.io/travis/kororo/rand)](https://pypi.python.org/project/rand/)
[![Coveralls github](https://img.shields.io/coveralls/github/kororo/rand)](https://pypi.python.org/project/rand/)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/rand.svg)](https://pypi.python.org/project/rand/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/rand)](https://pypi.python.org/project/rand/)

---

Random generated String from regex pattern

# WARNING

The library **rand** is still in working-in-progress. It is subject to high possibility of API changes. Would appreciate feedback, suggestions or help.

# Why?

There are lot of existing projects similar to **rand**, they are powerful and have similar goals and results. However most of them are old projects/non-maintained and non-MIT licenses.

This is a good opportunity for **rand** to be the library to help generate random data for any projects and gather all other existing libraries to be the main driver.


# Install

Use pip or clone this repository and execute the setup.py file.

```shell script
$ pip install rand
```

# Usages

Basic usage **rand** examples

```python
# import module
from rand import Rand

# initialise object
rnd = Rand()

# generate pattern literal
rnd.gen('koro') # ['koro']
rnd.gen('28') # ['28']
rnd.gen('a-z') # ['a-z']

# generate pattern any
rnd.gen('.') # any char in string.printable

# generate pattern branch
rnd.gen('ko|ro') # either ['ko'] or ['ro']
rnd.gen('ko|ro|ro') # either ['ko'] or ['ro']

# generate pattern in
rnd.gen('[kororo]') # either ['k'] or ['o'] or ['r']
rnd.gen('k[o]r[o]r[o]') # ['kororo']

# generate pattern repeat
rnd.gen('r{2,8}') # char r in length between 2 to 8 times

# generate pattern range
rnd.gen('[a-z]') # char between a to z

# generate pattern subpattern
rnd.gen('(ro)') # ['ro']
```

Providers
---------

The library **rand** at core only provide random generators based on regex. Providers are built to allow extensions for rand.

## Built-in Providers

There are a few built-in providers inside **rand**

### EN Provider

This library covers most usage around English requirements.

```python
from rand import Rand


rnd = Rand()
rnd.gen('(:en_vocal:)') # char either a, i, u, e, o
```

### Dataset Provider

This library helps on getting data from dataset such as Python object or Database with [peewee](https://github.com/coleifer/peewee).

```python
from rand import Rand
from rand.providers.ds import RandDatasetBaseProvider, ListDatasetTarget


# example using dict of list
db = {'names': ['test1', 'test1'], 'cities': ['test2', 'test2']}
ds = RandDatasetBaseProvider(prefix='ds', target=ListDatasetTarget(db=db))
rnd = Rand()
rnd.register_provider(ds)
rnd.gen('(:ds_get:)', ['names'])  # ['test1']
rnd.gen('(:ds_get:)', ['cities']) # ['test2']
# or, magic getattr
rnd.gen('(:ds_get_names:)-(:ds_get_cities:)') # ['test1-test2']

# example of database using peewee
from peewee import Proxy
from playhouse.sqlite_ext import CSqliteExtDatabase
from rand.providers.ds import RandDatasetBaseProvider, DBDatasetTarget
db = Proxy()
# ensure to have table with name "names", contains column at least (id, name)
db.initialize(CSqliteExtDatabase(':memory:', bloomfilter=True))
ds = RandDatasetBaseProvider(prefix='ds', target=DBDatasetTarget(db=db))
rnd = Rand()
rnd.register_provider(ds)
rnd.gen('(:ds_get:)', ['names']) # ['test']
db.close()
```

## Integration Providers

The library *rand* also has integration with existing projects such as Faker. Ensure you have faker library installed.

### [Faker](https://github.com/joke2k/faker)

There is super basic integration with Faker for now, soon will be more implemented.

```shell script
# ensure you have Faker installed
pip install Faker
```

```python
from rand import Rand


rnd = Rand()
rnd.gen('(:faker_hexify:)') # abc
```

## Custom Providers

Below is sample code on how to integrate an existing class definition (TestProxy) to Rand.

```python
from rand import Rand
from rand.providers.base import RandProxyBaseProvider

# class definition
class TestProxy:
    # simple function definition to return args values
    def target(self, arg1='def1', arg2='def2'):
        return '%s-%s' % (arg1, arg2)

# init rand class
rnd = Rand()

# create proxy provider helper and register to rand
test_proxy = RandProxyBaseProvider(prefix='test', target=TestProxy())
rnd.register_provider(test_proxy)

# test
print(rnd.gen('(:test_target:)')) # ['def1-def2']
print(rnd.gen('(:test_target:)', ['ok1'])) # ['ok1-def2']
print(rnd.gen('(:test_target:)', ['ok1', 'ok2'])) # ['ok1-def2']
print(rnd.gen('(:test_target:)', [['ok1', 'ok2']])) # ['ok1-ok2']
print(rnd.gen('(:test_target:)', [['ok1', 'ok2'], 'ok3'])) # ['ok1-ok2']
print(rnd.gen('(:test_target:)', [{'arg1': 'ok1'}])) # ['ok1-def2']
print(rnd.gen('(:test_target:)', [{'arg1': 'ok1', 'arg2': 'ok2'}])) # ['ok1-ok2']
```

# Test

Run test by installing packages and run tox

```shell script
$ pip install poetry tox
$ tox
$ tox -e py36 -- tests/test_ds.py
```

For hot-reload development coding
```shell script
$ npm i -g nodemon
$ nodemon -w rand --exec python -c "from rand import Rand"
```

# Help?

Any feedback, suggestions and integration with 3rd-party libraries can be added using PR or create issues if needed helps. 

# Similar Projects

List of projects similar to **rand**:
- [exrex](https://github.com/asciimoo/exrex): Irregular methods on regular expressions
- [xeger](https://github.com/crdoconnor/xeger): Library to generate random strings from regular expressions
- [strgen](https://github.com/paul-wolf/strgen): A Python module for a template language that generates randomized data

# Acknowdlge Projects

List of projects that **rand** depends on:
- [peewee](https://github.com/coleifer/peewee): a small, expressive orm -- supports postgresql, mysql and sqlite
- [pytest](https://github.com/pytest-dev/pytest/): The pytest framework makes it easy to write small tests, yet scales to support complex functional testing
- [coverage](https://github.com/nedbat/coveragepy): Code coverage measurement for Python
- [pytest-cov](https://github.com/pytest-dev/pytest-cov): Coverage plugin for pytest
