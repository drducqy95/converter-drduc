.PHONY: install test coverage desktop-build verify clean

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

coverage:
	python -m pytest --cov=src --cov-report=term-missing --cov-report=xml

desktop-build:
	cd desktop && npm run build

verify: test desktop-build

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; shutil.rmtree('.pytest_cache', ignore_errors=True)"
