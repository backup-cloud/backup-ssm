AWS_ACCOUNT_NAME ?= michael
AWS_DEFAULT_REGION ?= eu-west-1
PYTHON ?= python3
BEHAVE ?= behave
KEYFILE ?=.anslk_random_testkey

LIBFILES := $(shell find backup_cloud_ssm -name '*.py')

all: lint test

# pytest-mocked is much faster than non-mocked which is slower even than
# the functional tests so run it first, then behave then ffinally the
# full pytest tests so that failures are detected early where possible.
test: develop pytest-mocked behave pytest 

behave:
	behave --tags ~@future

pytest-mocked:
	MOCK_AWS=true pytest

pytest:
	pytest

wip: develop
	behave --wip

lint:
	pre-commit install --install-hooks
	pre-commit run -a


# develop is needed to install scripts that are called during testing 
develop: .develop.makestamp

.develop.makestamp: setup.py backup_cloud_ssm/aws_ssm_cli.py $(LIBFILES)
	$(PYTHON) setup.py install --force
	$(PYTHON) setup.py develop
	touch $@

.PHONY: all test behave pytest-mocked pytest wip lint develop
