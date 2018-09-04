init:
	pip install -r requirements.txt

test:
	@python tests/*.py

install: init
	pip3 install -e .

.PHONY: init test
