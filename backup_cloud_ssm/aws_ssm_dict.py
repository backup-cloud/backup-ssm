import boto3
from hamcrest import assert_that, equal_to
from typing import Dict, Tuple, Union
from collections.abc import MutableMapping
from botocore.exceptions import ParamValidationError
from time import sleep
import logging


class aws_ssm_dict(MutableMapping):
    """provide a flat dictionary with access to AWS SSM parameters

    aws_ssm_dict provides a flat dictionary which allows access to AWS
    SSM parameters.  The key is the complete path to the parameter
    name, the value is the value of the parameter.

    When the dictionary is created it can either deliver the raw
    parmeter contents or it can decrypt them.  The default is to decryptb

    """

    def __init__(
        self, decrypt=True, return_type="value", region_name=None, ssm_client=None
    ):
        if ssm_client is None:
            if region_name is not None:
                self.ssm = boto3.client("ssm", region_name=region_name)
            else:
                self.ssm = boto3.client("ssm", region_name=region_name)
        else:
            self.ssm = ssm_client
        self.exceptions = self.ssm.exceptions
        self.decrypt = decrypt
        self.return_type = return_type

    def __setitem__(self, key: str, value: Union[str, Tuple]):
        """set the SSM parameter, to match a value

        given a string we use that by default as a securestring
        given a tuple we treat the first parameter as a type, the second as a value and optional third as a description
        """

        description = None
        if isinstance(value, dict):
            param_type = value["type"]
            val_string = value["value"]
            try:
                description = value["description"]
            except KeyError:
                description = None
        elif isinstance(value, tuple):
            param_type = value[0]
            val_string = value[1]
            try:
                description = value[2]
            except IndexError:
                description = None
        else:
            param_type = "SecureString"
            val_string = value

        request_params = dict(Name=key, Type=param_type, Value=val_string)
        if description is not None:
            request_params.update(dict(Description=description))
        try:
            self.ssm.put_parameter(**request_params)
        except (
            self.ssm.exceptions.ParameterNotFound,
            ParamValidationError,  # import from botocore.exceptions since ssm doesn't (currently?) export this
            self.ssm.exceptions.ParameterAlreadyExists,
        ) as e:
            raise AttributeError(e)
        except self.ssm.exceptions.ClientError as e:
            if "ValidationException" not in str(e):
                raise e
            raise AttributeError(e)

    def __delitem__(self, key, max_retries=15):
        """delete a parameter and wait for it to be deleted

        We send the delete_parameter call to AWS which requests
        parameter deletion.  Unfortunately it seems that this takes
        some time after the call returns to complete.  This means we
        means we wait to retry by default.
        """

        request_params = dict(Name=key)
        try:
            self.ssm.delete_parameter(**request_params)
        except self.ssm.exceptions.ParameterNotFound as e:
            raise KeyError(e)
        count = 0
        sleep_secs = 100 / 1000
        sleep_mult = 1.2
        while True:
            describe_response = self.ssm.describe_parameters(
                Filters=[{"Key": "Name", "Values": [key]}]
            )
            try:
                if "Description" not in describe_response["Parameters"][0]:
                    break
            except IndexError:
                break
            if count < max_retries:
                logging.debug("sleeping " + str(sleep_secs) + " to give ssm time")
                sleep(sleep_secs)
                count += 1
                sleep_secs = sleep_secs * sleep_mult
            else:
                raise Exception(
                    "Description failed to clear after delete - nasty AWS!!!"
                )

    def iterate_parameter_list(self):
        paginator = self.ssm.get_paginator("get_parameters_by_path")
        page_iterator = paginator.paginate(
            Path="/", Recursive=True, WithDecryption=True
        )
        for page in page_iterator:
            for i in page["Parameters"]:
                yield i

    def iterate_param_descs_for_names(self):
        paginator = self.ssm.get_paginator("describe_parameters")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            for i in page["Parameters"]:
                yield i["Name"]

    def iterate_for_tuples(self):
        for i in self.iterate_param_descs_for_names():
            name = i["Name"]
            yield (name, self.get_param_as_tuple(name))

    def iterate_for_values(self):
        for i in self.iterate_parameter_list():
            yield (i["Name"], i["Value"])

    def __iter__(self):
        yield from self.iterate_param_descs_for_names()

    def __len__(self):
        pass

    def get_param(self, key: str):
        try:
            response = self.ssm.get_parameter(Name=key, WithDecryption=self.decrypt)
        except self.ssm.exceptions.ParameterNotFound as e:
            raise KeyError(e)
        assert response["Parameter"]["Name"] == key
        return response

    def desc_param(self, key: str, max_retries=15):
        """get the description of a parameter we _know_ is there

        this tries to get the AWS parameter description from inside a
        describe_parameters response for a parameter with the
        parameter as the first (and only) parameter in the parameter
        list.  In the case that the initial call fails it retries
        (max_retries times) in case a parameter has been created but
        the data about it is not yet in sync.

        """

        """Note on code here:

        "Request results are returned on a best-effort basis."
        https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_DescribeParameters.html

        this means that even though we only want the first result, we
        still have to paginate through what may be a number of
        responses with empty parameter lists.
        """

        count = 0
        sleep_secs = 100 / 1000
        sleep_mult = 1.2
        while True:
            paginator = self.ssm.get_paginator("describe_parameters")
            page_iterator = paginator.paginate(
                Filters=[{"Key": "Name", "Values": [key]}]
            )
            param_pages = [page["Parameters"] for page in page_iterator]
            paramlist = [param for sublist in param_pages for param in sublist]
            if len(paramlist) == 0:
                if count > max_retries:
                    raise KeyError("description retry count exceeded - aborting")
                count += 1
                logging.debug(
                    "sleeping "
                    + str(sleep_secs)
                    + " to give ssm time to retrieve description"
                )
                sleep(sleep_secs)
                sleep_secs = sleep_secs * sleep_mult
            else:
                break
        assert len(paramlist) == 1
        assert paramlist[0]["Name"] == key
        return paramlist[0]

    def retrieve_description(self, key: str):
        parameter_describe = self.desc_param(key)
        try:
            description = parameter_describe["Description"]
        except KeyError:
            description = ""
        return description

    def get_param_as_dict(self, key: str):
        get_response = self.get_param(key)
        description = self.retrieve_description(key)

        retval = {
            "value": get_response["Parameter"]["Value"],
            "type": get_response["Parameter"]["Type"],
            "description": description,
        }
        return retval

    def get_param_as_tuple(self, key: str):
        get_response = self.ssm.get_parameter(Name=key, WithDecryption=self.decrypt)
        description = self.retrieve_description(key)
        return (
            get_response["Parameter"]["Type"],
            get_response["Parameter"]["Value"],
            description,
        )

    def get_param_as_value(self, key: str):
        response = self.get_param(key)
        return response["Parameter"]["Value"]

    def __getitem__(self, key: str):
        if self.return_type == "dict":
            return self.get_param_as_dict(key)
        elif self.return_type == "tuple":
            return self.get_param_as_tuple(key)
        elif self.return_type == "value":
            return self.get_param_as_value(key)
        raise Exception("unknown return type: " + self.return_type)

    def upload_dictionary(self, my_dict: Dict[str, str]):
        for i in my_dict.keys():
            self[i] = my_dict[i]

    def remove_dictionary(self, my_dict: Dict[str, str]):
        keys = [x for x in my_dict.keys()]
        for i in keys:
            self.pop(i, None)

    def verify_dictionary(self, my_dict: Dict[str, str]):
        for i in my_dict.keys():
            test_value = my_dict[i]
            if isinstance(test_value, dict):
                ssm_param = self.get_param_as_dict(i)
                assert_that(ssm_param["type"], equal_to(test_value["type"]))
                assert_that(ssm_param["value"], equal_to(test_value["value"]))
                assert_that(
                    ssm_param["description"], equal_to(test_value["description"])
                )
            if isinstance(test_value, str):
                assert_that(self.get_param_as_value(i), equal_to(test_value))

    def verify_deleted_dictionary(self, my_dict: Dict[str, str]):
        except_count = 0
        for i in my_dict.keys():
            try:
                self[i]
            except KeyError:
                except_count += 1
                continue
            assert False, "still found key: " + i + " in dictionary"
        assert except_count == len(my_dict.keys())
