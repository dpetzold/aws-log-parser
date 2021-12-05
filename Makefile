.PHONY: build
build:
	python3 setup.py bdist_wheel

release: build
	python3 -m twine upload --repository aws-log-parser dist/*.whl
	rm -f dist/*
