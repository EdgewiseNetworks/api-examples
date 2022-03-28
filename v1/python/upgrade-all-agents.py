#!/usr/bin/env python
#
# Copyright 2022 Zscaler
# SPDX-License-Identifier: Apache-2.0
#

import yaml
import argparse
from requests.exceptions import HTTPError
from edgeutils import ApiSession

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--count', required=False,
                    help='Perform this count of upgrades and then exit.')
args = parser.parse_args()

agent_operation = 'UPGRADE'

with open('config.yaml') as f:
    config = yaml.safe_load(f)

api = ApiSession(config)

# Get agents info
r = api.get('agents')
agents = [{'id': x['id'], 'name':x['name'], 'status':x['status']} for x in r if x['upgradePackage']]

if agent_operation in ['UPGRADE', 'UNINSTALL']:
    count = 0
    for agent in agents:
        if agent['status'] == 'CONNECTED':
            try:
                # Disable termination protection
                payload = {'configOptions': [{'name': 'AgentTerminationProtection', 'value': 0, 'type': 'int'}]}
                api.put('agents/{}/config'.format(agent['id']), payload)
                print("Disabled termination protection on host '{}'".format(agent['name']))
                
                # Perform operation
                payload = {'siteId': config['site_id'], 'name': agent['name'], 'targetId': agent['id'], 'operation': agent_operation}
                api.post('agents/{}/operation'.format(agent['id']), payload)
                print("Successfully ran '{}' command on host '{}'".format(agent_operation, agent['name']))
                count += 1
            except HTTPError:
                print("Failed to run '{}' command on host '{}'".format(agent_operation, agent['name']))
            if args.count:
                if count >= int(args.count):
                    break

