# -*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import h2osteam
from h2osteam.utils import get_filename_from_path


class AdminClient:
    @staticmethod
    def upload_h2o_engine(path):
        """
        Upload H2O engine to Steam.

        Uploads H2O engine from local machine to the Steam server where it is imported and made available to users.

        :param path: Full path to the H2O engine on disk of the local machine.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import AdminClient
        >>> url = "https://steam.example.com:9555"
        >>> username = "AzureDiamond"
        >>> password = "hunter2"
        >>> h2osteam.login(url=url, username=username, password=password, verify_ssl=True)
        >>> AdminClient.upload_h2o_engine("/tmp/h2o-3.26.0.6-cdh6.3.zip")

        """
        h2osteam.api().upload(target="/upload/h2o/engine", path=path, payload=None)

    @staticmethod
    def import_h2o_engine(path):
        """
        Import H2O engine to Steam.

        Imports H2O engine from Steam server and makes it available to users.

        :param path: Full path to the H2O engine on disk of the Steam server.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import AdminClient
        >>> url = "https://steam.example.com:9555"
        >>> username = "AzureDiamond"
        >>> password = "hunter2"
        >>> h2osteam.login(url=url, username=username, password=password, verify_ssl=True)
        >>> AdminClient.import_h2o_engine("/tmp/h2o-3.26.0.6-cdh6.3.zip")

        """
        h2osteam.api().import_h2o_engine(path)

    @staticmethod
    def upload_sparkling_engine(path):
        """
        Upload Sparkling Water engine to Steam.

        Uploads Sparkling Water engine from local machine to the Steam server
        where it is imported and made available to users.

        :param path: Full path to the Sparkling Water engine on disk of the local machine.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import AdminClient
        >>> url = "https://steam.example.com:9555"
        >>> username = "AzureDiamond"
        >>> password = "hunter2"
        >>> h2osteam.login(url=url, username=username, password=password, verify_ssl=True)
        >>> AdminClient.upload_sparkling_engine("/tmp/sparkling-water-3.28.0.1-1-2.4.zip")

        """
        h2osteam.api().upload(target="/upload/sparkling/engine", path=path, payload=None)

    @staticmethod
    def import_sparkling_engine(path):
        """
        Import Sparkling Water engine to Steam.

        Imports Sparkling Water engine from Steam server and makes it available to users.

        :param path: Full path to the Sparkling Water engine on disk of the Steam server.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import AdminClient
        >>> url = "https://steam.example.com:9555"
        >>> username = "AzureDiamond"
        >>> password = "hunter2"
        >>> h2osteam.login(url=url, username=username, password=password, verify_ssl=True)
        >>> AdminClient.import_sparkling_engine("/tmp/sparkling-water-3.28.0.1-1-2.4.zip")

        """
        h2osteam.api().import_sparkling_engine(path)

    @staticmethod
    def import_python_environment(name, path):
        """
        Import an existing Python environment using the Python Pyspark Path.

        Imports an existing Python environment to Steam using the path to the Python executable.

        :param name: Name of the new Python environment.
        :param path: Full path to the python executable of the new Python environment.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import AdminClient
        >>> url = "https://steam.example.com:9555"
        >>> username = "AzureDiamond"
        >>> password = "hunter2"
        >>> h2osteam.login(url=url, username=username, password=password, verify_ssl=True)
        >>> AdminClient.create_pyspark_python_path_environment("python3", "/tmp/virtual-env/python3/bin/python")

        """
        return h2osteam.api().create_python_environment(name, "", path, [])

    @staticmethod
    def upload_conda_environment(name, path):
        """
        Upload Conda Python environment.

        Uploads and imports an existing Python environment using a path to a conda-packed Conda Python environment.

        :param name: Name of the new Python environment.
        :param path: Full path to the conda-packed Conda Python environment.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import AdminClient
        >>> url = "https://steam.example.com:9555"
        >>> username = "AzureDiamond"
        >>> password = "hunter2"
        >>> h2osteam.login(url=url, username=username, password=password, verify_ssl=True)
        >>> AdminClient.upload_conda_environment("python3-conda", "/tmp/conda-python3.tar.gz")

        """

        basename = get_filename_from_path(path)
        created_id = h2osteam.api().create_python_environment(name, basename, "", [])
        try:
            payload = {'envName': name, 'envId': str(created_id)}
            h2osteam.api().upload(target="/upload/sparkling/conda-pack", path=path, payload=payload)
        except Exception:
            h2osteam.api().delete_python_environment(created_id)
            raise
        return created_id

    @staticmethod
    def delete_user_resources(username):
        """
        Delete driverless instances and h2o kubernetes clusters of given user.

        :param username: Name of the user.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import AdminClient
        >>> url = "https://steam.example.com:9555"
        >>> username = "AzureDiamond"
        >>> password = "hunter2"
        >>> h2osteam.login(url=url, username=username, password=password, verify_ssl=True)
        >>> AdminClient.delete_user_resources(username="adam")

        """
        return h2osteam.api().terminate_identity_resources(username)
