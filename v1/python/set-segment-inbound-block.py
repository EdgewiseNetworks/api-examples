#!/usr/bin/env python
#
# Copyright 2021 Zscaler
# SPDX-License-Identifier: Apache-2.0
#

"""
This script can be used to update the inbound perimeter configuration for
a host segment. It will switch from a simulated block to a full block. 
If no host perimeter is configured then the script will error out.
"""

import yaml
import argparse
from edgeutils import ApiSession

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--segment_name', required=True,
                    help='Name of the host segment to inspect. If no host segment name is provided, all host segments will be returned.')
args = parser.parse_args()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

api = ApiSession(config)

# Get existing perimeter object. This will fail if no perimeter is set!
perimeter = [x for x in api.get('perimeters')['content'] if x['target']['name'] == args.segment_name][0]

# Remove sim block from existing perimeter and commit
perimeter['inboundAction'] = 'BLOCK'
response = api.put('perimeters/{}'.format(perimeter['id']), perimeter)

print("Name: {}".format(response['target']['name']))
print("Inbound policy: {}".format(response['inboundAction']))
print("Outbound policy: {}".format(response['outboundAction']))
print("Internal policy: {}".format(response['internalAction']))
