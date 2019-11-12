fixed_key = "/backup_cloud_aws_ssm_test/test_key"
from hypothesis import given, settings
import hypothesis.strategies as strategies
from backup_cloud_ssm.aws_ssm_dict import aws_ssm_dict
from moto import mock_ssm
from os import environ as env
import pytest


def identity(ob):
    return ob


if env.get("MOCK_AWS", "false") == "true":
    sometimes_mock_ssm = mock_ssm
else:
    sometimes_mock_ssm = identity

badkey_examples = ("", "/", None)


# this cannot be mocked via moto because moto accepts these keys!
@given(strategies.sampled_from(badkey_examples))
def test_bad_key_raises_exception(key):
    ssm_dict = aws_ssm_dict()
    exception_thrown = False
    try:
        ssm_dict[key] = "the_value"
    except AttributeError:
        exception_thrown = True
    assert exception_thrown, "key: " + key + " failed to throw expected assertion"


def store_restore_key(ssm_dict, value):
    try:
        del ssm_dict[fixed_key]
    except KeyError:
        pass
    ssm_dict[fixed_key] = value
    return ssm_dict[fixed_key]


def store_restore_key_with_types(ssm_dict, value, type_name, description):
    assert ssm_dict.return_type == "dict"
    try:
        del ssm_dict[fixed_key]
    except KeyError:
        pass
    ssm_dict[fixed_key] = {
        "value": value,
        "type": type_name,
        "description": description,
    }
    return ssm_dict[fixed_key]


@sometimes_mock_ssm
@settings(deadline=3000)
@given(strategies.text(min_size=1, max_size=400))
def test_store_returns_input(value):
    ssm_dict = aws_ssm_dict()
    assert store_restore_key(ssm_dict, value) == value


type_names = ("SecureString", "String", "StringList")


@pytest.mark.wip
@sometimes_mock_ssm
@settings(deadline=3000)
@given(
    strategies.text(min_size=1, max_size=400),
    strategies.sampled_from(type_names),
    strategies.text(min_size=0, max_size=400),
)
def test_store_returns_input_with_type(value, type_name, description):
    ssm_dict = aws_ssm_dict(return_type="dict")
    returned_param = store_restore_key_with_types(
        ssm_dict, value, type_name, description
    )
    assert isinstance(returned_param, dict)
    assert (
        value == returned_param["value"]
        and type_name == returned_param["type"]
        and description == returned_param.get("description", "")
    ), "return parameter mismatch"


def test_true():
    return True
