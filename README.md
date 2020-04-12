rand
====

Random generated String from regex pattern.

WARNING
-------

The library **rand** is still in working-in-progress. It is subject to high possibility of API changes. Would appreciate for feedbacks, suggestions or helps.

Install
-------

Use pip or clone this repository and execute the setup.py file.

```shell script
$ pip install rand
```

Usages
------

```python
# import module
from rand import Rand

# initialise object
rand = Rand()

# generate pattern literal
rand.gen('koro') # ['koro']
rand.gen('28') # ['28']
rand.gen('a-z') # ['a-z']

# generate pattern any
rand.gen('.') # any char in string.printable

# generate pattern branch
rand.gen('ko|ro') # either ['ko'] or ['ro']
rand.gen('ko|ro|ro') # either ['ko'] or ['ro']

# generate pattern in
rand.gen('[kororo]') # either ['k'] or ['o'] or ['r']
rand.gen('k[o]r[o]r[o]') # ['kororo']

# generate pattern repeat
rand.gen('r{2,8}') # char r in length between 2 to 8 times

# generate pattern range
rand.gen('[a-z]') # char between a to z

# generate pattern subpattern
rand.gen('(ro)') # ['ro']

# use built-in providers
rand.gen('(:en_vocal:)') # char either a, i, u, e, o
```

Providers
---------

The library **rand** at core only provide random generator based on regex. Providers are built to allow extensions for rand.
Below is sample code how to integrate existing class definition (TestProxy) to Rand.

```python
from rand import Rand
from rand.providers.base import RandProxyBaseProvider

# class definition
class TestProxy:
    # simple function definition to return args values
    def target(self, arg1='def1', arg2='def2'):
        return '%s-%s' % (arg1, arg2)

# init rand class
rand = Rand()

# create proxy provider helper and register to rand
test_proxy = RandProxyBaseProvider(prefix='test', target=TestProxy())
rand.register_provider(test_proxy)

# test
print(rand.gen('(:test_target:)')) # ['def1-def2']
print(rand.gen('(:test_target:)', ['ok1'])) # ['ok1-def2']
print(rand.gen('(:test_target:)', ['ok1', 'ok2'])) # ['ok1-def2']
print(rand.gen('(:test_target:)', [['ok1', 'ok2']])) # ['ok1-ok2']
print(rand.gen('(:test_target:)', [['ok1', 'ok2'], 'ok3'])) # ['ok1-ok2']
print(rand.gen('(:test_target:)', [{'arg1': 'ok1'}])) # ['ok1-def2']
print(rand.gen('(:test_target:)', [{'arg1': 'ok1', 'arg2': 'ok2'}])) # ['ok1-ok2']
```

The library *rand* also has integration with existing projects such as Faker. Ensure you have faker library installed.

```python
from rand import Rand


rand = Rand()
rand.gen('(:faker_hexify:)') # abc
```

Test
----

Run test by installing packages and run tox

```shell script
$ pip install poetry tox
$ tox
```

For hot-reload development coding
```shell script
$ npm i -g nodemon
$ nodemon -w rand --exec python -c "from rand import Rand"
```

