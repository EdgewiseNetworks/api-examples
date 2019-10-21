#!/usr/bin/env python
#
# Copyright 2019 Edgewise Networks
# SPDX-License-Identifier: Apache-2.0
#

import requests

site_id = ''
username = ''
password = ''
cert_file = '/path/to/cert.pem'
key_file = '/path/to/key.pem'

agent_operation = 'UPGRADE'

# Authenticate
response = requests.post(
    url='https://console.edgewise.services/auth/login',
    json={'username': username, 'password': password},
    cert=(cert_file, key_file),
)
response.raise_for_status()
access_token = response.json()['accessToken']

# Get agents info
response = requests.get(
    url='https://console.edgewise.services/api/v1/sites/{}/agents'.format(site_id),
    headers={'authorization': 'Bearer %s' % access_token},
    cert=(cert_file, key_file),
)
response.raise_for_status()
agents = [{'id': x['id'], 'name':x['name']} for x in response.json()]

# Prepare agents for operation
if agent_operation in ['UPGRADE', 'UNINSTALL']:
    for agent in agents:
        try:
            response = requests.put(
                url='https://console.edgewise.services/api/v1/sites/{}/agents/{}/config'.format(site_id, agent['id']),
                headers={'authorization': 'Bearer %s' % access_token},
                json={'configOptions': [{'name': 'AgentTerminationProtection', 'value': 0, 'type': 'int'}]},
                cert=(cert_file, key_file),
            )
            response.raise_for_status()
        except:
            print("Failed to prepare agent on host '{}' for operation '{}', skipping...".format(agent['name'], agent_operation))
            agents[:] = [x for x in agents if x.get('id') != agent['id']]

# Perform operation
for agent in agents:
    print("Running operation '{}' for agent on host '{}'".format(agent_operation, agent['name']))
    try:
        response = requests.post(
            url='https://console.edgewise.services/api/v1/sites/{}/agents/{}/operation'.format(site_id, agent['id']),
            headers={'authorization': 'Bearer %s' % access_token},
            json={'siteId': site_id, 'name': agent['name'], 'targetId': agent['id'], 'operation': agent_operation},
            cert=(cert_file, key_file),
        )
        response.raise_for_status()
    except:
        print("Failed operation '{}' for agent on host '{}'".format(agent_operation, agent['name']))
