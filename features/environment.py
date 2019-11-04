import random
import string
from behave import fixture
from behave.fixture import use_fixture_by_tag
from backup_cloud.aws_ssm_dict import aws_ssm_dict


@fixture
def setup_ssm_parameters(context):
    ssm_dict = context.ssm_dict = aws_ssm_dict()
    params = context.test_params = {
        "".join(
            [random.choice(string.ascii_letters + string.digits) for n in range(16)]
        ): "".join(
            [random.choice(string.ascii_letters + string.digits) for n in range(16)]
        ),
        "".join(
            [random.choice(string.ascii_letters + string.digits) for n in range(16)]
        ): "".join(
            [random.choice(string.ascii_letters + string.digits) for n in range(16)]
        ),
        "".join(
            [random.choice(string.ascii_letters + string.digits) for n in range(16)]
        ): "".join(
            [random.choice(string.ascii_letters + string.digits) for n in range(16)]
        ),
    }
    aws_ssm_dict.upload_dictionary(ssm_dict, params)
    yield (True)
    aws_ssm_dict.remove_dictionary(ssm_dict, params)
    aws_ssm_dict.verify_deleted_dictionary(ssm_dict, params)


# -- REGISTRY DATA SCHEMA 1: fixture_func
fixture_registry1 = {"fixture.ssm_params": setup_ssm_parameters}


def before_tag(context, tag):
    if tag.startswith("fixture."):
        return use_fixture_by_tag(tag, context, fixture_registry1)
