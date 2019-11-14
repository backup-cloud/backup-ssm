fixed_key = "/backup_cloud_aws_ssm_test/test_key"
from hypothesis import given, settings, example
import hypothesis.strategies as strategies
from backup_cloud_ssm.aws_ssm_dict import aws_ssm_dict
from moto import mock_ssm
from os import environ as env
import pytest
from time import sleep
from warnings import warn


def identity(ob):
    return ob


if env.get("MOCK_AWS", "false") == "true":
    sometimes_mock_ssm = mock_ssm
else:
    sometimes_mock_ssm = identity

badkey_examples = ("", "/", None)


# this cannot be mocked via moto because moto accepts these keys!
@settings(deadline=10000)
@given(strategies.sampled_from(badkey_examples))
def test_bad_key_raises_exception(key):
    ssm_dict = aws_ssm_dict()
    exception_thrown = False
    try:
        ssm_dict[key] = "the_value"
    except AttributeError:
        exception_thrown = True
    assert exception_thrown, "key: " + key + " failed to throw expected assertion"


def store_restore_key(ssm_dict, key, value):
    try:
        del ssm_dict[key]
    except KeyError:
        pass

    ssm_dict[fixed_key] = value
    return ssm_dict[fixed_key]


def store_key_with_types(ssm_dict, key, value, type_name, description):
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


@sometimes_mock_ssm
@settings(deadline=10000)
@given(strategies.text(min_size=1, max_size=400))
def test_store_returns_input(value):
    ssm_dict = aws_ssm_dict()
    assert store_restore_key(ssm_dict, fixed_key, value) == value


type_names = ("SecureString", "String", "StringList")

# this test can be flaky, certainly in the time to run safely to the
# extent we should almost set deadline=None ; still it's the key
# function so we leave it in and keep increasing the time and retrys


@pytest.mark.wip
@sometimes_mock_ssm
@settings(deadline=100000)
@given(
    strategies.text(min_size=1, max_size=400),
    strategies.sampled_from(type_names),
    strategies.text(min_size=0, max_size=400),
)
@example(value="0", type_name="SecureString", description="0")
@example(value="0", type_name="SecureString", description="")
def test_store_returns_input_with_type(value, type_name, description):
    ssm_dict = aws_ssm_dict(return_type="dict")
    store_key_with_types(ssm_dict, fixed_key, value, type_name, description)
    max_retries = 10
    count = 0
    sleep_secs = 300 / 1000
    sleep_mult = 1.4
    while True:
        if count > max_retries:
            raise Exception(
                "Too many retries: description mismatch - probably update is broken"
            )
        returned_param = ssm_dict[fixed_key]
        if returned_param["description"] != description:
            warn("description mismatch - sleep and try again")
            sleep(sleep_secs)
            count += 1
            sleep_secs = sleep_secs * sleep_mult
        else:
            break

    assert isinstance(returned_param, dict)
    assert (
        returned_param["value"] == value
        and returned_param["type"] == type_name
        and returned_param["description"] == description
    ), "return parameter mismatch"


def test_empty_string_is_stored_as_none_and_returned_as_empty():
    value = "empty desc demo"
    type_name = "SecureString"
    description = ""
    ssm_dict = aws_ssm_dict(return_type="dict")
    try:
        del ssm_dict[fixed_key]
    except KeyError:
        pass

    ssm_dict[fixed_key] = (type_name, value, "")

    returned_param = ssm_dict[fixed_key]
    assert isinstance(returned_param, dict)
    assert (
        returned_param["value"] == value
        and returned_param["type"] == type_name
        and returned_param["description"] == description
    ), "return parameter mismatch"


def test_true():
    return True
