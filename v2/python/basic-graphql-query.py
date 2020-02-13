#!/usr/bin/python
#
# Copyright 2019 Edgewise Networks
# SPDX-License-Identifier: Apache-2.0
#

import pprint
import requests

cert_file = '/path/to/cert.pem'
key_file = '/path/to/key.pem'

headers = {"X-Api-Token":"<tokenSecret_string>”}
           
query = '''{
  agents {
    nodes {
      friendlyHostname
      status
    }
  }
}
'''

response = requests.post(
    url = 'https://console.edgewise.services/api/v2/graphql',
    json={'query': query},
    headers=headers,
    cert=(cert_file, key_file),
)
response.raise_for_status()
pprint.pprint(response.json())
