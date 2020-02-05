#!/usr/bin/python
#
# Copyright 2019 Edgewise Networks
# SPDX-License-Identifier: Apache-2.0
#

import requests
from urllib.parse import urlparse

class ApiSession:
    def __init__(self, config):
        self.site_id = config['site_id']
        self.username = config['username']
        self.password = config['password']
        self.cert = (config['cert_file'], config['key_file'])
        self.url_root = 'https://console.edgewise.services'
        self.url_auth = self.url_root + '/auth/login'
        self.url_api = self.url_root + '/api/v1/sites/{}'.format(self.site_id)
        self.access_token = self.authenticate()
        self.headers = {'authorization':'Bearer %s' % self.access_token}

    def authenticate(self):
        response = requests.post(
            url=self.url_auth,
            json={'username':self.username, 'password':self.password},
            cert=self.cert,
        )
        response.raise_for_status()
        return response.json()['accessToken']

    def get(self, url):
        if not self._is_url(url):
            url = self.url_api + '/{}'.format(url)
        response = requests.get(
            url=url,
            headers=self.headers,
            cert=self.cert,
        )
        response.raise_for_status()
        return response.json()

    def put(self, url, payload):
        if not self._is_url(url):
            url = self.url_api + '/{}'.format(url)
        response = requests.put(
            url=url,
            headers=self.headers,
            json=payload,
            cert=self.cert,
        )
        response.raise_for_status()
        if not response.text:
            return
        return response.json()

    def post(self, url, payload):
        if not self._is_url(url):
            url = self.url_api + '/{}'.format(url)
        response = requests.post(
            url=url,
            headers=self.headers,
            json=payload,
            cert=self.cert,
        )
        response.raise_for_status()
        if not response.text:
            return
        return response.json()

    def delete(self, url):
        if not self._is_url(url):
            url = self.url_api + '/{}'.format(url)
        response = requests.delete(
            url=url,
            headers=self.headers,
            cert=self.cert,
        )
        response.raise_for_status()
        if not response.text:
            return
        return response.json()

    def _is_url(self, url):
      try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
      except ValueError:
        return False
