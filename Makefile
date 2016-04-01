.PHONY: install test upload


install:
	pip install -e .[test]

test:
	py.test

release:
	rm -rf dist/*
	python setup.py sdist bdist_wheel
	twine upload dist/*
