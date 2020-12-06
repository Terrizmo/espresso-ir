import logging
import boto3
from botocore.exceptions import ClientError
import json


ssm = boto3.client('ssm')
ec2 = boto3.resource('ec2')
Instance = ec2.Instance('id')

Instance_list = []
DumpBucket = 'mem-dump-test-bucket'
bucketName = 'dumpit-test-bucket'
S3Key = 'DumpItx64.exe'
caseId = ''
dump_instance_list =[]

def dump_memory(caseId,instance_list):

    """
    This function downloads Dumpit from an S3 bucket creates a memory dump 
    of a Windows machine and uploads it to a seprate S3 bucket, then
    removes the files form the Windows host.
    """

    dump_bucket = caseId + '-memory-evidence-bucket'
    binary_bucket = caseId + '-binary-source-bucket'
    Instance_list = instance_list

    for InstanceId in Instance_list:
        ec2_instance = ec2.Instance(InstanceId)
        platform = ec2_instance.platform
        state = ec2_instance.state['Name']

        #Check Instance is running
        if state == "running":
            InstanceIds = [InstanceId]
    
            #Check the instance is running Windows
            if platform == "windows":
                #Keep a list of Windows hosts to send the dump memory commands to. Max of 50 can be sent at once 
                dump_instance_list.extend(InstanceIds)
    
                commands = ["Copy-S3Object -BucketName " + binary_bucket + " -Key " + S3Key + " -LocalFolder C:\\users\\Administrator\\Downloads",
                            "cd  C:\\users\\Administrator\\Downloads",
                            "$InstanceId = Get-EC2InstanceMetadata -Category InstanceId",
                            "mkdir $InstanceId",
                            ".\\DumpItx64.exe /N /Q /O .\\$InstanceId\\$InstanceId",
                            "Write-S3Object -bucketname " + dump_bucket + " -Folder .\\$InstanceId\\ " + "-keyprefix $InstanceId",
                            "Remove-Item * -Recurse"]  # clean up on the Instances and remove the exe and memory dump
            else:
                logging.error(f"{InstanceId} is not a windows host. Memory capture not attempted")
        
        else:
            logging.error(f"{InstanceId} is offline")
    
    #Max of 50 host can be sent due to Service manager restrictions. No validation currently in place.
    ssm.send_command(
        InstanceIds=dump_instance_list,
        DocumentName='AWS-RunPowerShellScript',
        Parameters={'commands': commands
                    }
    )
    return dump_instance_list

def main():
    dump_memory(caseId, Instance_list)

if __name__ == "__main__":
    main()
