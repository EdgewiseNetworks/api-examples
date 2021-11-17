#!/usr/bin/python
#
# Copyright 2021 Zscaler
# SPDX-License-Identifier: Apache-2.0
#

"""
This script can be used to create and update network segments via API. This script
reads in a CSV file formatted with columns Name and CIDR.
"""

import csv
import yaml
import pprint
import argparse
from ipaddress import IPv4Network
from edgeutils import ApiSession

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dry_run', action='store_true',
                    help='Prints the output but does not run the create or update commands.')
args = parser.parse_args()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

api = ApiSession(config)

# Read in CSV
network_segments = {}
with open('update-network-segments.csv', mode='r', encoding='utf-8-sig') as f:
    csv_reader = csv.DictReader(f, dialect='excel')
    for row in csv_reader:
        
        name = row['Name'].strip()
        cidr = row['CIDR'].strip()

        if '/' not in cidr:
            cidr = cidr + '/32'

        try:
            cidr = IPv4Network('{}'.format(cidr))
        except Exception as e:
            print("Failed to convert {} to CIDR: {}".format(cidr, e))
        
        if name not in network_segments.keys():
            network_segments[name] = [cidr]
        else:
            network_segments[name].append(cidr)

# If dry_run, print the pending changes and exit
if args.dry_run:
    pprint.pprint(network_segments)
    exit()

for name, addresses in network_segments.items():
    # Create or update networks
    print("\nCreating segment {}".format(name))
    print("Creating networks {}".format(addresses))

    # payload = [{'cidrBlock': str(segment['cidr']), 'type': 'NETWORK'}]
    payload = [{'cidrBlock': str(x), 'type': 'NETWORK'} for x in addresses]
    response = api.post('networks', payload)


    # Get existing network segments, see if there is a name match, get ID
    netseg_id = [x['id'] for x in api.get('network-segments')['content'] if x['name'].lower() == name.lower()]

    # Create or overwrite network segment
    if netseg_id:
        netseg_id = netseg_id[0]
        payload = {'name': name, 'networks': response, 'type': 'NETWORK_SEGMENT', 'loadBalancer': False}
        response = api.put('network-segments/{}'.format(netseg_id), payload)
    else:
        payload = {'name': name, 'networks': response, 'type': 'NETWORK_SEGMENT', 'loadBalancer': False}
        response = api.post('network-segments', payload)
    print("Done")
