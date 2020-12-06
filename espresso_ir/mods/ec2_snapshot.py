# Code source from https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html
import logging
import boto3
from botocore.exceptions import ClientError
import json

client = boto3.client('ec2')

caseId = ""
Instance_list = []

def ec2_snapshot(caseId, Instance_list):

    try:
        for InstanceId in Instance_list:
            client.create_snapshots(
                Description=f'Snapshot of {InstanceId} for IR case: {caseId}',
                InstanceSpecification={
                    'InstanceId': InstanceId,
                    'ExcludeBootVolume': False
                },
                TagSpecifications=[
                    {
                        'ResourceType': 'snapshot',
                        'Tags': [
                            {
                                'Key': 'CaseID',
                                'Value': caseId
                            },
                        ]
                    },
                ],
                DryRun=False,
                CopyTagsFromSource='volume'
            )
            logging.info(f'Snapshot of "{InstanceId}" has be taken')
            
    except ClientError as e:
        logging.error(e)
        return False
    return True


def main():
    ec2_snapshot(caseId, Instance_list)

if __name__ == "__main__":
    main()
