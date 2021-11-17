#!/usr/bin/python
#
# Copyright 2021 Zscaler
# SPDX-License-Identifier: Apache-2.0
#

"""
This script can be used to create and update host segments via API. This script
reads in a CSV file formatted with columns SegmentName and ServerName.
"""

import csv
import yaml
import time
import argparse
from edgeutils import ApiSession

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dry_run', action='store_true',
                    help='Prints the output but does not run the create or update commands.')
parser.add_argument('-f', '--force_missing', action='store_true',
                    help='Creates segments even if some agents are missing.')
parser.add_argument('-m', '--missing', action='store_true',
                    help='Print list of missing hosts.')
args = parser.parse_args()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

api = ApiSession(config)

# Get existing host segments
existing_collections = api.get('collections')['content']
existing_segments = [x for x in existing_collections if ((x['owner'] == 'USER') and (x['query']['type'] == 'HOST'))]

# Get existing agents
existing_agents = api.get('agents')

# Read in data from csv
input_data = {}
with open('update-host-segments.csv', mode='r', encoding='utf-8-sig') as f:
    csv_reader = csv.DictReader(f, dialect='excel')
    for row in csv_reader:
        if row['SegmentName'] not in input_data.keys():
            # Use the FQDN. Will parse out domain later on to handle cases where we 
            # don't know the format in ZWS
            input_data[row['SegmentName'].strip()] = [row['ServerName'].strip()]
        else:
            input_data[row['SegmentName']].append(row['ServerName'].strip())

# Iterate data from csv
missing_agents = []
for segment_name, server_list in input_data.items():

    if segment_name == '':
        continue  # No segment name, skip

    server_list = [x.lower() for x in server_list]

    # This following list is tricky to build because of FQDNs vs friendly hostnames
    agent_list = [{'id': x['id'], 'name': x['name']} for x in existing_agents if ((x['name'].lower() in server_list) or (x['name'].lower() in [x.split('.')[0].lower() for x in server_list]))]

    # If empty agent list
    if len(agent_list) < 1:
        continue

    # If not enough agents
    if not args.force_missing:
        if len(agent_list) < len(server_list):
            # Note, we use less than here to accomodate cases where 
            # there are two registered for the same host
            available = [x for x in server_list if x in [x['name'].lower() for x in existing_agents]]
            missing = [x for x in server_list if x not in [x['name'].lower() for x in existing_agents]]
            print("Agent list for segment '{}' does not contain all required hosts. No action will be taken.\n  Available: {}\n  Missing: {}".format(
                segment_name, 
                available, 
                missing,
                ))
            missing_agents.extend(missing)
            continue  # Incomplete agent list, skip

    # If a new segment
    if segment_name not in [x['name'] for x in existing_segments]:
        print("Segment '{}' does not exist. Creating a new segment and adding hosts {}.".format(segment_name, [x['name'] for x in agent_list]))
        payload = {'type': 'COLLECTION', 'name': segment_name, 'dynamic': True, 'query': {'type': 'HOST', 'hosts': agent_list}}
        if not args.dry_run:
            response = api.post('collections', payload)
            print("  Done")

    # If an existing segment
    else:
        print("Segment '{}' exists. Setting host list to: {}".format(segment_name, [x['name'] for x in agent_list]))
        existing_segment = [x for x in existing_segments if x['name'] == segment_name][0]
        payload = {'type': 'COLLECTION', 'id': existing_segment['id'], 'name': segment_name, 'dynamic': True, 'query': {'type': 'HOST', 'hosts': agent_list}}
        if not args.dry_run:
            response = api.put('collections/{}'.format(existing_segment['id']), payload)
            print("  Done")

if args.missing and missing_agents:
    print("\nAll missing: {}".format(missing_agents))
