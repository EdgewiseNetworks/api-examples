#!/usr/bin/python
#
# Copyright 2019 Edgewise Networks
# SPDX-License-Identifier: Apache-2.0
#

import pprint
import requests

cert_file = '/path/to/cert.pem'
key_file = '/path/to/key.pem'

headers = {"Authorization":"Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xljjEiYXBpX3VzZXIiLCJ1c2VyX25hbWUiOiJkZW1vQHRydXN0ZWRhcHAuaW8iLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSavVnVsbE5hbWUiOiJEZW1vIiwic2l0ZXMiOlsiOWIwNDFmNTEtOTU4MC00NmU5LThlNjAtZmNjMzk5MWQ1MmI5Il0sImV4cCI6MTU1OTU3Mzc3NCwiYXV0aG9yaXRpZXMiOlsiUk9MRV9BRE1JTiIsInVzZXI6MzU4YWY2YTQtYjBkNS00OTRmLTliYjctZGFhZTljYTFiNWM3IiwiQVBJX1VTRVIiLCJST0xFX0JFVEEiLCJjdXN0b21lcjphMjMzYWM0Yi1jMGY2LTQyMzQtOTFkNy0yOWI0YTc3NmFmZDciLCJzaXRlOjliMDQxZjUxLTk1ODAtNDZlOS04ZTYwLWZjYzM5OTFkNTJiOSJdLCJqdGkiOiJmNzQ3NzQ0NS03MjE2LTRiYjEtODIyYS0wZDg0MzAwNmQxY2UiLCJjbGllbnRfaWQiaFllZGdlYXBwIiwiY3VzdG9tZXIiOiJhMjMzYWM0Yi1jMGY2LTQyMzQtOTFkNy0yOWI0YTc3NmFmZDcifQ.edyZ_SxwlE_PS3l7VNbYFmgI9hAilm0DdLpRZqvD8pfPuqSI7K6H2TrTOyqkdtYaUEjLZKl299p-Du7QmUwd9TxIdJRozx6k81BtjP4CKS-aqsQZi2bUOk9yQHtzYwHKrYi6Fv0nL6QgsZH2BC9GjpUzW5TweKsWuQyjG8u7X1U0ptx6XRTmb9lO2JH5HSWaxbOEG0iJOiumnc4zamoLiQlrZSyLqb3mIXKdyvYI_LbR2YCW-Cl-jRkvCX9-JARYgkWs52lORhn7Ak5M63me_XlEo7zLRs03AaXc8ayL2M05IcJX6GTaSUoNelZH0oG56o9Lc6STRkNZ0Yp-vJZzwA"}

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
