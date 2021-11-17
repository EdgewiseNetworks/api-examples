#!/usr/bin/python
#
# Copyright 2021 Zscaler
# SPDX-License-Identifier: Apache-2.0
#

import yaml
import argparse
from edgeutils import ApiSession

with open('config.yaml') as f:
    config = yaml.safe_load(f)

api = ApiSession(config)

name_modifier = 'AS'

# Get existing host segments
existing_collections = api.get('collections')['content']
existing_segments = [x for x in existing_collections if ((x['owner'] == 'USER') and (x['query']['type'] == 'HOST_APP'))]

# Update segment names
for segment in existing_segments:
    if segment['name'].startswith('{}-'.format(name_modifier)):
        continue
    payload = {
        'type': 'COLLECTION',
        'id': segment['id'],
        'name': '{}-{}'.format(name_modifier, segment['name']),
        'dynamic': segment['dynamic'],
        'query': segment['query'],
        }
    response = api.put('collections/{}'.format(segment['id']), payload)
