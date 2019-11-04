Feature: backup SSM parameter store
In order to ensure that I can recover my SSM parameters even

   @wip
   @fixture.ssm_params
   Scenario: backup SSM to a plaintext file
   Given that I have some parameters in SSM parameter store
   And that I have backed up those parmameters
   When I delete those parameters from SSM parameter store
   And I run my restore script
   Then those parameters should be in SSM parameter store
