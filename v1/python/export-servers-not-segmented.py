#!/usr/bin/python
#
# Copyright 2021 Zscaler
# SPDX-License-Identifier: Apache-2.0
#

"""
This script can be used to collect and save or display a list of managed hosts
that are not members any host segments not including the excluded skip_segments.
"""

import os
import csv
import yaml
import argparse
import pprint
from edgeutils import ApiSession

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output_file', required=False,
                    help='Name or path to an output csv file. If no output file is provide, output will be printed to the screen.')
parser.add_argument('-d', '--ignore_decommissioned', required=False,
                    help='Ignore hosts where status is decommissioned')
parser.add_argument('-s', '--summary_only', required=False,
                    help='Only print the summary count. Do not print the list of not segmented hosts.')
args = parser.parse_args()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

skip_segments = [
    'All Hosts',
    'All-Hosts',
    'All Managed Hosts',
    'All-Managed-Hosts',
    'HS-All Managed Hosts',
    'HS-All-Managed-Hosts',
    'AAA-all-managed-hosts',
]

api = ApiSession(config)

# Get segments
collections = api.get('collections')['content']
user_collections = [x for x in collections if x['owner'] == 'USER']
segments = [x for x in user_collections if x['query']['type'] == 'HOST']

# Build a list of hosts that are in at least one segment
# Ignore skip_segments host segments
all_segmented_hosts = set()
for segment in segments: 
    if segment['name'].lower() not in [x.lower() for x in skip_segments]:
        r = api.get('scopes/{}/scope-data?scopeType=COLLECTION'.format(segment['id']))
        hosts = [x['name'].lower() for x in r['childScopes'] if x['type'] == 'HOST']
        if len(hosts) > 1:
            all_segmented_hosts.update(hosts)
        elif len(hosts) == 1:
            all_segmented_hosts.add(hosts[0])

# Get all hosts and compare to the first list
not_segmented_hosts = []
hosts = api.get('hosts')['content']
for host in hosts:
    if host['name'].lower() not in all_segmented_hosts:
        if args.ignore_decommissioned and (host['status'] == 'DECOMMISSIONED'):
            continue
        not_segmented_hosts.append({
            'name': host['name'],
            'status': host['status'],
            'addresses': host['addresses'],
        })
print("{} hosts not in a segment".format(len(not_segmented_hosts)))

# Export or print data
if not args.summary_only:
    output = not_segmented_hosts
    if args.output_file:
        output_file = args.output_file.rsplit('/', 1)
        if len(output_file) > 1:
            output_dir = output_file[0]
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        with open('{}'.format(args.output_file), mode='w', newline='') as f:
            if output:
                keys = output[0].keys()
                writer = csv.DictWriter(f, keys)
                writer.writeheader()
                writer.writerows(output)
    else:
        pprint.pprint(output)
