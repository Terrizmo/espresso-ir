#Code source from https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudtrail.html
import logging
import boto3
from botocore.exceptions import ClientError
import json

trail_client = boto3.client('cloudtrail')

caseId = ""
trail_name = 'API_trail_' + caseId
res_trail_names = []

def create_trail(caseId):
    """Create an CloudTrail Trail for API calls bucket in a specified region
    """

    trail_name = 'API_trail_' + caseId

    # Create trail
    try:
        trail_client.create_trail(
            Name=trail_name,
            S3BucketName=caseId + "-api-cloudtrail-log-bucket",
            #S3KeyPrefix='string',
            #SnsTopicName='string',
            IncludeGlobalServiceEvents=True,
            IsMultiRegionTrail=True,
            EnableLogFileValidation=True,
            #CloudWatchLogsLogGroupArn='string',
            #CloudWatchLogsRoleArn='string',
            #KmsKeyId='string',
            IsOrganizationTrail=False,
            TagsList=[
                {
                    'Key': 'CaseId',
                    'Value': caseId
                },
            ]
        )
        logging.info(f'CloudTrail trail "{trail_name}" has been created!')

        trail_client.start_logging(Name=trail_name)

    except ClientError as e:
        logging.error(e)
        return False
    return True

    
"""
Future work
use get_trail_status() API to check if API logging is already enabled. 
Give user option to contiue to make a new trail of keep the current one. 
Also will require a CLI overide to create a new trail anyway. 

response = trail_client.list_trails(
    #NextToken='string'
)

#print(response)


for trails in response['Trails']:
    res_trail_names.append(trails["Name"])



print(res_trail_names)

if trail_name not in res_trail_names:
    create_trail()
    #print(f'CloudTrail trail "{trail_name}" has been created!')
    logging.info(f'CloudTrail trail "{trail_name}" has been created!')
    #Turn on logging on the previous create trail
    trail_client.start_logging(Name=trail_name)
    #print(f'CloudTrail logging for "{trail_name}" has been turned on!')
    logging.info(f'CloudTrail logging for "{trail_name}" has been turned on!')
else:
    #print(f'CloudTrail trail "{trail_name} already exists!')
    logging.warning(f'CloudTrail trail "{trail_name}" already exists!')
"""
def main():
    create_trail(caseId=caseId)

if __name__ == "__main__":
    main()
