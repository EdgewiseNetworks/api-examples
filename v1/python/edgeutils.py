#!/usr/bin/python
#
# Copyright 2019 Edgewise Networks
# SPDX-License-Identifier: Apache-2.0
#

import requests
from getpass import getpass
from urllib.parse import urlparse
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class ApiSession:
    def __init__(self, config):
        self.site_id = config['site_id']
        self.username = self._get_username(config)
        self.password = self._get_password(config)

        self.url_root = config['url_root']
        self.url_auth = self.url_root + '/auth/login'
        self.url_api = self.url_root + '/api/v1/sites/{}'.format(self.site_id)

        self.session = self._session()
        self.session.cert = (config['cert_file'], config['key_file'])
        self.session.headers.update({'authorization':'Bearer %s' % self._authenticate()})

    def get(self, url, page=0, size=10000):
        if not self._is_url(url):
            if '?' in url:
                separator = '&'
            else:
                separator = '?'
            url = self.url_api + '/{}{}page={}&size={}'.format(url, separator, page, size)        
        response = self.session.get(url=url)
        response.raise_for_status()
        return response.json()

    def put(self, url, payload):
        if not self._is_url(url):
            url = self.url_api + '/{}'.format(url)
        response = self.session.put(url=url, json=payload)
        response.raise_for_status()
        if not response.text:
            return
        return response.json()

    def post(self, url, payload):
        if not self._is_url(url):
            url = self.url_api + '/{}'.format(url)
        response = self.session.post(url=url, json=payload)
        response.raise_for_status()
        if not response.text:
            return
        return response.json()

    def delete(self, url):
        if not self._is_url(url):
            url = self.url_api + '/{}'.format(url)
        response = self.session.delete(url=url)
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

    def _get_username(self, config):
        if config['username']:
            return config['username']
        else:
            return str(input("Username (e.g. 'user@domain.com'): "))
    
    def _get_password(self, config):
        if config['password']:
            return config['password']
        else:
            return str(getpass())
    
    def _authenticate(self):
        response = self.session.post(
            url=self.url_auth,
            json={'username':self.username, 'password':self.password},
        )
        response.raise_for_status()
        return response.json()['accessToken']

    def _session(self):
        session = requests.Session()
        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        session.mount('http://', HTTPAdapter(max_retries=retries))
        return session

