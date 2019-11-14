from unittest.mock import MagicMock, patch
from backup_cloud_ssm.aws_ssm_dict import aws_ssm_dict


def test_get_parameter_as_dict_should_get_and_describe():
    value = "empty desc demo"
    type_name = "SecureString"
    description = "the description"
    ssm_mock = MagicMock()
    ssm_mock.get_parameter.return_value = {
        "Parameter": {"Name": "fakeparam", "Type": type_name, "Value": value}
    }
    ssm_mock.describe_parameters.return_value = {
        "Parameters": [
            {"Name": "fakeparam", "Type": "SecureString", "Description": description}
        ]
    }
    ssm_dict = aws_ssm_dict(ssm_client=ssm_mock, return_type="dict")
    returned_param = ssm_dict.get_param_as_dict("fakeparam")
    assert (
        returned_param["value"] == value
        and returned_param["type"] == type_name
        and returned_param["description"] == description
    ), "return parameter mismatch"
    ssm_mock.get_parameter.assert_called()
    ssm_mock.describe_parameters.assert_called()


def test_get_parameter_desc_should_retry_and_then_return():
    description = "the description"
    ssm_mock = MagicMock()
    ssm_mock.exceptions.ParameterNotFound = Exception
    ssm_mock.describe_parameters.side_effect = [
        {"Parameters": []},
        {"Parameters": []},
        {"Parameters": []},
        {"Parameters": []},
        {"Parameters": []},
        {"Parameters": []},
        {
            "Parameters": [
                {
                    "Name": "fakeparam",
                    "Type": "SecureString",
                    "Description": description,
                }
            ]
        },
    ]
    ssm_dict = aws_ssm_dict(ssm_client=ssm_mock, return_type="dict")

    def mock_sleep(time):
        pass

    with patch("backup_cloud_ssm.aws_ssm_dict.sleep"):
        returned_desc = ssm_dict.desc_param("fakeparam")
    assert returned_desc["Parameters"][0]["Name"] == "fakeparam"
    ssm_mock.describe_parameters.assert_called()
