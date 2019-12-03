Feature: backup SSM parameter store
In order to ensure that I can recover my SSM parameters even

   @fixture.preexist_params
   @fixture.ssm_params
   Scenario: backup SSM to a plaintext file
   Given I have some parameters in SSM parameter store
   And that I have backed up those parmameters
   When I delete those parameters from SSM parameter store
   And I restore those parameters
   Then those parameters should be in SSM parameter store

   @fixture.preexist_params
   @fixture.ssm_typed_params
   Scenario: backup SSM to a plaintext file
   Given I have some parameters in SSM parameter store
   And that I have backed up those parmameters
   When I delete those parameters from SSM parameter store
   And I restore those parameters
   Then those parameters should be in SSM parameter store
   And the types of those parameters should be preserved

   @fixture.preexist_params
   @fixture.ssm_params
   Scenario: provide backup from command line
   Given I have some parameters in SSM parameter store
   And I run the aws-ssm-backup command
   When I delete those parameters from SSM parameter store
   And I run the aws-ssm-backup command with the restore argument
   Then those parameters should be in SSM parameter store


   @future
   Scenario: only warn for preexisting parameters if there is a mismatch
   Given I have an existing parameter with the same value as in my backup
   And I have an existing parameter with the a differnt value from my backup
   When I run my restore without overwriting parameters
   Then I should get a debug message about the matching parameter
   And I should get a warning message about the other parameter
