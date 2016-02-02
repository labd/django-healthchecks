.PHONY: test upload


test:
	py.test

upload:
	rm -rf dist/*
	python setup.py sdist bdist_wheel
	twine upload dist/*
