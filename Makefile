AWS_ACCOUNT_NAME ?= michael
AWS_DEFAULT_REGION ?= eu-west-1
PYTHON ?= python3
BEHAVE ?= behave
KEYFILE ?=.anslk_random_testkey

LIBFILES := $(shell find backup_cloud_ssm -name '*.py')

test: develop
	behave --tags ~@future

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
