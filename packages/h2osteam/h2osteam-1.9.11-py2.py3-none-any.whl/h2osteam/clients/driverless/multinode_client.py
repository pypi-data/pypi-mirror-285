# -*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import h2osteam
import time
import warnings
from . import DriverlessClient
from datetime import datetime


class MultinodeClient:

    def __init__(self, steam=None):
        self.steam = steam

        self.launch_cluster = self._launch_cluster
        self.get_cluster = self._get_cluster
        self.get_clusters = self._get_clusters

    def __api(self):
        return h2osteam.api() if self.steam is None else self.steam

    @staticmethod
    def launch_cluster(name=None,
                       version=None,
                       profile_name=None,
                       master_cpu_count=None,
                       master_gpu_count=None,
                       master_memory_gb=None,
                       master_storage_gb=None,
                       worker_count=None,
                       worker_cpu_count=None,
                       worker_gpu_count=None,
                       worker_memory_gb=None,
                       worker_storage_gb=None,
                       autoscaling_enabled=False,
                       autoscaling_min_workers=None,
                       autoscaling_max_workers=None,
                       autoscaling_buffer=None,
                       autoscaling_downscale_delay_seconds=None,
                       timeout_s=600):
        """
        DEPRECATED! Launch new Driverless AI multinode cluster.
        """

        warnings.warn(
            "'MultinodeClient.launch_cluster()' function is deprecated in favor of 'MultinodeClient("
            ").launch_cluster()' and will be removed in v1.9",
            stacklevel=2
        )

        return MultinodeClient()._launch_cluster(name=name,
                                                 version=version,
                                                 profile_name=profile_name,
                                                 master_cpu_count=master_cpu_count,
                                                 master_gpu_count=master_gpu_count,
                                                 master_memory_gb=master_memory_gb,
                                                 master_storage_gb=master_storage_gb,
                                                 worker_count=worker_count,
                                                 worker_cpu_count=worker_cpu_count,
                                                 worker_gpu_count=worker_gpu_count,
                                                 worker_memory_gb=worker_memory_gb,
                                                 worker_storage_gb=worker_storage_gb,
                                                 autoscaling_enabled=autoscaling_enabled,
                                                 autoscaling_min_workers=autoscaling_min_workers,
                                                 autoscaling_max_workers=autoscaling_max_workers,
                                                 autoscaling_buffer=autoscaling_buffer,
                                                 autoscaling_downscale_delay_seconds=autoscaling_downscale_delay_seconds,
                                                 timeout_s=timeout_s)

    def _launch_cluster(self,
                        name=None,
                        version=None,
                        profile_name=None,
                        master_cpu_count=None,
                        master_gpu_count=None,
                        master_memory_gb=None,
                        master_storage_gb=None,
                        worker_count=None,
                        worker_cpu_count=None,
                        worker_gpu_count=None,
                        worker_memory_gb=None,
                        worker_storage_gb=None,
                        autoscaling_enabled=False,
                        autoscaling_min_workers=None,
                        autoscaling_max_workers=None,
                        autoscaling_buffer=None,
                        autoscaling_downscale_delay_seconds=None,
                        timeout_s=600):
        """
        Launch new Driverless AI multinode cluster.

        Launches new Driverless AI multinode cluster using the parameters described below.

        :param name: Name of the Driverless AI instance.
        :param version: Version of Driverless AI.
        :param profile_name: Specify name of an existing profile that will be used for this cluster.
        :param master_cpu_count: Master node number of CPUs (threads or virtual CPUs).
        :param master_gpu_count: Master node number of GPUs.
        :param master_memory_gb: Master node amount of memory in GB.
        :param master_storage_gb: Master node amount of storage in GB.
        :param worker_count: Number of workers. This parameter is unused when autoscaling is enabled.
        :param worker_cpu_count: Worker node number of CPUs (threads or virtual CPUs).
        :param worker_gpu_count: Worker node number of GPUs.
        :param worker_memory_gb: Worker node amount of memory in GB.
        :param worker_storage_gb: Worker node amount of storage in GB.
        :param autoscaling_enabled: Enable autoscaling of worker nodes.
        :param autoscaling_min_workers: Minimum number of workers.
        :param autoscaling_max_workers: Maximum number of workers.
        :param autoscaling_buffer: Number of spare workers above the number of workers needed.
        :param autoscaling_downscale_delay_seconds: Downscaling is triggered after downscaling is needed for the specified period.
        :param timeout_s: (Optional) Maximum amount of time in seconds to wait for the Driverless AI master/workers to start.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import DriverlessClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = MultinodeClient().launch_cluster(name="dai-multinode-1",
        >>>                                            version="1.9.0.4",
        >>>                                            profile_name="default-driverless-kubernetes",
        >>>                                            master_cpu_count=4,
        >>>                                            master_gpu_count=0,
        >>>                                            master_memory_gb=32,
        >>>                                            master_storage_gb=1024,
        >>>                                            worker_cpu_count=2,
        >>>                                            worker_gpu_count=0,
        >>>                                            worker_memory_gb=16,
        >>>                                            worker_storage_gb=256,
        >>>                                            autoscaling_enabled=True,
        >>>                                            autoscaling_min_workers=1,
        >>>                                            autoscaling_max_workers=10,
        >>>                                            autoscaling_buffer=1,
        >>>                                            autoscaling_downscale_delay_seconds=60,
        >>>                                            timeout_s=600)

        """

        if name is None:
            raise Exception("Must enter valid cluster name")
        if version is None:
            raise Exception("Must enter Driverless AI version")
        if profile_name is None:
            raise Exception("Must enter valid profile name")
        if autoscaling_enabled and worker_count is not None:
            raise Exception("The 'worker_count' argument is not supported when autoscaling is enabled")

        if master_cpu_count is None:
            raise Exception("Mandatory parameter master_cpu_count is missing")
        if master_gpu_count is None:
            raise Exception("Mandatory parameter master_gpu_count is missing")
        if master_memory_gb is None:
            raise Exception("Mandatory parameter master_memory_gb is missing")
        if master_storage_gb is None:
            raise Exception("Mandatory parameter master_storage_gb is missing")
        if worker_cpu_count is None:
            raise Exception("Mandatory parameter worker_cpu_count is missing")
        if worker_gpu_count is None:
            raise Exception("Mandatory parameter worker_gpu_count is missing")
        if worker_memory_gb is None:
            raise Exception("Mandatory parameter worker_memory_gb is missing")
        if worker_storage_gb is None:
            raise Exception("Mandatory parameter worker_storage_gb is missing")

        if autoscaling_enabled:
            if autoscaling_min_workers is None:
                raise Exception("Mandatory parameter autoscaling_min_workers is missing")
            if autoscaling_max_workers is None:
                raise Exception("Mandatory parameter autoscaling_max_workers is missing")
            if autoscaling_buffer is None:
                raise Exception("Mandatory parameter autoscaling_buffer is missing")
            if autoscaling_downscale_delay_seconds is None:
                raise Exception("Mandatory parameter autoscaling_downscale_delay_second is missing")
        else:
            if worker_count is None:
                raise Exception("Mandatory parameter worker_count is missing")

        self.__api().launch_driverless_multinode(parameters={
            "name": name,
            "profile_name": profile_name,
            "version": version,
            "master_cpu_count": master_cpu_count,
            "master_gpu_count": master_gpu_count,
            "master_memory_gb": master_memory_gb,
            "master_storage_gb": master_storage_gb,
            "worker_count": worker_count,
            "worker_cpu_count": worker_cpu_count,
            "worker_gpu_count": worker_gpu_count,
            "worker_memory_gb": worker_memory_gb,
            "worker_storage_gb": worker_storage_gb,
            "timeout_seconds": timeout_s,
            "autoscaling_enabled": autoscaling_enabled,
            "autoscaling_min_workers": autoscaling_min_workers,
            "autoscaling_max_workers": autoscaling_max_workers,
            "autoscaling_buffer": autoscaling_buffer,
            "autoscaling_downscale_delay_seconds": autoscaling_downscale_delay_seconds,
        })

        return MultinodeCluster(name)

    @staticmethod
    def get_cluster(name):
        """
        DEPRECATED! Get existing Driverless AI multinode cluster.
        """

        warnings.warn(
            "'MultinodeClient.get_cluster()' function is deprecated in favor of 'MultinodeClient("
            ").get_cluster()' and will be removed in v1.9",
            stacklevel=2
        )

        return MultinodeClient()._get_cluster(name=name)

    def _get_cluster(self, name):
        """
        Get existing Driverless AI multinode cluster.

        :param name: Name of the Driverless AI multinode cluster.
        :returns: Driverless AI multinode cluster as an :class:`MultinodeCluster` object.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import MultinodeClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = MultinodeClient().get_cluster("dai-multinode-1")

        """
        return MultinodeCluster(name=name, api=self.__api())

    @staticmethod
    def get_clusters():
        """
        DEPRECATED! Get existing Driverless AI multinode cluster.
        """

        warnings.warn(
            "'MultinodeClient.get_clusters()' function is deprecated in favor of 'MultinodeClient("
            ").get_clusters()' and will be removed in v1.9",
            stacklevel=2
        )

        return MultinodeClient()._get_clusters()

    def _get_clusters(self):
        """
        Get all existing Driverless AI multinode clusters.

        :returns: List of :class:`MultinodeCluster` objects.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import MultinodeClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> clusters = MultinodeClient().get_clusters()

        """
        out = []
        clusters = self.__api().get_driverless_multinodes()

        for c in clusters:
            out.append(MultinodeCluster("", m=c, api=self.__api()))

        return out


