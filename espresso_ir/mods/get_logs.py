import logging
import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone
#import time

log_client = boto3.client('logs')
ec2 = boto3.resource('ec2')

ip_compromised = []
instance_compromised = []
stream_list = []
ip_addresses = []
#Start time is 60 minute ago in epoch. Required for get_log_event API call
start_time = int((datetime.utcnow() - timedelta(minutes=60)).timestamp()) * 1000
#currrent time in epoch. Required for get_log_event API call
end_time = int(datetime.utcnow().timestamp()) * 1000

#CaseId = 'dissertation'
def get_log_streams(CaseId):
    """
    This gets the name of the log streams within the case loggroup name that was set up from flow_logs.

    """
    stream_response = log_client.describe_log_streams(logGroupName=CaseId)
    
    try:

        for streams in stream_response['logStreams']:
            stream_list.append(streams['logStreamName'])
    
        return stream_list

    except ClientError as e:
        logging.error(e)
        return False
    return True
    

def get_log_events(CaseId, ip_addresses, logStream):
    """
    Gets log events from the selected Stream list. 
    Finds the suspecious IP and returns the local host machines IP addresses.
    """
    global log_response

    try:

        for logStream in stream_list:
            #Gets the logs that match the inputed parameters
    
            log_response = log_client.get_log_events(
                logGroupName=CaseId,
                logStreamName=logStream,
                startTime=start_time,
                endTime=end_time,
                #nextToken='string',
                limit=100, #Hard coded value just for testing
                #startFromHead=False
            )
            
            for ip_address in ip_addresses:
    
                #Finds the matching IP address and extracts the local IP  
                for event in log_response['events']:
                    if ip_address in event['message']:
                        #print(event['timestamp'], event['message'])
                        ip_match = event['message'].split(' ')[4]
                        #Might need to be if ip match not in ip_compromised
                        if ip_address not in ip_match:
                            ip_compromised.append(ip_match)

        return ip_compromised
        
    except ClientError as e:
        logging.error(e)
        return False
    return True

    



def get_ec2_id_from_ip(ip_compromised):
    """
    This function will return the Instance ID for the submitted IP address.

    """

    try:
        for instance in ec2.instances.all():
            #print(instance.private_ip_address)
            if instance.private_ip_address in ip_compromised:
                print(f'The ID for {instance.private_ip_address} that has been communcating with the supplied IP address is {instance.instance_id}')
                logging.debug(f'The ID for {instance.private_ip_address} that has been communcating with the supplied IP address is {instance.instance_id}')
                instance_compromised.append(instance.instance_id)
        
        return instance_compromised
        
    except ClientError as e:
        logging.error(e)
        return False
    return True

    



def main():
    get_log_streams('dissertation')
    get_log_events('dissertation', '8.8.8.8', stream_list)
    get_ec2_id_from_ip(ip_compromised)
    print(instance_compromised)


if __name__ == "__main__":
    main()
