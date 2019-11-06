import boto3
from hamcrest import assert_that, equal_to
from typing import Dict, Tuple, Union
from collections.abc import MutableMapping


class aws_ssm_dict(MutableMapping):
    """provide a flat dictionary with access to AWS SSM parameters

    aws_ssm_dict provides a flat dictionary which allows access to AWS
    SSM parameters.  The key is the complete path to the parameter
    name, the value is the value of the parameter.

    When the dictionary is created it can either deliver the raw
    parmeter contents or it can decrypt them.  The default is to decryptb

    """

    def __init__(self, decrypt=True, return_type="value", region_name="eu-west-1"):
        self.ssm = boto3.client("ssm", region_name=region_name)
        self.decrypt = decrypt
        self.return_type = return_type

    def __setitem__(self, key: str, value: Union[str, Tuple]):
        """set the SSM parameter, to match a value

        given a string we use that by default as a securestring
        given a tuple we treat the first parameter as a type, the second as a value and optional third as a description
        """

        description = None
        if isinstance(value, tuple):
            param_type = value[0]
            val_string = value[1]
            try:
                description = value[2]
            except IndexError:
                pass
        else:
            param_type = "SecureString"
            val_string = value

        request_params = dict(Name=key, Type=param_type, Value=val_string)
        if description:
            request_params.update(dict(Description=description))

        self.ssm.put_parameter(**request_params)

    def __delitem__(self, key):
        request_params = dict(Name=key)
        self.ssm.delete_parameter(**request_params)

    def get_tuple_for_param(self, name):
        try:
            get_response = self.ssm.get_parameter(
                Name=name, WithDecryption=self.decrypt
            )
        except self.ssm.exceptions.ParameterNotFound as e:
            raise KeyError(e)
        try:
            describe_response = self.ssm.describe_parameter(Name=name)
        except self.ssm.exceptions.ParameterNotFound as e:
            raise KeyError(e)
        return (
            get_response["Parameter"]["Type"],
            get_response["Parameter"]["Value"],
            describe_response["Parameter"]["Description"],
        )

    def iterate_parameter_list(self):
        paginator = self.ssm.get_paginator("get_parameters_by_path")
        page_iterator = paginator.paginate(
            Path="/", Recursive=True, WithDecryption=True
        )
        for page in page_iterator:
            for i in page["Parameters"]:
                yield i

    def iterate_parameter_descriptions(self):
        paginator = self.ssm.get_paginator("describe_parameters")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            for i in page["Parameters"]:
                yield i["Name"]

    def iterate_for_tuples(self):
        for i in self.iterate_parameter_descriptions():
            name = i["Name"]
            yield (name, self.get_tuple_for_param(name))

    def iterate_for_values(self):
        for i in self.iterate_parameter_list():
            yield (i["Name"], i["Value"])

    def __iter__(self):
        yield from self.iterate_parameter_descriptions()

    def __len__(self):
        pass

    def _return_as_tuple(self, key: str):
        raise
        pass

    def _return_as_value(self, key: str):
        try:
            response = self.ssm.get_parameter(Name=key, WithDecryption=self.decrypt)
        except self.ssm.exceptions.ParameterNotFound as e:
            raise KeyError(e)
        assert response["Parameter"]["Name"] == key
        return response["Parameter"]["Value"]

    def __getitem__(self, key: str):
        if self.return_type == "tuple":
            return self._return_as_tuple(key)
        else:
            return self._return_as_value(key)

    def upload_dictionary(self, my_dict: Dict[str, str]):
        for i in my_dict.keys():
            self[i] = my_dict[i]

    def remove_dictionary(self, my_dict: Dict[str, str]):
        keys = [x for x in my_dict.keys()]
        for i in keys:
            self.pop(i, None)

    def verify_dictionary(self, my_dict: Dict[str, str]):
        for i in my_dict.keys():
            value = self[i]
            assert_that(value, equal_to(my_dict[i]))

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
