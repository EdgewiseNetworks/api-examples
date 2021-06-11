#!/usr/bin/python
#
# Copyright 2019 Edgewise Networks
# SPDX-License-Identifier: Apache-2.0
#

import os
import glob
import requests
import yaml
from edgeutils import ApiSession

logs_dir = './logs'

with open('config.yaml') as f:
    config = yaml.safe_load(f)

api = ApiSession(config)

# Get event logs list, sort, and limit to newest 5
event_logs = api.get('audit-event-exports/recent')
event_logs = sorted(event_logs, key=lambda x: x['filename'])[-5:]

# Get local logs and drop these entries from event logs list
local_logs = [x.split('/')[-1] for x in glob.glob('{}/audit_events.*.json'.format(logs_dir))]
event_logs = [x for x in event_logs if x['filename'] not in local_logs]
print("Downloading {} latest logs.".format(len(event_logs)))
# Download new log files to logs_dir
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
for event_log in event_logs:
    response = requests.get(event_log['url'])
    with open('{}/{}'.format(logs_dir, event_log['filename']), 'wb') as f:
        f.write(response.content)
        print("Wrote log '{}'".format(event_log['filename']))
