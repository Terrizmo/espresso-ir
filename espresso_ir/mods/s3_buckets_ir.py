# Code adapted from https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-creating-buckets.html
import logging
import boto3
from botocore.exceptions import ClientError
import json

s3 = boto3.client('s3')

caseId = "dissertation"
binary_bucket = caseId + "-binary-source-bucket"
evidence_bucket = caseId + "-evidence-bucket"
bucket_names = [binary_bucket, evidence_bucket]
binary_location = ""

bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            
    }
    ]
}

# Convert the policy from JSON dict to string
#bucket_policy = json.dumps(bucket_policy)

def create_bucket(bucket_name, region=None):

    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
            # Set the new policy on the given bucket
            #s3_client.put_bucket_policy(
            #    Bucket=bucket_name, Policy=bucket_policy)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
            # Set the new policy on the given bucket
            #s3_client.put_bucket_policy(
            #    Bucket=bucket_name, Policy=bucket_policy)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def does_bucket_exist(caseId):

    # Retrieve the list of existing buckets

    binary_bucket = caseId + "-binary-source-bucket"
    evidence_bucket = caseId + "-memory-evidence-bucket"
    bucket_names = [binary_bucket, evidence_bucket]

    try:

        response = s3.list_buckets()
        
        res_bucket_names = []
        
        for bucket in response['Buckets']:
            res_bucket_names.append(bucket["Name"])
        
        for bucket_name in bucket_names:
            if bucket_name not in res_bucket_names:
                create_bucket(bucket_name)
                #print(f'API log bucket "{bucket_name}" has been created!')
                logging.info(f'API log bucket "{bucket_name}" has been created!')
            else:
                #print(f'API log Bucket "{bucket_name}" already exists!')
                logging.warning(f'API log Bucket "{bucket_name}" already exists!')
        
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_memory_capture_binary(binary_location, caseId, object_name='DumpItx64.exe'):
    """Uploads the selected memory capture binary to the designated binary S3 bucket

    : param binary_location: File to upload
    : param bucket: Bucket to upload to
    : param object_name: S3 object name. If not specified then file_name is used
    : return: True if file was uploaded, else False
    """
    #Name of S3 bucket to store binary
    binary_bucket = caseId + "-binary-source-bucket"

    # If S3 object_name was not specified, use file_name
    """if object_name is None:
        object_name = file_name"""

    # Upload the file
    try:
        s3.upload_file(binary_location, binary_bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def main():
    does_bucket_exist(caseId)
    upload_memory_capture_binary(binary_location, caseId)

    
if __name__ == "__main__":
    main()
