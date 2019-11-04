test:
	behave

wip:
	behave --wip


lint:
	pre-commit install --install-hooks
	pre-commit run -a
