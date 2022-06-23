# Adapted from SSPAM

Only works with Python 3.6.9 or older -- Python 3.8 is too new and causes exceptions "no comparison function for constant" and similar.


sspam: Symbolic Simplification with PAttern Matching
====================================================

sspam is a software for simplifying mixed expressions (expressions
using both arithmetic and boolean operators) with pattern matching. It
uses sympy for arithmetic simplification, and z3 for *flexible*
matching (matching equivalent expressions with different
representations).


Requirements
------------
To use sspam, you need:

* The SMT solver [z3](https://github.com/Z3Prover/z3) version 4.4.2
* The Python library for symbolic mathematics [sympy](http://www.sympy.org/fr/index.html)
* The Python module for ast unparsing [astunparse](https://github.com/simonpercivall/astunparse)

To contribute to sspam, you need:

* The Python module for source checking [flake8] (https://pypi.python.org/pypi/flake8)
* The Python module for source checking [pylint] (https://www.pylint.org/)
* The Python framework for testing [pytest] (http://docs.pytest.org/en/latest/index.html)

Installation
------------

* You can install most requirements with `pip install -r requirements.txt` (or `pip install -r requirements-dev.txt` to contribute)

* To install z3, you can either:
 * Compile it from [source](https://github.com/Z3Prover/z3)
 * Or download a [release](https://github.com/Z3Prover/z3/releases) and
  add the `bin/` directory to your `$PYTHONPATH`

* To install SSPAM:

```
$ sudo python setup.py install
```

Using sspam
------------

You can use sspam either with the command line:

```
$ sspam "(x & y) + (x | y)"

(x + y)

```

Or in a python script:

```
from sspam import simplifier

print simplifier.simplify("(x & y) + (x | y)")
```

You'll see a few examples of utilisation of sspam in the examples/
directory.

Note that a `cse` module is provided in order to do *common
subexpression elimination* (avoid dealing with the same subexpressions
several times).


Tests
-----

To run tests of sspam please use `make test`


Contribute
----------

To contribute to sspam, create a branch with your contribution
(feature, fix...). Please use the command `make check` for some basic
checkings of your codestyle. As not all errors of pylint might be relevant,
you can use `#pylint: disable=` comments in your code to disable
irrelevant errors.

To check that your contribution does not affect normal behaviour of
sspam, please use `make test`.
