# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import requests

from h2osteam.deprecated import SteamClient
from h2osteam.backend import SteamConnection
from h2osteam.utils import print_val as _print_val, print_profile_value as _print_value, set_env_no_proxy

conn = None  # type: SteamConnection


def login(url=None, username=None, password=None, verify_ssl=True, cacert=None, access_token="", refresh_token="",
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
    global conn

    if url is None or url == "":
        raise Exception("Parameter 'url' must be set")

    if (access_token is None or access_token == "") and (refresh_token is None or refresh_token == ""):
        if password is None or password == "":
            raise Exception("Parameter 'password' must be set")

    parsed_url = requests.utils.urlparse(url)
    host = parsed_url.hostname
    path = parsed_url.path.rstrip("/")
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

    if no_proxy is True:
        set_env_no_proxy(host=host)

    conn = SteamConnection.open(scheme=scheme,
                                host=host,
                                path=path,
                                port=port,
                                username=username,
                                password=password,
                                verify_ssl=verify_ssl,
                                cacert=cacert,
                                access_token=access_token,
                                refresh_token=refresh_token)

    return conn


def api():
    """
        Get direct access to the Steam API for expert users only.

        Expert users can bypass the clients for each product and access the Steam API directly.
        This use-case is not supported and not recommended! If possible use the provided clients!

        :examples:

        >>> import h2osteam
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> api = h2osteam.api()
        >>> api

    """
    if conn is None:
        raise Exception("You are not connected to the Steam server. Use h2osteam.login to establish connection.")
    return conn


def set_license(path=None, text=None):
    """
        Sets (or updates) Enterprise Steam license. The license can be provided either by specifying a path to a license
        file or providing license text in respective parameters.

        :param path: Path to a license file.
        :param text: License text. Ignored if path is provided.

        :examples:

        >>> import h2osteam
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="admin_user", password="token-here", verify_ssl=True)
        >>> h2osteam.set_license(path="/user/admin/license.sig")
        >>> # Or provide license text directly
        >>> h2osteam.set_license(text='''
        >>> license text...
        >>> ''')

    """

    if path is not None:
        conn.upload("/upload/steam/license", path, payload=None)
        return

    if text is not None:
        conn.set_license(text)


def print_profiles():
    """
        Prints profiles available to this user.

        Prints details about the profiles available to the logged-in user.

        :examples:

        >>> import h2osteam
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> h2osteam.print_profiles()
        >>> # Profile name: default-h2o
        >>> # Profile type: h2o
        >>> # Number of nodes: MIN=1 MAX=10
        >>> # Node memory [GB]: MIN=1 MAX=30
        >>> # Threads per node: MIN=0 MAX=0
        >>> # Extra memory [%]: MIN=10 MAX=50
        >>> # Max idle time [hrs]: MIN=1 MAX=24
        >>> # Max uptime [hrs]: MIN=1 MAX=24
        >>> # YARN virtual cores: MIN=0 MAX=0
        >>> # YARN queues:

    """
    profiles = conn.get_profiles()

    for profile in profiles:
        print("===")
        _print_val("Profile name", profile['name'])
        _print_val("Profile type", profile['profile_type'])
        if profile['profile_type'] == "h2o":
            _print_value("Number of nodes", profile['h2o']['h2o_nodes'])
            _print_value("CPUs per node", profile['h2o']['h2o_threads'])
            _print_value("YARN virtual cores", profile['h2o']['yarn_vcores'])
            _print_value("Node memory [GB]", profile['h2o']['h2o_memory'])
            _print_value("Extra node memory [%]", profile['h2o']['h2o_extramempercent'])

            _print_value("Max idle time [hrs]", profile['h2o']['max_idle_time'])
            _print_value("Max uptime [hrs]", profile['h2o']['max_uptime'])

            _print_val("YARN queues", profile['h2o']['yarn_queue'])
            _print_value("Start timeout [s]", profile['h2o']['start_timeout'])

        if profile['profile_type'] == "sparkling_internal":
            _print_value("Driver cores", profile['sparkling_internal']['driver_cores'])
            _print_value("Driver memory [GB]", profile['sparkling_internal']['driver_memory'])

            _print_value("Number of executors", profile['sparkling_internal']['num_executors'])
            _print_value("Executor cores", profile['sparkling_internal']['executor_cores'])
            _print_value("Executor memory [GB]", profile['sparkling_internal']['executor_memory'])

            _print_value("H2O threads per node", profile['sparkling_internal']['h2o_threads'])
            _print_value("Extra node memory [%]", profile['sparkling_internal']['h2o_extramempercent'])

            _print_value("Max idle time [hrs]", profile['sparkling_internal']['max_idle_time'])
            _print_value("Max uptime [hrs]", profile['sparkling_internal']['max_uptime'])

            _print_val("YARN queues", profile['sparkling_internal']['yarn_queue'])
            _print_value("Start timeout", profile['sparkling_internal']['start_timeout'])

        if profile['profile_type'] == "sparkling_external":
            _print_value("Driver cores", profile['sparkling_external']['driver_cores'])
            _print_value("Driver memory [GB]", profile['sparkling_external']['driver_memory'])

            _print_value("Number of executors", profile['sparkling_external']['num_executors'])
            _print_value("Executor cores", profile['sparkling_external']['executor_cores'])
            _print_value("Executor memory [GB]", profile['sparkling_external']['executor_memory'])

            _print_value("H2O nodes", profile['sparkling_external']['h2o_nodes'])
            _print_value("H2O CPUs per node", profile['sparkling_external']['h2o_threads'])
            _print_value("H2O node memory [GB]", profile['sparkling_external']['h2o_memory'])
            _print_value("Extra node memory [%]", profile['sparkling_external']['h2o_extramempercent'])

            _print_value("Max idle time [hrs]", profile['sparkling_external']['max_idle_time'])
            _print_value("Max uptime [hrs]", profile['sparkling_external']['max_uptime'])

            _print_val("YARN queues", profile['sparkling_external']['yarn_queue'])
            _print_value("Start timeout", profile['sparkling_external']['start_timeout'])


def print_python_environments():
    """
        Prints Sparkling Water Python environments available to this user.

        Prints details about Sparkling Water Python environments available to the logged-in user.

        :examples:

        >>> import h2osteam
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> h2osteam.print_python_environments()
        >>> # Name: Python 2.7 default
        >>> # Python Pyspark Path:
        >>> # Conda Pack path: lib/conda-pack/python-27-default.tar.gz
        >>> # ===
        >>> # Name: Python 3.7 default
        >>> # Python Pyspark Path:
        >>> # Conda Pack path: lib/conda-pack/python-37-default.tar.gz

    """

    envs = conn.get_python_environments()

    for env in envs:
        print("===")
        _print_val("Name", env['name'])
        _print_val("Python Pyspark Path", env['pyspark_python_path'])
        _print_val("Conda Pack path", env['conda_pack_path'])