class MultinodeCluster(object):
    def __init__(self, name, m=None, api=None):
        self._api = h2osteam.api() if api is None else api

        if m is None:
            m = self._api.get_driverless_multinode(name)

        self.id = m['id']
        self.master_id = m['master_id']
        self.name = m['name']
        self.profile_name = m['profile_name']
        self.master_status = m['master_status']
        self.version = m['version']
        self.master_cpu_count = m['master_cpu_count']
        self.master_gpu_count = m['master_gpu_count']
        self.master_memory_gb = m['master_memory_gb']
        self.master_storage_gb = m['master_storage_gb']
        self.worker_cpu_count = m['worker_cpu_count']
        self.worker_gpu_count = m['worker_gpu_count']
        self.worker_memory_gb = m['worker_memory_gb']
        self.worker_storage_gb = m['worker_storage_gb']

        self.autoscaling_min_workers = m['autoscaling_min_workers']
        self.autoscaling_max_workers = m['autoscaling_max_workers']
        self.autoscaling_buffer = m['autoscaling_buffer']
        self.autoscaling_downscale_delay_seconds = m['autoscaling_downscale_delay_seconds']

        self.target_worker_count = m['target_worker_count']
        self.starting_worker_count = m['starting_worker_count']
        self.running_worker_count = m['running_worker_count']
        self.stopping_worker_count = m['stopping_worker_count']

        self.authentication = m['authentication']
        self._address = m['address']
        self._username = m['username']
        self._password = m['password']

        self.created_at = datetime.fromtimestamp(m['created_at']).isoformat()
        self.started_at = datetime.fromtimestamp(m['started_at']).isoformat()

    def refresh(self):
        self.__init__(self.name)

    def wait(self):
        """
        Waits for Driverless AI multinode cluster to reach target status.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import MultinodeClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = MultinodeClient().launch_cluster(name="dai-multinode-1", ...)
        >>> cluster.wait()
        >>> cluster.connect()

        """
        master = self._api.get_driverless_instance_by_id(self.master_id)

        while master["status"] != master["target_status"]:
            time.sleep(5)
            master = self._api.get_driverless_instance_by_id(self.master_id)

        return self

    def terminate(self):
        """
        Terminate Driverless AI multinode cluster.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import MultinodeClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = MultinodeClient().get_cluster("dai-multinode-1")
        >>> cluster.terminate()

        """
        self._api.terminate_driverless_multinode(self.name)
        self.refresh()

    def restart(self):
        """
        Restart failed Driverless AI multinode cluster.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import MultinodeClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = MultinodeClient().get_cluster("dai-multinode-1")
        >>> cluster.restart()

        """
        self._api.restart_driverless_multinode(self.name)
        self.refresh()

    def is_master_ready(self):
        """
        Check whether the master node of the multinode cluster is ready and can be connected to.

        """
        self.refresh()
        return self.master_status == "running"

    def internal_address(self):
        """
        Get address of the Driverless AI master node. This address is accessible only inside the Kubernetes cluster.

        """
        self.refresh()
        return self._address

    def external_address(self):
        """
        Get address of the Driverless AI master node. This address is reverse-proxied by Enterprise Steam and is
        accessible from outside the Kubernetes cluster.

        """
        self.refresh()
        return '%s://%s:%s%s/proxy/driverless/%d' % (self._api.scheme, self._api.host, self._api.port, self._api.path, self.id)

    def openid_login_url(self):
        """
        Returns an URL that is only valid with OpenID authentication and redirects to the Driverless AI multinode master

        """
        return '%s://%s:%s%s/oidc-login-start?forward=/proxy/driverless/%d/openid/callback' \
               % (self._api.scheme, self._api.host, self._api.port, self._api.path, self.id)

    def connect(self, use_own_client=False, backend_version_override=None):
        """
        Connect to the running Driverless AI multinode cluster using the Python client.

        :param use_own_client: Set to True to use your own driverlessai client instead of the one provided by Steam.
        :param backend_version_override: (Optional) version of client backend to use, overrides Driverless AI server
        version detection. Specify "latest" to get the most recent backend supported. In most cases the user should rely
         on Driverless AI server version detection and leave this as the default None.

        :returns: driverlessai.Client class.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import MultinodeClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = MultinodeClient().get_cluster("dai-multinode-1")
        >>> client = cluster.connect()

        """
        if not self.is_master_ready():
            raise Exception("Master node is not ready")

        return DriverlessClient.connect(self._api,
                                        self.master_id,
                                        False,
                                        use_own_client=use_own_client,
                                        backend_version_override=backend_version_override)

    def get_events(self):
        """
        Get events of the Driverless AI multinode cluster.
        Can be used for debugging purposes.

        """
        return self._api.get_events("driverless-instance", self.master_id)
