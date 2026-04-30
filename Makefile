.PHONY: install compile-dictionaries test coverage desktop-build verify clean

install:
	python -m pip install -e ".[dev]"

compile-dictionaries:
	python -m src.core.md_dictionary_compiler --dict-root data/dictionaries

test:
	python -m pytest

coverage:
	python -m pytest --cov=src --cov-report=term-missing --cov-report=xml

desktop-build:
	cd desktop && npm run build

verify: compile-dictionaries test desktop-build

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; shutil.rmtree('.pytest_cache', ignore_errors=True)"
