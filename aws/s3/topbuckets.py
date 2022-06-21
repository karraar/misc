#!/usr/bin/env python3

import sys
import boto3
import datetime
import pandas as pd
from tabulate import tabulate
import getopt
import humanize


def list_s3_objects(bucket, max_levels_in_details):
    """List all keys in an S3 bucket and return a pandas dataframe"""

    objects = []
    for o in s3.Bucket(bucket).objects.all():
        obj = {'Key': o.key,
               'LastModified': o.last_modified,
               'Size': o.size,
               'level0': '/',
               'level1': '/' + o.key.split('/')[0]
               }
        for lvl in range(2, max_levels_in_details):
            obj['level' + str(lvl)] = '/' + '/'.join(o.key.split('/')[0:lvl])
        objects.append(obj)

    return pd.DataFrame(objects)


def agg_bucket_level(df, level_col, level):
    """Aggregate bucket stats at level column"""

    level_df = df.groupby(level_col, as_index=False) \
        .agg(num_objects=('Size', 'count'),
             size=('Size', 'sum'),
             min_last_modified=('LastModified', 'min'),
             max_last_modified=('LastModified', 'max')
             )
    level_df['level'] = level
    level_df['objects'] = level_df['num_objects'].map(lambda x: humanize.intword(x))
    level_df['sizes'] = level_df['size'].map(lambda x: humanize.naturalsize(x, False, True, '%8.1f'))
    level_df['prefix'] = level_df[level_col]
    return level_df.sort_values(['size', 'num_objects'], ascending=False).head(5)


def print_bucket_stats(df, max_levels_in_details):
    level_details = []
    for lvl in range(0, max_levels_in_details):
        level_details.append(agg_bucket_level(df, 'level' + str(lvl), lvl))

    bucket_summary_df = pd.concat(level_details)[['level',
                                                  'size_gb',
                                                  'num_objects_k',
                                                  'min_last_modified',
                                                  'max_last_modified',
                                                  'prefix']]

    print(tabulate(bucket_summary_df, headers='keys', tablefmt='psql', showindex=False))


def get_s3_bucket_size(bucket):
    now = datetime.datetime.now()
    sizes = cw.get_metric_statistics(Namespace='AWS/S3',
                                     MetricName='BucketSizeBytes',
                                     Dimensions=[{'Name': 'BucketName', 'Value': bucket},
                                                 {'Name': 'StorageType', 'Value': 'StandardStorage'}],
                                     Statistics=['Average'],
                                     Period=3600,
                                     StartTime=(now - datetime.timedelta(days=2)).isoformat(),
                                     EndTime=now.isoformat()
                                     )['Datapoints']

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
                                 EndTime=now.isoformat()
                                 )['Datapoints']

    return int(n[0]['Average']) if len(n) > 0 else 0


def get_s3_buckets_stats():
    """Iterate through each bucket"""

    buckets_stats = {}
    for bucket in s3.buckets.all():
        buckets_stats[bucket.name] = [get_s3_bucket_size(bucket.name),
                                      get_s3_bucket_num_objects(bucket.name)]

    return buckets_stats


def get_top_s3_buckets(max_buckets):
    s3_buckets_stats = get_s3_buckets_stats()
    return sorted(s3_buckets_stats.items(),
                  key=lambda item: item[1],
                  reverse=True)[0:max_buckets]


def print_top_s3_buckets(max_buckets, max_buckets_with_details, max_levels_in_details):
    print("Top {} Buckets by Size:".format(max_buckets))
    print("{:<60s}{:>30s}{:>30s}".format('Bucket', 'Avg[2 days] Size (GB)', 'Avg[2 days] # Objects (k)'))

    detail = 1
    for b in get_top_s3_buckets(max_buckets):
        bucket = b[0]
        size_gb = int(b[1][0] / 1024 / 1024 / 1024)
        num_objects = int(b[1][1] / 1000)
        print("{:<60s}{:>30,d}{:>30,d}".format(bucket, size_gb, num_objects))
        if detail <= max_buckets_with_details:
            if num_objects > 0:
                print_bucket_stats(list_s3_objects(b[0], max_levels_in_details), max_levels_in_details)
            detail = detail + 1


def usage():
    print("Usage: {} [OPTIONS]".format(sys.argv[0]))
    print("\t-r, --region=<region>")
    print("\t\t## Optional<Default: us-east-1>: The AWS Region to use.")
    print("\t-m, --max_buckets=<max_buckets>")
    print("\t\t## Optional<Default: 10>: The number of top buckets to print.")
    print("\t-d, --max_buckets_with_details=<max_buckets_with_details>")
    print("\t\t## Optional<Default: 1>: The number of buckets to print with details.")
    print("\t-l, --max_levels_in_details=<max_levels_in_details>")
    print("\t\t## Optional<Default: 3>: The number of levels to print in detailed buckets report.")


def get_options():
    opts = {'region': 'us-east-1',
            'max_buckets': 10,
            'max_buckets_with_details': 1,
            'max_levels_in_details': 3}
    try:
        optlist, args = getopt.getopt(sys.argv[1:],
                                      "hr:m:d:l:",
                                      ["help",
                                       "region=",
                                       "max_buckets=",
                                       "max_buckets_with_details=",
                                       "max_levels_in_details="])
    except getopt.GetoptError as err:
        print("Got Getopt Error: " + str(err))
        usage()
        sys.exit(2)

    for opt, arg in optlist:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-r", "--region"):
            opts['region'] = arg
        elif opt in ("-m", "--max_buckets"):
            opts['max_buckets'] = int(arg)
        elif opt in ("-d", "--max_buckets_with_details"):
            opts['max_buckets_with_details'] = int(arg)
        elif opt in ("-l", "--max_levels_in_details"):
            opts['max_levels_in_details'] = int(arg)

    return opts


if __name__ == "__main__":
    options = get_options()
    cw = boto3.client('cloudwatch', options['region'])
    s3 = boto3.resource('s3', options['region'])
    print_top_s3_buckets(options['max_buckets'],
                         options['max_buckets_with_details'],
                         options['max_levels_in_details'])
