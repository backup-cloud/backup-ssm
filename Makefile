AWS_ACCOUNT_NAME ?= michael
AWS_DEFAULT_REGION ?= eu-west-1
PYTHON ?= python3
BEHAVE ?= behave

export AWS_DEFAULT_REGION

LIBFILES := $(shell find backup_cloud_ssm -name '*.py')

# we want to automate all the setup but we don't want to do it by surprise so we default
# to aborting with a message to correct things

## default rule to avoid installing software without warning
abort:
	@echo "***************************************************************************"
	@echo "* please run 'make all' to install library and programs locally then test *"
	@echo "***************************************************************************"
	@echo
	exit 2

## run all normal tasks to setup and verify
all: lint test

# pytest-mocked is much faster than non-mocked which is slower even than
# the functional tests so run it first, then behave then finally the
# full pytest tests so that failures are detected early where possible.
## standard tests
test: develop pytest-mocked behave pytest 

## behave tests only - excludes @future tagged tests to be used for planning
behave:
	behave --tags ~@future

## pytest based tests accellerated with AWS service mocking mostly
pytest-mocked:
	MOCK_AWS=true pytest

## pytest based tests only (unit or property testing)
pytest:
	pytest

## current behave work in progress test
wip: develop
	$(BEHAVE) --wip


## standard linting and reformatting
lint:
	pre-commit install --install-hooks
	pre-commit run -a

## remove python working files - does not unininstall results of develop
clean:
	python setup.py clean --all

## locally install scripts that are called during testing
develop: .develop.makestamp

# implementation of develop but using a file to record a timestamp
.develop.makestamp: setup.py backup_cloud_ssm/aws_ssm_cli.py $(LIBFILES)
	$(PYTHON) setup.py install --force
	$(PYTHON) setup.py develop
	touch $@

.PHONY: all test behave pytest-mocked pytest wip lint develop
