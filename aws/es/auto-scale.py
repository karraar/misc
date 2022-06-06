#!/usr/bin/env python3

from datetime import datetime, timedelta
from requests_aws_sign import AWSV4Sign
from boto3 import session
import boto3
from elasticsearch import Elasticsearch
import json
import math
import re
import getopt
import sys

es_domain_name = ""
region = "us-east-1"
percent_nodes_available_allow = 0.30
min_slave_nodes = 5
max_slave_nodes = 50
configure = False


class ClusterNodesInfo(object):
    def __init__(self, domain_status):
        self.slaves = domain_status['ElasticsearchClusterConfig']['InstanceCount']
        self.masters = domain_status['ElasticsearchClusterConfig']['DedicatedMasterCount']
        self.total = self.slaves + self.masters
        self.print_node_info()

    def print_node_info(self):
        print("Cluster Nodes: {} ({} Masters and {} Slaves).".format(
            self.total,
            self.masters,
            self.slaves))


class ClusterStorageInfo(object):
    def __init__(self, domain_status, cluster_nodes, es_domain_name, client_id):
        self.per_node = domain_status['EBSOptions']['VolumeSize']
        self.total = float(cluster_nodes.slaves * self.per_node)
        self.used = float(ClusterStorageInfo.get_cloudwatch_metric('ClusterUsedSpace', es_domain_name, client_id) / 1024)
        self.available = self.total - self.used
        self.print_storage_info()

    @staticmethod
    def get_cloudwatch_metric(metric_name, es_domain_name, client_id):
        metric_value = boto3.client('cloudwatch').get_metric_statistics(Namespace='AWS/ES',
                                                                        Dimensions=[
                                                                            {'Name': 'DomainName',
                                                                             'Value': es_domain_name},
                                                                            {'Name': 'ClientId', 'Value': client_id}
                                                                        ],
                                                                        MetricName=metric_name,
                                                                        StartTime=datetime.now() - timedelta(minutes=5),
                                                                        EndTime=datetime.now(),
                                                                        Period=300,
                                                                        Unit='Megabytes',
                                                                        Statistics=['Average']
                                                                        )['Datapoints'][0]['Average']
        return metric_value

    def print_storage_info(self):
        print("Cluster Disk Space(GB): {:,.2f} Total ({:,.2f} Used, {:,.2f} Available).".format(
            self.total,
            self.used,
            self.available))


class ClusterInfo(object):
    region_pattern = re.compile('\.(.*)\.es.amazonaws.com')

    def __init__(self, es_domain_name):
        self.boto3_es = boto3.client('es', 'us-east-1')
        self.es_describe = self.boto3_es.describe_elasticsearch_domain(DomainName=es_domain_name)
        self.client_id = self.es_describe['DomainStatus']['DomainId'].split('/')[0]
        self.endpoint = self.es_describe['DomainStatus']['Endpoint']
        self.region = self.region_pattern.search(self.endpoint).group(1)
        self.nodes = ClusterNodesInfo(self.es_describe['DomainStatus'])
        self.storage = ClusterStorageInfo(self.es_describe['DomainStatus'], self.nodes, es_domain_name, self.client_id)

    def set_nodes(self, new_instance_count):
        r = self.boto3_es.update_elasticsearch_domain_config(
            DomainName=es_domain_name,
            ElasticsearchClusterConfig={'InstanceCount': new_instance_count}
        )
        print(r)


def usage():
    print("Usage: {} -d <es-domain-name>  [OPTIONS]".format(sys.argv[0]))
    print("\t-d, --domain-name=<es-domain-name>")
    print("\t\t\t\t## Required: The AWS ElasticSearch Domain Name to use.")
    print("\t-r, --region=<region>")
    print("\t\t\t\t## Optional: The AWS Region to use. Default: us-east-1")
    print("\t--min-slaves=<min-slaves-to-use>")
    print("\t\t\t\t## Optional: The minimum number of slave nodes to use. Default: 5")
    print("\t--max-slaves=<max-slaves-to-use>")
    print("\t\t\t\t## Optional: The maximum number of slave nodes to use. Default: 50")
    print("\t-p, --percent-allow=<%-slaves-to-allow>")
    print("\t\t\t\t## Optional: The % number of slave nodes to allow for growth and sharding. Default: .30")
    print("\t-c, --configure")
    print("\t\t\t\t## Optional: Actually request cluster configuration changes.  Default false")


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hd:r:p:c",
                                   ["help",
                                    "domain-name=",
                                    "region=",
                                    "min-slaves=",
                                    "max-slaves=",
                                    "percent-allow=",
                                    "configure"])
    except getopt.GetoptError as err:
        print("Got GetoptError: " + str(err))
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--domain-name"):
            es_domain_name = arg
        elif opt in ("-r", "--region"):
            region = arg
        elif opt == '--min-slaves':
            min_slave_nodes = int(arg)
        elif opt == '--max-slaves':
            max_slave_nodes = int(arg)
        elif opt == '--percent-allow':
            percent_nodes_available_allow = float(arg)
        elif opt in ("-c", '--configure'):
            configure = True

    print("Using the following configuration:")
    print("DomainName:    " + str(es_domain_name))
    print("min-slaves:    " + str(min_slave_nodes))
    print("max-slaves:    " + str(max_slave_nodes))
    print("percent-allow: " + str(percent_nodes_available_allow))
    print("configure:     " + str(configure))
    print("")

    if es_domain_name == "":
        print("")
        print("\t-d, --domain-name=<domain-name> is a required parameter.")
        print("")
        usage()
        sys.exit(2)

    cluster_info = ClusterInfo(es_domain_name)

    # Calculate Number of nodes needed for this disk space.
    cluster_slave_nodes_needed = int(math.ceil(cluster_info.storage.used / cluster_info.storage.per_node))
    cluster_slave_nodes_needed_with_allowance = int(
        math.ceil(math.ceil(cluster_slave_nodes_needed * percent_nodes_available_allow) + cluster_slave_nodes_needed))
    cluster_slave_nodes_needed_safe_guarded = min(max(cluster_slave_nodes_needed_with_allowance, min_slave_nodes),
                                                  max_slave_nodes)

    print("Cluster Slave Nodes: Currently using: {}, Need: {}, with allowance: {}, with safeguard: {}.".format(
        cluster_info.nodes.slaves,
        cluster_slave_nodes_needed,
        cluster_slave_nodes_needed_with_allowance,
        cluster_slave_nodes_needed_safe_guarded))

    if configure:
        print("Changing Configuration...")
        cluster_info.set_nodes(cluster_slave_nodes_needed_safe_guarded)
