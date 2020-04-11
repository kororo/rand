rand
====

Random generated String from regex pattern

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
