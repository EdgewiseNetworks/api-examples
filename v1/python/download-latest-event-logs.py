#!/usr/bin/python
#
# Copyright 2019 Edgewise Networks
# SPDX-License-Identifier: Apache-2.0
#

import os
import glob
import requests

site_id = ''
username = ''
password = ''
cert_file = '/path/to/cert.pem'
key_file = '/path/to/key.pem'
logs_dir = './logs'

# Authenticate
response = requests.post(
    url = 'https://console.edgewise.services/auth/login',
    json={'username':username, 'password':password},
    cert=(cert_file, key_file),
)
response.raise_for_status()
access_token = response.json()['accessToken']

# Get event logs list, sort, and limit to newest 5
response = requests.get(
    url = 'https://console.edgewise.services/api/v1/sites/{}/audit-event-exports/recent'.format(site_id),
    headers = {'authorization':'Bearer %s' % access_token},
    cert=(cert_file, key_file),
)
response.raise_for_status()
event_logs = sorted(response.json(), key=lambda x: x['filename'])[-5:]

# Get local logs and drop these entries from event logs list
local_logs = [x.strip('./') for x in glob.glob('{}/audit_events.*.json'.format(logs_dir))]
event_logs = [x for x in event_logs if x['filename'] not in local_logs]

# Download new log files to logs_dir
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
for event_log in event_logs:
    response = requests.get(event_log['url'])
    with open('{}/{}'.format(logs_dir, event_log['filename']), 'wb') as f:
        f.write(response.content)
        print("Wrote log '{}'".format(event_log['filename']))
