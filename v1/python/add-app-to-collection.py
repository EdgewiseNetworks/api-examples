#!/usr/bin/python
#
# Copyright 2019 Edgewise Networks
# SPDX-License-Identifier: Apache-2.0
#

import yaml
import argparse
from edgeutils import ApiSession

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--collection_name', required=True,
                    help='Name of the app collection to modify.')
parser.add_argument('-a', '--app_name', required=True,
                    help='Name of the app to add to the collection.')
parser.add_argument('-H', '--app_hash',
                    help='SHA256 hash of the app to add to the collection.')
parser.add_argument('-s', '--simulated', action='store_true',
                    help='Actions are simulated. No changes are made.')
parser.add_argument('-f', '--force', action='store_true',
                    help='Force a re-evalution of the collection membership.')
args = parser.parse_args()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

api = ApiSession(config)


#### New app checks ####

# Check for matching apps
url = 'scopes/inbound/scope-stats?appNames={}&scopeType=HOST_APP'.format(args.app_name)
apps = api.get(url)['content']
if not apps:
    raise Exception("No app instances found for name: {}".format(args.app_name))

app_hashes = {}
for app in apps:
    id = app['scope']['id'].split(':', 1)[-1]
    features = api.get('apps/{}'.format(id))
    app_hashes[id] = features['features']['FILE_SHA256']

# Check that if a hash is provided, it is known to Edgewise
if args.app_hash:
    if args.app_hash not in app_hashes.values():
        raise Exception("App SHA256 not indexed. \
                         Ensure app has run on an Edgewise managed host.")


#### Collection checks ####

# Check for matching collection
collections = [x for x in api.get('collections')['content'] if x['name'] == args.collection_name]
if not collections:
    raise Exception("No collection found with name: {}".format(args.collection_name))
collection = collections[0]

# Check if collection is user managed
if collection['owner'] != 'USER':
    raise Exception("Collection is not user owned")

# Check if collection type is app collection
if collection['query']['type'] != 'HOST_APP':
    raise Exception("Collection is not type app collection")

# Check if app is already in the collection
if args.app_name in collection['query']['appNames']:
    print("App is already a member of collection: {}".format(args.collection_name))
    if args.force:
        print("Force flag used. Continuing...")
    else:
        print("Use --force to override")
        exit()


#### Review current collection apps ####

url = 'collections/{}/scopes/inbound/scope-stats'.format(collection['id'])
scopes = api.get(url)['content']

# Build the list of collection apps before making any changes
apps_before = []
for scope in scopes:
    id = scope['scope']['id'].split(':',1)[-1]
    features = api.get('apps/{}'.format(id))
    hash = features['features']['FILE_SHA256']
    apps_before.append('{}:{}'.format(id, hash))


#### Update collection ####

current = collection['query']['appNames']
collection['query']['appNames'] = current + [args.app_name]
if not args.simulated:
    api.put('collections/{}'.format(collection['id']), collection)


#### Compare collection apps before-after ####

if not args.simulated:
    # Get a fresh collection app list
    url = 'collections/{}/scopes/inbound/scope-stats'.format(collection['id'])
    scopes = api.get(url)['content']
else:
    # No point in querying the API again, collection
    # membership is not changed in simulated mode
    scopes = apps

# Build the list of collection apps that were added or simulated added
apps_after = []
for scope in scopes:
    id = scope['scope']['id'].split(':',1)[-1]
    features = api.get('apps/{}'.format(id))
    hash = features['features']['FILE_SHA256']
    apps_after.append('{}:{}'.format(id, hash))

# Check for no-op
if apps_before == apps_after:
    print("Collection apps list before and after match. No change was made.")
    exit()

# Do a detailed before-after comparison
app_diff = [x for x in apps_after if x not in apps_before]
if app_diff:
    for app in app_diff:
        id, hash = app.split(':', 1)
        features = api.get('apps/{}'.format(id))
        print("Added app instance")
        print("  App name: {}".format(features['name']))
        print("  SHA256: {}".format(hash))
        if args.app_hash and hash != args.app_hash:
            print("\nWARNING: hash of app added does not match provided app_hash. \
                   Manually review colleciton membership.\n")
        print()
else:
    print("Collection app membership diff shows no change")
