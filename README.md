Backup SSM parameter store to a file.  Optional (but default)
encryption to be added.


## Using CLI tools

1) set up the appropriate environment including AWS variables

2) to backup run

   aws-ssm-backup > <filename>

3) to restore run

   aws-ssm-backup --restore > <filename>

## Using python interface

    import backup_aws_ssm
    backup_aws_ssm.backup_to_file("myfile")


    import backup_aws_ssm
    backup_aws_ssm.restore_from_file("myfile")


## Using python ssm library

Included in the package is a library which provides a dict object
which accesses SSM parameter store.  This will likely, later, be split out into a separate packge.  In the meantime it can be used in Alpha testing mode.

      from backup_cloud_ssm.aws_ssm_dict import aws_ssm_dict
      ssm_dict = aws_ssm_dict()
      ssm_dict["parameter"] = "value"
      print(ssm_dict["parameter"])
      

SSM parameter store treats storing no description and storing the
empty description ("") as the same thing and will not return any
description.  For simplicity we have now chosen to represent this as
the empty string.  This decision may change in future and feedback is
appreciated.

When parameters are deleted the parameter description sometimes seems
to persist for some time, possibly only when it was '0'.  Do not rely
on the deescription to be empty or ee testing/test_parameter_storage
for how to handle this.

## Development

We aim to use Behavior Driven Development to encourage reasonable feature descriptions and a level of tests appropriate for the business functionality included here.  Test Driven Development and to some extent Test Driven Design are encouraged in order to improve testability and eas of modification of the code.

Some of the tests are designed to run against either the Moto library or a real AWS instance.  By defining the variable:\

    We aim to use Behavior Driven Development to encourage reasonable feature descriptions and a level of tests appropriate for the business functionality included here.  Test Driven Development and to some extent Test Driven Design are encouraged in order to improve testability and eas of modification of the code.

Some of the tests are designed to run against either the Moto library or a real AWS instance.  By defining the shell variable MOCK_AWS as "true" all of the tests which can be run in mocked form will be.  

    export MOCK_AWS=true

This considerably speeds up testing but slightly increases risk since Moto's model of SSM is missing a number of features.  

## Defined functionality

See the features directory for the supported features of the software.  This is considered part of the documentation. 
