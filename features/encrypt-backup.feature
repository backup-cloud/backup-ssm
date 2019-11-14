Feature: encrypt backups

In order to reduce the risk of leakage of credentials from SSM
parameter store Michael would like to use public key encryption from
backup_cloud to ensure that backups are encrypted and protected but can be recovered when needed.


  Background: we have prepared to run encrypted backups
        Given I have access to an account for doing backups
          and I have a private public key pair
          and the public key from that key pair is stored in an s3 bucket
          and I have configured my settings in SSM


  @future
  @wip
  Scenario: default encryption when ssm is backed up to S3
      Given I have some parameters in SSM parameter store
       When I run the aws-ssm-backup command 
       Then a backup object should be created in the S3 destination bucket
         and if I decrypt that file the content with the private key it should match the original
