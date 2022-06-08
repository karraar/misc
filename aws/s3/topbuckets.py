#!/usr/bin/env python3

import sys
import boto3
import datetime
import pandas as pd
from tabulate import tabulate
import getopt


def list_s3_objects(bucket):
    """List all keys in an S3 bucket and return a pandas dataframe"""

    objects = []
    for page in s3.get_paginator('list_objects_v2').paginate(Bucket=bucket):
        if 'Contents' in page:
            for obj in page['Contents']:
                obj['level0'] = '/'
                obj['level1'] = '/' + obj['Key'].split('/')[0]
                obj['level2'] = '/' + '/'.join(obj['Key'].split('/')[0:2])
                del obj['Key']
                del obj['ETag']
                objects.append(obj)

    return pd.DataFrame(objects)


def agg_bucket_level(df, level_col, level):
    """Aggregate bucket stats at level column"""

    level_df = df.groupby(level_col) \
        .agg({'Size': ['count', 'sum'],
              'LastModified': ['min', 'max']}
             )
    level_df['level'] = level
    level_df.rename(columns={level_col: 'prefix'})
    level_df.columns = ['level', 'num_objects', 'size', 'minLastModified', 'maxLastModified']
    level_df['num_objects_k'] = level_df['num_objects'].map(lambda x: '{:,}'.format(int(x / 1000)))
    level_df['size_k'] = level_df['size'].map(lambda x: '{:,}'.format(int(x / 1024 / 1024 / 1024)))
    return level_df


def print_bucket_stats(df):
    level0_df = agg_bucket_level(df, 'level0', 0)
    level1_df = agg_bucket_level(df, 'level1', 1)
    level2_df = agg_bucket_level(df, 'level2', 2)

    bucket_summary_df = pd.concat([level0_df, level1_df, level2_df], ignore_index=True)
    bucket_summary_df = bucket_summary_df.sort_values(['level', 'size', 'num_objects'], ascending=False)
    del bucket_summary_df['size']
    del bucket_summary_df['num_objects']
    print(tabulate(bucket_summary_df, headers='keys', tablefmt='psql'))


def get_s3_bucket_size(bucket):
    now = datetime.datetime.now()
    sizes = cw.get_metric_statistics(Namespace='AWS/S3',
                                     MetricName='BucketSizeBytes',
                                     Dimensions=[{'Name': 'BucketName', 'Value': bucket},
                                                 {'Name': 'StorageType', 'Value': 'StandardStorage'}],
                                     Statistics=['Average'],
                                     Period=3600,
                                     StartTime=(now - datetime.timedelta(days=2)).isoformat(),
                                     EndTime=now.isoformat())['Datapoints']

    return int(sizes[0]['Average']) if len(sizes) > 0 else 0


def get_s3_bucket_num_objects(bucket):
    now = datetime.datetime.now()
    n = cw.get_metric_statistics(Namespace='AWS/S3',
                                 MetricName='NumberOfObjects',
                                 Dimensions=[{'Name': 'BucketName', 'Value': bucket},
                                             {'Name': 'StorageType', 'Value': 'AllStorageTypes'}],
                                 Statistics=['Average'],
                                 Period=3600,
                                 StartTime=(now - datetime.timedelta(days=2)).isoformat(),
                                 EndTime=now.isoformat())['Datapoints']

    return int(n[0]['Average']) if len(n) > 0 else 0


def get_s3_buckets_stats():
    """Iterate through each bucket"""

    buckets_stats = {}
    for bucket in s3.list_buckets()['Buckets']:
        size = get_s3_bucket_size(bucket['Name'])
        num_objects = get_s3_bucket_num_objects(bucket['Name'])
        buckets_stats[bucket['Name']] = [size, num_objects]

    return buckets_stats


def get_top_s3_buckets(buckets_limit):
    s3_buckets_stats = get_s3_buckets_stats()
    return sorted(s3_buckets_stats.items(), key=lambda item: item[1], reverse=True)[0:buckets_limit]


def print_top_s3_buckets(buckets_limit, buckets_details_limit):
    print("Top {} Buckets by Size:".format(buckets_limit))
    print("{:<60s}{:>30s}{:>30s}".format('Bucket', 'Avg[2 days] Size (GB)', 'Avg[2 days] # Objects (k)'))

    detail = 1
    for b in get_top_s3_buckets(buckets_limit):
        bucket = b[0]
        size = int(b[1][0] / 1024 / 1024 / 1024)
        objects = int(b[1][1] / 1000)
        print("{:<60s}{:>30,d}{:>30,d}".format(bucket, size, objects))
        while detail <= buckets_details_limit:
            if objects > 0:
                print_bucket_stats(list_s3_objects(b[0]))
            detail = detail + 1


def usage():
    print("Usage: {} [OPTIONS]".format(sys.argv[0]))
    print("\t-r, --region=<region>")
    print("\t\t\t\t## Optional: The AWS Region to use. Default: us-east-1")
    print("\t--limit=<buckets-limit>")
    print("\t\t\t\t## Optional: The number of top buckets to print. Default: 10")
    print("\t--details_limit=<buckets-details-limit>")
    print("\t\t\t\t## Optional: The number of buckets to print details for. Default: 1")


if __name__ == "__main__":
    options = {'region': 'us-east-1', 'buckets_limit': 10, 'buckets_details_limit': 1}
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hr:l:d:",
                                   ["help",
                                    "region=",
                                    "limit=",
                                    "details_limit="])
    except getopt.GetoptError as err:
        print("Got Getopt Error: " + str(err))
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-r", "--region"):
            options['region'] = arg
        elif opt in ("-l", "--limit"):
            options['buckets_limit'] = int(arg)
        elif opt in ("-d", "--details_limit"):
            options['buckets_details_limit'] = int(arg)

    cw = boto3.client('cloudwatch', options['region'])
    s3 = boto3.client('s3', options['region'])
    print_top_s3_buckets(options['buckets_limit'], options['buckets_details_limit'])