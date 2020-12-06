import logging
import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime

ec2_client = boto3.client('ec2')
ec2 = boto3.resource('ec2')
vpc = ec2.Vpc('id')
iam = boto3.resource('iam')
iamClient = boto3.client('iam')

CaseId = ""
now = datetime.now()
time_now = now.strftime("%Y%b%d-%H:%M:%S")
RoleName = "Flow-Logs-Role"
VpcID = []
account_id = boto3.client('sts').get_caller_identity().get('Account')
InstanceId = ''

#This Trust policy allows the role to access the VPC Flow log service
TrustPolicy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": "vpc-flow-logs.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

#This policy grants permissions to send logs to CloudWatch and S3
RolePolicy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:CreateLogDelivery",
                "logs:DeleteLogDelivery"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}

def get_vpc_id(InstanceIds):
    """
    This function returns the VPC ID for the given instatnce ID.
    """
    try:
        for InstanceId in InstanceIds:
            instance = ec2.Instance(InstanceId)
            global VpcID
            VpcID.append(instance.vpc.id)
        return VpcID

    except ClientError as e:
        logging.error(e)
        return False
    return True


def create_role(CaseId):
    """
    This function creates a role that will allow flow logs to CloudWatch
    """
    try:
        iam.create_role(
            AssumeRolePolicyDocument=json.dumps(TrustPolicy),
            Path='/',
            RoleName=RoleName,
            Description='IAM role for publishing flow logs to CloudWatch',
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


def flow_policy(CaseId):
    """
    This function creates the flow policy and add it to the previous role.
    """
    try:
        iamClient.create_policy(
            PolicyName=CaseId + '-Flowlogs',
            PolicyDocument=json.dumps(RolePolicy),
            Description='This policy grants permissions to send logs to CloudWatch and S3'
        )
    except ClientError as e:
        logging.error(e)
        return False
    return True

def attach_role_policy(CaseId):
    try:
        
        iamClient.attach_role_policy(
            RoleName=RoleName,
            PolicyArn='arn:aws:iam::' + account_id + ':policy/' + CaseId + '-Flowlogs'
        )
        print(
            f'Attaching "arn:aws:iam::{account_id}:policy/{CaseId}-Flowlogs" role polcy to {RoleName} role!')
            
        #This policy allows access to S3 buckets.
        iamClient.attach_role_policy(
            RoleName=RoleName,
            PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
        )
        print(
            f'Attaching "arn:aws:iam::aws:policy/AmazonS3FullAccess" role polcy to {RoleName} role!')

    except ClientError as e:
        logging.error(e)
        return False
    return True


def create_flow_log(CaseId, vpc_id):
    """
    Creates a flow log for the specified EC2 instances or VPCs

    """
    try:
        for VpcID in vpc_id:
            ec2_client.create_flow_logs(
            DryRun = False,
            ClientToken = CaseId + "-" + time_now,
                DeliverLogsPermissionArn='arn:aws:iam::' + account_id + ':role/' + RoleName,
            LogGroupName = CaseId,
            ResourceIds = [
                VpcID,
            ],
            ResourceType = 'VPC',
            TrafficType = 'ALL',
            LogDestinationType = 'cloud-watch-logs',
            #LogDestination = 'string',
            #LogFormat = 'string',
            TagSpecifications = [
                {
                    'ResourceType': 'vpc-flow-log',
                    'Tags': [
                        {
                            'Key': 'CaseId',
                            'Value': CaseId
                        },
                    ]
                },
            ],
            #MaxAggregationInterval = 123
            )
    except ClientError as e:
        logging.error(e)
        return False
    return True

def main():
    get_vpc_id(InstanceId)
    create_role(CaseId)
    flow_policy(CaseId)
    attach_role_policy(CaseId)
    create_flow_log(CaseId, VpcID)
    
if __name__ == "__main__":
    main()
