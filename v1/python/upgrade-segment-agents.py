#!/usr/bin/env python
#
# Copyright 2020 Edgewise Networks
# SPDX-License-Identifier: Apache-2.0
#

import yaml
import argparse
from requests.exceptions import HTTPError
from edgeutils import ApiSession

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--segment_name', required=True,
                    help='Name of the host segment to modify.')
args = parser.parse_args()

agent_operation = 'UPGRADE'

with open('config.yaml') as f:
    config = yaml.safe_load(f)

api = ApiSession(config)

# Get segments
collections = api.get('collections')['content']
user_collections = [x for x in collections if x['owner'] == 'USER']
segments = [x for x in user_collections if x['query']['type'] == 'HOST']

# Verify that the supplied segment exists
segment_names = [x['name'] for x in segments]
if args.segment_name not in segment_names:
    raise Exception("Supplied segment '{}' was not found. Valid segments are: \n{}".format(
        args.segment_name, 
        segment_names
    ))

# Find the correct segment
segment = next((x for x in segments if x['name'] == args.segment_name), None)
if not segment:
    raise Exception('Failed to get required information about the supplied host segment')

# Get segment hosts
r = api.get('scopes/{}/scope-data?scopeType=COLLECTION'.format(segment['id']))
hosts = [x['name'] for x in r['childScopes'] if x['type'] == 'HOST']

# Get agents for segment hosts
r = api.get('agents')
agents = [{'id': x['id'], 'name':x['name'], 'status':x['status']} for x in r if x['name'] in hosts]

# Prepare agents for operation
if agent_operation in ['UPGRADE', 'UNINSTALL']:
    for agent in agents:
        if agent['status'] == 'CONNECTED':
            payload = {'configOptions': [{'name': 'AgentTerminationProtection', 'value': 0, 'type': 'int'}]}
            api.put('agents/{}/config'.format(agent['id']), payload)
            print("Disabled termination protection on host '{}'".format(agent['name']))

# Perform operation
for agent in agents:
    if agent['status'] == 'CONNECTED':
        try:
            payload = {'siteId': config['site_id'], 'name': agent['name'], 'targetId': agent['id'], 'operation': agent_operation}
            api.post('agents/{}/operation'.format(agent['id']), payload)
            print("Successfully ran '{}' command on host '{}'".format(agent_operation, agent['name']))
        except HTTPError:
            print("Failed to run '{}' command on host '{}'. Is it already upgraded?".format(agent_operation, agent['name']))

