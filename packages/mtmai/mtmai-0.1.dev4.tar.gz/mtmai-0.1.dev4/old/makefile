


.PHONY: pip_publish
pip_publish:
	python -m build \
	&& twine check dist/* \
	&& twine upload -r dist/*
