.PHONY: bootstrap format lint typecheck test build check

bootstrap:
	@python3 --version

format:
	python3 scripts/contracts.py format

lint:
	python3 scripts/contracts.py validate

typecheck:
	python3 -m compileall -q -x '.*\._.*' scripts tests

test:
	python3 -m unittest discover -s tests

build:
	python3 scripts/contracts.py build

check: lint typecheck test build
