import pytest
import h2osteam
import requests
import os

steam_url = 'https://%s:9555' % os.environ['SERVER']


class TestLoginFunctions:
    def test_login_ssl_error(self):
        with pytest.raises(requests.exceptions.ConnectionError):
            h2osteam.login(url=steam_url,
                           username='admin',
                           password='adminadmin',
                           verify_ssl=True)

    def test_bad_cert_error(self):
        with pytest.raises(IOError):
            h2osteam.login(url=steam_url,
                           username='admin',
                           password='adminadmin',
                           verify_ssl=True,
                           cacert='/cert.pem')
