#!/usr/bin/python
#
# Copyright 2020 Edgewise Networks
# SPDX-License-Identifier: Apache-2.0
#

import yaml
import argparse
from edgeutils import ApiSession

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--segment_name', required=True,
                    help='Name of the host segment to modify.')
parser.add_argument('-H', '--hosts_list', required=True,
                    help='Name of the hosts to add to the segment. Comma separated list.',
                    type=str)
group = parser.add_mutually_exclusive_group()
group.add_argument('-u', '--update', action='store_true',
                    help='If host segment exists, merge hosts_list with list of existing hosts.')
group.add_argument('-f', '--force', action='store_true',
                    help='If host segment exists, replace existing hosts with hosts_list.')
args = parser.parse_args()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

api = ApiSession(config)

# Get new hosts
hosts = api.get('agents')
arg_hosts_list = [x.strip().lower() for x in args.hosts_list.split(',')]
new_hosts = [{'id': x['id']} for x in hosts if x['name'].lower() in arg_hosts_list]

# Get segments
collections = api.get('collections')['content']
user_collections = [x for x in collections if x['owner'] == 'USER']
segments = [x for x in user_collections if x['query']['type'] == 'HOST']

# Get existing segment, if specified, else None
segment = next((x for x in segments if x['name'] == args.segment_name), None)

# Update/overwrite if exists else create segment
response = None
if segment:
    print("Existing segment '{}' found".format(args.segment_name))
    payload = {}

    # Update the segment if exists and update flag is True
    if args.update:
        print('Updating segment hosts list')
        r = api.get('scopes/{}/scope-data?scopeType=COLLECTION'.format(segment['id']))
        existing_hosts = [{'id': x['id']} for x in r['childScopes'] if x['type'] == 'HOST']
        all_hosts = [*existing_hosts, *new_hosts]
        payload = {'type': 'COLLECTION', 'id': segment['id'], 'name': args.segment_name, 'query': {'type': 'HOST', 'hosts': all_hosts}}

    # Overwrite the segment if exists and force flag is True
    elif args.force:
        print('Overwriting segment hosts list')
        payload = {'type': 'COLLECTION', 'id': segment['id'], 'name': args.segment_name, 'query': {'type': 'HOST', 'hosts': new_hosts}}

    # Error out if segment exists but no update or force flag set
    else:
        raise Exception('Existing segment found, modifying it requires either update or force flag but none set')

    # Execute the update/overwrite
    response = api.put('collections/{}'.format(segment['id']), payload)

else:
    # Create the new segment
    print("Segment '{}' does not exist\nCreating a new segment".format(args.segment_name))
    payload = {'type': 'COLLECTION', 'name': args.segment_name, 'dynamic': True, 'query': {'type': 'HOST', 'hosts': new_hosts}}
    response = api.post('collections', payload)

# Verify and print result
result_hosts = [x['name'].lower() for x in hosts if x['id'] in [y['id'] for y in response['query']['hosts']]]
print("Segment '{}' now contains hosts: {}".format(response['name'], sorted(result_hosts))) 

