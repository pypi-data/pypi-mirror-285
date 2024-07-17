# -*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import time
import json
import logging
import h2osteam
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from h2osteam.backend.api import SteamApi
from h2osteam.utils import (ProgressBar, get_filename_from_path)

requests.packages.urllib3.disable_warnings()


class SteamConnection(SteamApi):
    def __init__(self):
        self._uid = 0
        self._username = None
        self._password = None
        self._requests_verify_ssl = True

        self.scheme = None
        self.host = None
        self.path = None
        self.port = None
        self.verify_ssl = True
        self.cacert = None
        self.cookie = None

    @staticmethod
    def open(scheme=None, host=None, path=None, port=None, username=None, password=None, verify_ssl=True, cacert=None, access_token=None, refresh_token=None):
        conn = SteamConnection()
        conn._username = username
        conn._password = password

        conn.scheme = scheme
        conn.host = host
        conn.path = path
        conn.port = port
        conn.verify_ssl = verify_ssl
        conn.cacert = cacert

        requests_verify_ssl = False
        if verify_ssl is True and cacert is not None:
            requests_verify_ssl = cacert
        if verify_ssl is True and cacert is None:
            requests_verify_ssl = True
        conn._requests_verify_ssl = requests_verify_ssl

        res = requests.request('POST', '%s://%s:%s%s/auth' % (scheme, host, port, path),
                               data={'access_token': access_token, 'refresh_token': refresh_token},
                               auth=(username, password),
                               verify=requests_verify_ssl,
                               allow_redirects=False)

        if res.status_code != 200 and res.status_code != 307:
            raise HTTPError(res.status_code, res.content.decode())

        if "steam-session" not in res.cookies:
            raise Exception("Invalid URL path")

        conn.cookie = res.cookies["steam-session"]

        return conn

    def check_connection(self):
        server_api_version = self.ping_server('Python connect')
        if server_api_version != h2osteam.__version__ and h2osteam.__version__ != "SUBST_PACKAGE_VERSION":
            raise Exception(
                "Client API version '%s' does not match server API version '%s'" % (
                    h2osteam.__version__, server_api_version))

    def call(self, method, params):
        self._uid = self._uid + 1
        request = {
            'id': self._uid,
            'method': 'web.' + method,
            'params': [params]
        }
        payload = json.dumps(request)
        header = {
            'User-Agent': 'Enterprise Steam Python Client',
            'Content-type': 'application/json; charset="UTF-8"',
            'Content-length': '%d' % len(payload),
        }

        res = requests.request('POST', '%s://%s:%s%s/%s' % (self.scheme, self.host, self.port, self.path, 'web'),
                               cookies={"steam-session": self.cookie},
                               data=payload,
                               verify=self._requests_verify_ssl,
                               headers=header)

        # RPC communication error
        if res.status_code != 200:
            logging.exception('%s %s %s', res.status_code, res.reason, res.content)
            res.close()
            raise HTTPError(res.status_code, res.reason)

        response = res.json()
        res.close()
        error = response['error']

        if error is None:
            result = response['result']
            return result
        else:
            logging.exception(error)
            raise RPCError(error)

    def upload(self, target, path, payload):
        encoder = create_upload(path, payload)
        callback = create_callback(encoder)
        monitor = MultipartEncoderMonitor(encoder, callback)
        res = requests.post('%s://%s:%s%s%s' % (self.scheme, self.host, self.port, self.path, target),
                            cookies={"steam-session": self.cookie},
                            verify=self._requests_verify_ssl,
                            data=monitor,
                            headers={'Content-Type': monitor.content_type})

        if res.status_code != 200:
            logging.exception('%s %s %s', res.status_code, res.reason, res.content)
            res.close()
            raise HTTPError(res.status_code, res.reason)

    def download(self, target, path):
        res = requests.get('%s://%s:%s%s%s' % (self.scheme, self.host, self.port, self.path, target),
                           cookies={"steam-session": self.cookie},
                           verify=self._requests_verify_ssl)

        if res.status_code != 200:
            # forbidden error do not log stack trace
            if res.status_code != 403 and res.status_code != 204:
                logging.exception('%s %s %s', res.status_code, res.reason, res.content)
            res.close()
            raise HTTPError(res.status_code, res.reason)

        if len(res.content) != 0:
            open(path, 'wb').write(res.content)

    def requests_verify(self):
        return self._requests_verify_ssl


class HTTPError(Exception):
    def __init__(self, code, value):
        self.value = value
        self.code = code

    def __str__(self):
        return repr('%s: %s' % (self.code, self.value))


class RPCError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def create_callback(encoder):
    encoder_len = encoder.len
    bar = ProgressBar(expected_size=encoder_len, filled_char='=')

    def callback(monitor):
        bar.show(monitor.bytes_read)

    return callback


def create_upload(path, payload):
    multipart = {'file': (get_filename_from_path(path), open(path, 'rb'))}
    if payload is not None:
        multipart.update(payload)

    return MultipartEncoder(multipart)
