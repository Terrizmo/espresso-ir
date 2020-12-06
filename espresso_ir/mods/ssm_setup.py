#This with set up a SSM role and allow it to be added to the specified EC2 Instance.

import logging
import boto3
from botocore.exceptions import ClientError
import json


iam = boto3.resource('iam')
iamClient = boto3.client('iam')
ec2Client = boto3.client('ec2')
instance_profile = iam.InstanceProfile('name') #The InstanceProfile's name identifier. This must be set.


CaseId = ''
ec2_id = []
account_id = boto3.client('sts').get_caller_identity().get('Account')
instance_ID = ''
RoleName = 'EnablesEC2ToAccessSystemsManagerRole'

#This policy is to allow access to EC2 instances
PolicyDocument = {
    'Version': '2012-10-17',
    'Statement': {
        'Effect': 'Allow',
        'Principal': {
            'Service': 'ec2.amazonaws.com'
        },
        'Action': 'sts:AssumeRole'
    }
}

def create_role(CaseId):
    #This function creates a role that will attached to EC2 Instances to allow SSM to interact with the EC2 instance
    try:
        iam.create_role(
            AssumeRolePolicyDocument=json.dumps(PolicyDocument),
            Path='/',
            RoleName=RoleName,
            Description='Enables an EC2 instance to access Systems Manager',
            Tags=[
                {
                    'Key': 'CaseId',
                    'Value': CaseId
                },
            ]
        )
        print(f'Creating {RoleName} role!')
    except ClientError as e:
        logging.error(e)
        return False
    return True


def attach_role_policy():
    #This function attaches the required policies to the previous created role. 
    try:
        #This policy is what allows SSM to talk to the SSM agent on the EC2 instance
        iamClient.attach_role_policy(
            RoleName=RoleName,
            PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
        )
        print(f'Attaching AmazonSSMManagedInstanceCore role polcy to {RoleName} role!')
        
        #This policy allows access to S3 buckets.
        iamClient.attach_role_policy(
            RoleName=RoleName,
            PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
        )
        print(
            f'Attaching Instance Profile role polcy to {RoleName} role!')

        instance_profile.add_role(
            RoleName=RoleName,
            InstanceProfileName=RoleName
        )

    except ClientError as e:
        logging.error(e)
        return False
    return True

def add_role_to_ec2(instance_id):
    #This function adds the RoleName role to the specified EC2 instances 
    try:
        for instance_ID in instance_id:
            ec2Client.associate_iam_instance_profile(
                IamInstanceProfile={
                    'Arn': 'arn:aws:iam::' + account_id + ':instance-profile/' + RoleName,
                    'Name': RoleName
                },
                InstanceId=instance_ID
            )
            print(f'Adding AmazonSSMManagedInstanceCore role to {instance_ID} EC2 Instance')
    except ClientError as e:
        logging.error(e)
        return False
    return True


def main():
    create_role(CaseId)
    attach_role_policy()
    add_role_to_ec2(instance_ID)
    """iamClient.create_instance_profile(
        InstanceProfileName=RoleName,
        Path='/'
    )"""
    

if __name__ == "__main__":
    main()
