from backup_cloud import backup_aws_ssm
from tempfile import NamedTemporaryFile
from behave import given, when, then


@given(u"that I have some parameters in SSM parameter store")
def step_impl_1(context):
    context.ssm_dict.verify_dictionary(context.test_params)


@given(u"that I have backed up those parmameters")
def step_impl_2(context):
    t = context.backup_temp_file = NamedTemporaryFile()
    backup_aws_ssm.backup_to_file(t.name)


@when(u"I delete those parameters from SSM parameter store")
def step_impl_3(context):
    context.ssm_dict.remove_dictionary(context.test_params)
    context.ssm_dict.verify_deleted_dictionary(context.test_params)


@when(u"I run my restore script")
def step_impl_4(context):
    backup_aws_ssm.restore_from_file(context.backup_temp_file.name)


@then(u"those parameters should be in SSM parameter store")
def step_impl_5(context):
    context.ssm_dict.verify_dictionary(context.test_params)
