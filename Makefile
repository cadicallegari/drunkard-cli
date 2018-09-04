init:
	pip install -r requirements.txt

test:
	@python tests/*.py

.PHONY: init test
