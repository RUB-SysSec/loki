flake8:
	flake8 --config=.flake8 sspam tests

pylint:
	pylint --rcfile=.pylintrc sspam tests

check:
	$(MAKE) flake8
	$(MAKE) pylint

test-quick:
	pytest -k 'not long'

test:
	pytest
