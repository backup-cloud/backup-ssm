from behave import given, when, then


@given(u"I have access to an account for doing backups")
def step_impl_0(context):
    raise NotImplementedError(
        u"STEP: Given I have access to an account for doing backups"
    )


@given(u"I have a private public key pair")
def step_impl_1(context):
    raise NotImplementedError(u"STEP: Given I have a private public key pair")


@given(u"the public key from that key pair is stored in an s3 bucket")
def step_impl_2(context):
    raise NotImplementedError(
        u"STEP: Given the public key from that key pair is stored in an s3 bucket"
    )


@given(u"I have configured my settings in SSM")
def step_impl_3(context):
    raise NotImplementedError(u"STEP: Given I have configured my settings in SSM")


@when(u"I run the aws-ssm-backup command")
def step_impl_4(context):
    raise NotImplementedError(u"STEP: When I run the aws-ssm-backup command")


@then(u"a backup object should be created in the S3 destination bucket")
def step_impl_5(context):
    raise NotImplementedError(
        u"STEP: Then a backup object should be created in the S3 destination bucket"
    )


@then(
    u"if I decrypt that file the content with the private key it should match the original"
)
def step_impl_6(context):
    raise NotImplementedError(
        u"STEP: Then if I decrypt that file the content with the private key it should match the original"
    )
