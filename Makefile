.PHONY: build
build:
	poetry build

.PHONY: release
release: build
	python3 -m twine upload --repository pypi dist/*.whl
	rm -f dist/*
