import argparse
import os
import logging
import time


import espresso_ir
from espresso_ir.mods import (cloudtrail_api, s3_bucket_cloudtrail, 
    ssm_setup, s3_buckets_ir, memdump, flow_logs, get_logs, ec2_snapshot, 
    vpc
)

#List of args, Cases number, Region, EC2 instance ID, Dump memeory, Set up API reording, Flow logs, EC2  Snapshot, EC2 Isolation

t0 = time.time()

def cli():

    parser = argparse.ArgumentParser(description='An Incident Repsonse tool for memory aquisition of windows hosts on AWS.')

    parser.add_argument(
        'caseID',
        help='The case id matched to this incident and to associate with the result of this command. Must be lowercase Alpha Numeric and hyphens, no spaces allowed.',
        type=str,
        metavar='case-id',
        action='store'
    )

    parser.add_argument(
        '-a',
        '--api-logging',
        help='Turns on CloudTrail API logging named "API_trail_<case id>" to S3 bucket "<case ID>-api-cloudtrail-log-bucket"',
        metavar='apiLogging',
        const=True,
        action='store_const'
    )

    parser.add_argument(
        '--setup',
        help='Creates roles and policies to to collect memory using SSM and creates S3 Bucket to put the memory dumps. Requires the file local file location of memory aquisition tool (currently only supports DumpIt).',
        nargs='+',
        metavar='Path_To_DumpIt',
        action='store',
        dest='setup'
    )

    parser.add_argument(
        '-dm',
        '--dump-memory',
        help='Creates a Memory dump of the supplied Instance ID and Output to evidence S3 bucket',
        nargs='+',
        metavar='Instance ID',
        action='store',
        dest='dumpMem'
    )

    parser.add_argument(
        '-fl',
        '--flow-logs',
        help='Turns on flow logs for the VPC of the specified Instance ID',
        nargs='+',
        metavar='Instance ID',
        action='store',
        dest='flowLogs'
    )

    parser.add_argument(
        '-sf',
        '--search-flow',
        help='Uses CloudWatch to search for the bad IP address and returns the Instance Ids for the host communicating with it.',
        nargs='+',
        metavar='Bad IP Address',
        action='store',
        dest='badIPAddress'
    )

    parser.add_argument(
        '-s',
        '--snapshot',
        help='Create a snapshot of the specified Instance ID',
        nargs='+',
        metavar='Instance ID',
        action='store',
        dest='snapshot'
    )

    parser.add_argument(
        '-i',
        '--isolate',
        help='Changes Instances Secuirty Group to one with no rules denying any traffic in or out.',
        nargs='+',
        metavar='Instance ID',
        action='store',
        dest='isolate'
    )

    args = parser.parse_args()
    caseid = args.caseID

    # Logging not fully set for all actions yet
    #logging.basicConfig(level='INFO',filename=f'{caseid}.logs')

    #print(args)

    #Processing Algorithm for flow control of function execution.

    if (args.api_logging):
        logging.info('Turning on API logging')
        s3_bucket_cloudtrail.create_bucket(caseid)
        cloudtrail_api.create_trail(caseid)
    else:
       logging.info('Not turning logging API calls')

    if (args.setup):
        file_location = os.path.normpath(str(args.setup).strip("[]'"))
        logging.info('Setup started')
        s3_buckets_ir.does_bucket_exist(caseid)
        s3_buckets_ir.upload_memory_capture_binary(file_location, caseid)
        ssm_setup.create_role(caseid)
        ssm_setup.attach_role_policy()
        flow_logs.create_role(caseid)
        flow_logs.flow_policy(caseid)
        flow_logs.attach_role_policy(caseid)
        
    if (args.dumpMem):
        #ssm_setup.add_role_to_ec2(args.dumpMem)
        result = memdump.dump_memory(caseid, args.dumpMem)
        print(f'Memory is being acquired from the following instance: {result}')

    if (args.flowLogs):
        vpc_id = flow_logs.get_vpc_id(args.flowLogs)
        flow_logs.create_flow_log(caseid, vpc_id)

    if (args.badIPAddress):
        logStream = get_logs.get_log_streams(caseid)
        ip_compromised = get_logs.get_log_events(
            caseid, args.badIPAddress, logStream)
        get_logs.get_ec2_id_from_ip(ip_compromised) 

    if (args.snapshot):
        ec2_snapshot.ec2_snapshot(caseid, args.snapshot)

    if (args.isolate):
        #Get instance VPC ID
        vpc_ids = flow_logs.get_vpc_id(args.isolate)
        #Create Security Group in VPC
        for vpc_id in vpc_ids:
            sg_group_id = vpc.create_sg(vpc_id)
            isolated = vpc.isolate_instances(args.isolate, sg_group_id)
        print(f'{isolated} have been isolated!')

    t1 = time.time()
    total = t1-t0

    print(f'Completed in {total} seconds')
    
    
if __name__ == "__main__":
    cli()
