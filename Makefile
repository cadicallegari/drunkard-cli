init:
	pip install -r requirements.txt

test:
	@python tests/*.py

install:
	pip3 install -e .

.PHONY: init test
