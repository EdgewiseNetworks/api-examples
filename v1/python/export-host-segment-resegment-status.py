#!/usr/bin/python
#
# Copyright 2021 Zscaler
# SPDX-License-Identifier: Apache-2.0
#

"""
This script recreates the Auto-Segment workflow logic that displays app paths that are 
not covered by policy and have a firstSeen time newer than time t. Time t is the autoSegTime
timestamp by default but this is configurable via the CLI options.
"""

import os
import csv
import yaml
import argparse
import urllib.parse
import dateutil.parser
from edgeutils import ApiSession

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--all_time', required=False, action='store_true',
                    help='The default is to use the Auto-Segment timestamp as the starting point when calculating new paths \
                          not covered by policy since time t. Use this option to calculate new paths not covered by policy for all time.')
parser.add_argument('-c', '--custom_timestamp', required=False, action='extend', nargs='+', type=str,
                    help='Use a custom timestamp as the starting point when calculating new paths since time t. \
                          The format should be year-month-day hour:minute:second.')
parser.add_argument('-o', '--output_file', required=False,
                    help='Name or path to an output csv file. If no output file is provide, output will be printed to the screen.')
args = parser.parse_args()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

api = ApiSession(config)

# Get segments
collections = api.get('collections')['content']
user_collections = [x for x in collections if x['owner'] == 'USER']
host_segments = [x for x in user_collections if x['query']['type'] == 'HOST']
perimeters = api.get('perimeters')['content']

# Define buckets of policies
autoseg_buckets = {
    'inbound': [
        'GUM_TO_TARGET',
        'LUM_TO_TARGET',
        'MANAGED_TO_TARGET',
    ],
    'outbound': [
        'TARGET_TO_GUM',
        'TARGET_TO_LUM',
        'TARGET_TO_MANAGED',
    ],
    'internal': [
        'TARGET_TO_TARGET',
    ],
}

requiring_resegment = set()
for segment in host_segments:

    # Check the segment perimeter config and modify the autoseg buckets accordingly
    perimeter = [x for x in perimeters if x['target']['id'] == segment['id']]
    if perimeter:
        perimeter = perimeter[0]
    else:
        continue # break out of the loop, no perimeter set
    buckets = []
    enforcement_actions = ['BLOCK', 'SIMULATE_BLOCK']
    if perimeter['inboundAction'] in enforcement_actions:
        buckets.extend(autoseg_buckets['inbound'])
    if perimeter['outboundAction'] in enforcement_actions:
        buckets.extend(autoseg_buckets['outbound'])
    if perimeter['internalAction'] in enforcement_actions:
        buckets.extend(autoseg_buckets['internal'])

    print(f"Checking segment'{segment['name']}'")

    # Determine the start time (sinceAutoSegTime)
    if args.all_time:
        timestamp = None
    elif args.custom_timestamp:
        # Custom timestamp format: 2020-10-10 10:10:10
        # autoSegTime format: 2021-11-11 12:24:11.048+0000
        t = dateutil.parser.isoparse(' '.join(args.custom_timestamp))
        timestamp = str(t.strftime('%Y-%m-%d %H:%M:%S.%f%z')[:-3]) + '+0000'
    else:
        timestamp = segment['autoSegTime']
        if not timestamp:
            print(f"  Skipping segment due to None timestamp. Is this segment Auto-Segmented?")
            continue

    # Check applicable policy buckets for the segment
    for bucket in buckets:
        print(f"  Checking bucket '{bucket}'")
        if timestamp:
                # Use this url if a timestamp is provided
                url = 'paths/unassigned-paths?targetId={}&autoSegBucket={}&sinceAutoSegTime={}'.format(
                segment['id'], 
                bucket, 
                urllib.parse.quote(timestamp),
            )
        else: 
            # Use this url if a timestamp is NOT provided
            url = 'paths/unassigned-paths?targetId={}&autoSegBucket={}'.format(
                segment['id'], 
                bucket, 
            )
        response = api.get(url)
        if response['content']:
            print(f"    {len(response['content'])} paths found")
            requiring_resegment.add(segment['name'])

# Export or print data
data = requiring_resegment
if requiring_resegment:
    if args.output_file:
        print(f"\nExporting to file '{args.output_file}'")
        output_file = args.output_file.rsplit('/', 1)
        if len(output_file) > 1:
            output_dir = output_file[0]
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        with open('{}'.format(args.output_file), 'w', newline='') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow([row])
    else:
        print("\nSegments requiring Auto-Resegment:")
        for x in requiring_resegment:
            print(x)
