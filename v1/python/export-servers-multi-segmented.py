#!/usr/bin/python
#
# Copyright 2021 Zscaler
# SPDX-License-Identifier: Apache-2.0
#

"""
This script can be used to collect and save or display a list of managed hosts
that are members of at least two host segments not including the excluded skip_segments.
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
args = parser.parse_args()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

skip_segments = [
    'All Hosts',
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

# Build a list of segment data that includes the member hosts
# Ignore skip_segments host segments
segment_data = []
for segment in segments:
    r = api.get('scopes/{}/scope-data?scopeType=COLLECTION'.format(segment['id']))
    hosts = [x['name'] for x in r['childScopes'] if x['type'] == 'HOST']
    if segment['name'] in skip_segments:
        continue
    segment_data.append({
        'id': segment['id'],
        'name': segment['name'],
        'hosts': hosts,
        'auto-update': segment['dynamic'],
        'query-definition': segment['query'],
    })

# Build a map of hosts to the segments they belong to
host_to_segment_map = {}
hosts = api.get('hosts')['content']
for host in hosts:
    for segment in segment_data:
        if host['name'] in segment['hosts']:
            if host['name'] in host_to_segment_map.keys():
                host_to_segment_map[host['name']].add(segment['name'])
            else:
                host_to_segment_map[host['name']] = set([segment['name']])

# Find hosts that are in multiple segments
multi_segmented_hosts = []
for k,v in host_to_segment_map.items():
    if len(v) > 1:
        multi_segmented_hosts.append({
            'name': k,
            'segments': v,
        })

# Export or print data
output = multi_segmented_hosts
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
