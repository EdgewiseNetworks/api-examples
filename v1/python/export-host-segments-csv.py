#!/usr/bin/env python
#
# Copyright 2020 Edgewise Networks
# SPDX-License-Identifier: Apache-2.0
#

import os
import csv
import yaml
import argparse
import pprint
from edgeutils import ApiSession

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--segment_name', required=False,
                    help='Name of the host segment to inspect. If no host segment name is provided, all host segments will be returned.')
parser.add_argument('-o', '--output_file', required=False,
                    help='Name or path to an output csv file. If no output file is provide, output will be printed to the screen.')
args = parser.parse_args()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

api = ApiSession(config)

# Get segments
collections = api.get('collections')['content']
user_collections = [x for x in collections if x['owner'] == 'USER']
segments = [x for x in user_collections if x['query']['type'] == 'HOST']

# If a segment name is provided, find that segment
if args.segment_name:
    segment_names = [x['name'] for x in segments]
    if args.segment_name not in segment_names:
        raise Exception("Supplied segment '{}' was not found. Valid segments are: \n{}".format(
            args.segment_name, 
            segment_names
        ))
    segments = [next((x for x in segments if x['name'] == args.segment_name), None)]

# Get hosts in relevant segments
data = []
for segment in segments:
    r = api.get('scopes/{}/scope-data?scopeType=COLLECTION'.format(segment['id']))
    hosts = [x['name'] for x in r['childScopes'] if x['type'] == 'HOST']
    data.append({
        'id': segment['id'],
        'name': segment['name'],
        'hosts': hosts,
        'auto-update': segment['dynamic'],
        'query-definition': segment['query'],
    })

# Export or print data
if args.output_file:
    output_file = args.output_file.rsplit('/', 1)
    if len(output_file) > 1:
        output_dir = output_file[0]
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    with open('{}'.format(args.output_file), 'w', newline='') as f:
        keys = data[0].keys()
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(data)
else:
    pprint.pprint(data)

