import logging
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

caseId = ''
egress_options = [True, False]
vpc_sg_dict = {}
isolated_instance =[]

def create_vpc():
    """
    This function creates a VPC to isolate compromised instances.
    """

    try:
        vpc = ec2.create_vpc(CidrBlock='192.66.0.0/16')
        vpc.create_tags(Tags=[{"Key": "Name", "Value": "Isolation_VPC"}])
        vpc.wait_until_available()

        logging.info(f'Your isolation VPC ID is {vpc.id}')
        print(vpc.id)

        response = ec2_client.describe_network_acls(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [
                        vpc.id,
                    ]
                },
            ],
        )

        network_acl_id = response['NetworkAcls'][0]['NetworkAclId']

        network_acl = ec2.NetworkAcl(network_acl_id)

        for option in egress_options:
            network_acl.replace_entry(
                CidrBlock='192.66.0.0/16',
                Egress=option,
                Protocol='-1',
                RuleAction='deny',
                RuleNumber=100
            )

        logging.info(f'Acl ID is {network_acl_id} and has blocked all traffic out of VPC {vpc.id}')

        return {'vpc_id': vpc.id, 'acl_id': network_acl_id}

    except ClientError as e:
        logging.error(e)
        return False
    return True

def create_isolation_sg(vpc_id):
    """
    This function creates a Security Group to isolate compromised instances.
    """

    try:
        sg_response = ec2_client.create_security_group(
            Description='Security Group to isolate compromised instances',
            GroupName='Isolation_SG',
            VpcId=vpc_id,
        )

        sg_group_id = sg_response['GroupId']
        security_group = ec2.SecurityGroup(sg_group_id)

        security_group.revoke_egress(
            IpPermissions=[
                {'IpProtocol': '-1', 'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                 'Ipv6Ranges': [], 'PrefixListIds': [], 'UserIdGroupPairs': []}]
        )
        return sg_group_id.split()

    except ClientError as e:
        logging.error(e)
        return False
    return True

def create_sg(vpc_id):
    """
    This function handles the logic for creating Security Group to isolate compromised instances.
    """
    string_vpc_id = str(vpc_id).strip("'[]'")

    try:
        for sg_name in ec2_client.describe_security_groups()['SecurityGroups']:
            if string_vpc_id in sg_name['VpcId']:
                vpc_sg_dict[sg_name['GroupName']] = sg_name['GroupId']

        if 'Isolation_SG' in vpc_sg_dict:
            sg_group_id = vpc_sg_dict['Isolation_SG']
            #vpc_sg_dict.clear
        else:
            sg_group_id = create_isolation_sg(string_vpc_id)
            sg_group_id
            
        return sg_group_id

    except ClientError as e:
        logging.error(e)
        return False
    return True


def isolate_instances(instance_ids, sg_id):
    """
    This function removes the current security group from the instances and adds the isolation security group.
    """
    sg_id = list(sg_id.split())

    try:
        #Get security group IDs to remove from the instances 
        for InstanceId in instance_ids:
            ec2_instance = ec2.Instance(InstanceId)
            #Remove all security groups and add the isolate security group 
            ec2_instance.modify_attribute(Groups=sg_id)
            if InstanceId not in isolated_instance:
                isolated_instance.append(InstanceId)

        return isolated_instance

    except ClientError as e:
        logging.error(e)
        return False
    return True