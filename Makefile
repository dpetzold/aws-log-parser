.PHONY: build
build:
	python3 -m build

release: build
	python3 -m twine upload --repository aws-log-parser dist/*
	rm -f dist/*
