init:
	pip install -r requirements.txt

test:
	@python tests/test_*.py

install: init
	pip3 install -e .

.PHONY: init test
