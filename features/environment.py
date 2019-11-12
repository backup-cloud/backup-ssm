import random
import string
from behave import fixture
from behave.fixture import use_fixture_by_tag
from backup_cloud_ssm.aws_ssm_dict import aws_ssm_dict


def randomword(length=16):
    return "".join(
        [random.choice(string.ascii_letters + string.digits) for n in range(16)]
    )


def randomlist():
    return ",".join([randomword(4), randomword(4), randomword(4), randomword(4)])


def create_random_params(ssm_dict):
    params = {
        randomword(): randomword(),
        randomword(): randomword(),
        randomword(): randomword(),
    }
    ssm_dict.upload_dictionary(params)
    return params


def create_random_typed_params(ssm_dict):
    params = {
        randomword(): {
            "value": randomword(),
            "type": "String",
            "description": "aws-ssm-backup testing String parameter",
        },
        randomword(): {
            "value": randomword(),
            "type": "SecureString",
            "description": "aws-ssm-backup testing String parameter",
        },
        randomword(): {
            "value": randomlist(),
            "type": "StringList",
            "description": "aws-ssm-backup testing String parameter",
        },
    }
    ssm_dict.upload_dictionary(params)
    return params


@fixture
def setup_ssm_parameters(context):
    """parameters that will be deleted during the simulated disaster"""
    ssm_dict = context.ssm_dict = aws_ssm_dict()
    context.test_params = params = create_random_params(ssm_dict)
    yield (True)
    aws_ssm_dict.remove_dictionary(ssm_dict, params)
    aws_ssm_dict.verify_deleted_dictionary(ssm_dict, params)


@fixture
def setup_typed_ssm_parameters(context):
    """parameters that will be deleted during the simulated disaster"""
    ssm_dict = context.ssm_dict = aws_ssm_dict()
    context.test_params = params = create_random_typed_params(ssm_dict)
    yield (True)
    aws_ssm_dict.remove_dictionary(ssm_dict, params)
    aws_ssm_dict.verify_deleted_dictionary(ssm_dict, params)


@fixture
def preexisting_ssm_parameters(context):
    """\
    parameters that don't get deleted during disaster (or perhaps were
    recreated manually after disaster but before restore)
    """
    ssm_dict = context.ssm_dict = aws_ssm_dict()
    context.preexist_params = params = create_random_params(ssm_dict)
    yield (True)
    aws_ssm_dict.remove_dictionary(ssm_dict, params)
    aws_ssm_dict.verify_deleted_dictionary(ssm_dict, params)


# -- REGISTRY DATA SCHEMA 1: fixture_func
fixture_registry1 = {
    "fixture.ssm_params": setup_ssm_parameters,
    "fixture.ssm_typed_params": setup_typed_ssm_parameters,
    "fixture.preexist_params": preexisting_ssm_parameters,
}


def before_tag(context, tag):
    if tag.startswith("fixture."):
        return use_fixture_by_tag(tag, context, fixture_registry1)
