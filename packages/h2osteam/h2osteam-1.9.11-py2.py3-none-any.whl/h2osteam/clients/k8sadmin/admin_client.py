import time
import json
import logging
import h2osteam
import requests
from h2osteam.backend import TypedSteamConnection


class KubernetesAdminClient:
    def __init__(self):
        self.conmn = None

    def login(self, url=None, username=None, password=None, verify_ssl=True, cacert=None, access_token="",
              refresh_token="",
              no_proxy=True):
        """
        Connect to an existing Enterprise Server server.

        There are two ways to pass password to a server: either pass a `server` parameter containing an instance of
        an H2OLocalServer, or specify `ip` and `port` of the server that you want to connect to.

        You may pass either OpenID access or refresh token. Refresh token is recommended.

        :param url: Full URL (including schema and port) of the Steam server to connect to. Must use https schema.
        :param username: Username of the connecting user.
        :param password: Password of the connecting user or access token.
        :param verify_ssl: Setting this to False will disable SSL certificates verification.
        :param cacert: (Optional) Path to a CA bundle file or a directory with certificates of trusted CAs.
        :param access_token: Access token
        :param refresh_token: OpenID refresh token
        :param no_proxy: If True, sets or appends environmental variables `no_proxy` and `NO_PROXY` with Steam hostname
        before doing any network requests.

        :examples:

        >>> import h2osteam
        >>> url = "https://steam.example.com:9555"
        >>> username = "AzureDiamond"
        >>> password = "hunter2"
        >>> h2osteam.login(url=url, username=username, password=password, verify_ssl=True)
        >>> # or using an access token retrieved from the Web Client
        >>> h2osteam.login(url="https://steam.example.com:9555", access_token="SyzjffQAcYgz6Nk...")
        >>> # or using a refresh token
        >>> h2osteam.login(url="https://steam.example.com:9555", refresh_token="KdO2KdntsON9a...")

        """

        if url is None or url == "":
            raise Exception("Parameter 'url' must be set")

        if (access_token is None or access_token == "") and (refresh_token is None or refresh_token == ""):
            if password is None or password == "":
                raise Exception("Parameter 'password' must be set")

        parsed_url = requests.utils.urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        scheme = parsed_url.scheme

        if host is None:
            raise Exception("Unable to parse URL")
        if port is None and scheme == "http":
            port = 80
        if port is None and scheme == "https":
            port = 443
        if password is None:
            password = ""
        if access_token is None:
            access_token = ""
        if refresh_token is None:
            refresh_token = ""

        self.conn = TypedSteamConnection.open(scheme=scheme,
                                              host=host,
                                              port=port,
                                              username=username,
                                              password=password,
                                              verify_ssl=verify_ssl,
                                              cacert=cacert,
                                              access_token=access_token,
                                              refresh_token=refresh_token)

    def test(self):
        return self.conn.get_driverless_engines()

