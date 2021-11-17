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
collections_perimeter = api.get('perimeters')['content']
collections = [x for x in collections_perimeter if x['target']['subtype'] == 'HOST']
collections_hosts = api.get('collections')['content']
user_collections = [x for x in collections_hosts if x['owner'] == 'USER']
segments = [x for x in user_collections if x['query']['type'] == 'HOST']

full_block=[]
for x in collections:
    if x['inboundAction'] == 'BLOCK':
        full_block.append({
            'Host-Segment Name': x['target']['name'],
	    'Status' : 'Full Blocks' 	
        })
    if x['inboundAction'] == 'SIMULATE_BLOCK':
        full_block.append({
            'Host-Segment Name': x['target']['name'],
            'Status' : 'Sim-Block'
        })

for x in segments:
    if x['autoSegTime'] == None:
        full_block.append({
            'Host-Segment Name': x['name'],
            'Status': 'No Perimeter'
        })

## Export or print data
if args.output_file:
    output_file = args.output_file.rsplit('/', 1)
    if len(output_file) > 1:
        output_dir = output_file[0]
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    with open('{}'.format(args.output_file), 'w', newline='') as f:
        keys = full_block[0].keys()
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(full_block)
else:
    pprint.pprint(full_block)
