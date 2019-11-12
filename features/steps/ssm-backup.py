from hamcrest import assert_that, instance_of
from backup_cloud_ssm import backup_aws_ssm
from tempfile import NamedTemporaryFile
from behave import given, when, then
from subprocess import run, CalledProcessError


@given(u"I have some parameters in SSM parameter store")
def step_impl_1(context):
    context.ssm_dict.verify_dictionary(context.test_params)


@given(u"that I have backed up those parmameters")
def step_impl_2(context):
    t = context.backup_temp_file = NamedTemporaryFile()
    backup_aws_ssm.backup_to_file(t.name)


@given(u"I run the aws-ssm-backup command")
def step_impl_6(context):
    call_args = ["aws-ssm-backup"]
    try:
        proc_res = run(call_args, capture_output=True, check=True)
        context.backup_contents = proc_res.stdout
    except CalledProcessError as e:
        print("Failed backup stderr:", e.stderr, "stdout:", e.stdout)
        raise


@when(u"I delete those parameters from SSM parameter store")
def step_impl_3(context):
    context.ssm_dict.remove_dictionary(context.test_params)
    context.ssm_dict.verify_deleted_dictionary(context.test_params)


@when(u"I restore those parameters")
def step_impl_4(context):
    backup_aws_ssm.restore_from_file(context.backup_temp_file.name)


@when(u"I run the aws-ssm-backup command with the restore argument")
def step_impl_7(context):
    call_args = ["aws-ssm-backup", "--restore"]
    try:
        context.restore_res = run(
            call_args, capture_output=True, input=context.backup_contents, check=True
        )
    except CalledProcessError as e:
        print("Failed backup stderr:", e.stderr, "stdout:", e.stdout)
        raise


@then(u"those parameters should be in SSM parameter store")
def step_impl_5(context):
    context.ssm_dict.verify_dictionary(context.test_params)


@then(u"the types of those parameters should be preserved")
def step_impl(context):
    test_params = context.test_params
    for i in test_params.keys():
        assert_that(test_params[i], instance_of(dict))
    context.ssm_dict.verify_dictionary(context.test_params)
