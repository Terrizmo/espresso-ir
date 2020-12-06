# Code adapted from https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-creating-buckets.html
import logging
import boto3
from botocore.exceptions import ClientError
import json

caseId = "dissertation"

bucket_name = caseId + "-api-cloudtrail-log-bucket"

bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck20150319",
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "cloudtrail.amazonaws.com"
                ]
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::" + bucket_name
        },
        {
            "Sid": "AWSCloudTrailWrite20150319",
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "cloudtrail.amazonaws.com"
                ]
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::" + bucket_name + "/AWSLogs/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}

# Convert the policy from JSON dict to string
bucket_policy = json.dumps(bucket_policy)

def create_bucket(caseId, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    s3 = boto3.client('s3')
    response = s3.list_buckets()
    res_bucket_names = []
    bucket_name = caseId + "-api-cloudtrail-log-bucket"

    # Create bucket
    try:

        for bucket in response['Buckets']:
            res_bucket_names.append(bucket["Name"])

        if bucket_name not in res_bucket_names:
            if region is None:
                s3_client = boto3.client('s3')
                s3_client.create_bucket(Bucket=bucket_name)
    
                # Set the new policy on the given bucket
                s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
            else:
                s3_client = boto3.client('s3', region_name=region)
                location = {'LocationConstraint': region}
                s3_client.create_bucket(Bucket=bucket_name,
                                        CreateBucketConfiguration=location, )
                # Set the new policy on the given bucket
                s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
        else:
            print(f'API log Bucket "{bucket_name}" already exists!')
            #logging.warning(f'API log Bucket "{bucket["Name"]}" already exists!')
    except ClientError as e:
        logging.error(e)
        return False
    return True


def main():
    create_bucket(caseId)

if __name__ == "__main__":
    main()


