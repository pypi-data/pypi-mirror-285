# -*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import time
import h2osteam
import importlib

from h2osteam.utils import set_scalable_cluster_params, validate_dataset_params
from distutils.version import LooseVersion


class H2oCluster:
    def __init__(self, cluster_id=None):
        self.id = cluster_id
        self.api = h2osteam.api()
        self.config = {}

    def start(self,
              dataset_size_gb=None,
              dataset_dimension=None,
              using_xgboost=False,
              profile_name=None,
              nodes=None,
              node_cpus=None,
              yarn_vcores=None,
              node_memory_gb=None,
              extra_memory_percent=None,
              max_idle_h=None,
              max_uptime_h=None,
              timeout_s=None,
              yarn_queue="",
              leader_node_id=0,
              save_cluster_data=False,
              fault_tolerant_grid_search=False):
        """
        Start saved H2O cluster.

        Starts a saved H2O cluster using the parameters described below.
        You dont need to provide any parameters. Unless provided, all launch parameters are copied from the stopped
        cluster except save_cluster_data which is set to False by default.
        You can override following launch parameters.
        The process of starting a cluster can take up to 5 minutes.

        :param dataset_size_gb: (Optional) Specify size of your uncompressed dataset. For compressed data source, use dataset_dimension parameter. Cluster parameters will be preset to accommodate your dataset within selected profile limits. Does not override user-specified values.
        :param dataset_dimension: (Optional) Tuple of (n_rows, n_cols) representing an estimation of dataset dimensions. Use this parameter when you intend to use compressed data source like Parquet format. Cluster parameters will be preset to accommodate your dataset within selected profile limits. Does not override user-specified values.
        :param using_xgboost: (Optional) Set boolean value to indicate whether you want to use XGBoost on your cluster. extra_memory_percent parameter will be set accordingly. Does not override user-specified value.
        :param profile_name: (Optional) Specify name of an existing profile that will be used for this cluster.
        :param nodes: (Optional) Number of nodes of the H2O cluster.
        :param node_cpus: (Optional) Number of CPUs/threads used by H2O on a single node. Specify '0' to use all available CPUs/threads.
        :param yarn_vcores: (Optional) Number of YARN virtual cores per cluster node. Should match node_cpus.
        :param node_memory_gb: (Optional) Amount of memory in GB allocated for a single H2O node.
        :param extra_memory_percent: (Optional) Percentage of extra memory that will be allocated outside of H2O JVM for algos like XGBoost.
        :param max_idle_h: (Optional) Maximum amount of time in hours the cluster can be idle before shutting down.
        :param max_uptime_h: (Optional) Maximum amount of time in hours the cluster will be up before shutting down.
        :param timeout_s: (Optional) Maximum amount of time in seconds to wait for the H2O cluster to start.
        :param yarn_queue: (Optional) Name of the YARN queue where the cluster will be placed.
        :param leader_node_id: (Optional) ID of the H2O leader node.
        :param save_cluster_data: (Optional) Set boolean value to indicate whether you want to save cluster data
        (default False). Cluster data will be saved when the cluster reaches its uptime or idle time limit.
        Such cluster can be restarted with saved data automatically loaded.
        :param fault_tolerant_grid_search: (Optional) Set boolean value to indicate whether you want to use Grid Search
        in a fault tolerant mode (default False). In this mode, when the cluster fails while training a Grid Search
        model, it will attempt to restart itself and continue training. Reaching idle or uptime limit is not considered
        a failure.
        :returns: H2O cluster as an :class:`H2oCluster` object.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import H2oClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = H2oClient.get_cluster(name="test-cluster")
        >>> cluster.stop(save_cluster_data=True)
        >>> cluster.start(dataset_dimension=(10000,500), using_xgboost=True)

        """

        c_params = self._fetch_cluster()

        # Set unspecified cluster params from the original cluster
        if profile_name is None:
            profile_name = c_params["profile_name"]
        if nodes is None:
            nodes = c_params["h2o_nodes"]
        if node_cpus is None:
            node_cpus = c_params["h2o_threads"]
        if yarn_vcores is None:
            yarn_vcores = c_params["yarn_vcores"]
        if node_memory_gb is None:
            node_memory_gb = c_params["h2o_memory"]
        if extra_memory_percent is None:
            extra_memory_percent = c_params["h2o_extramempercent"]
        if max_idle_h is None:
            max_idle_h = c_params["max_idle_time"]
        if max_uptime_h is None:
            max_uptime_h = c_params["max_uptime"]
        if yarn_queue is None:
            yarn_queue = c_params["yarn_queue"]
        if leader_node_id is None:
            leader_node_id = c_params["leader_node_id"]

        profile = h2osteam.api().get_profile_by_name(profile_name)

        if timeout_s is None:
            timeout_s = profile['h2o']['start_timeout']['initial']

        # Validate dataset parameters
        validate_dataset_params(dataset_size_gb, dataset_dimension)
        # Get recommended total memory based on dataset params
        rec_cluster_memory = h2osteam.api().get_estimated_cluster_memory({
            "dataset_size_gb": dataset_size_gb,
            "rows": dataset_dimension[0] if dataset_dimension is not None else None,
            "cols": dataset_dimension[1] if dataset_dimension is not None else None,
            "using_x_g_boost": using_xgboost
        })
        # Scale cluster based on dataset params
        nodes, node_memory_gb, extra_memory_percent = set_scalable_cluster_params(profile,
                                                                                  rec_cluster_memory,
                                                                                  nodes,
                                                                                  node_memory_gb,
                                                                                  extra_memory_percent)

        print("H2O Cluster is starting, please wait...")

        h2osteam.api().start_h2o_cluster(
            id=self.id,
            parameters={
                "profile_id": profile['id'],
                "h2o_engine_id": h2osteam.api().get_h2o_engine_by_version(c_params['h2o_engine_version'])['id'],

                "h2o_nodes": nodes,
                "h2o_threads": node_cpus,
                "yarn_vcores": yarn_vcores,
                "h2o_memory": node_memory_gb,
                "h2o_extramempercent": extra_memory_percent,

                "max_idle_time": max_idle_h,
                "max_uptime": max_uptime_h,
                "start_timeout": timeout_s,

                "yarn_queue": yarn_queue,
                "leader_node_id": leader_node_id,

                "save_cluster_data": save_cluster_data,
                "recover_grid_search": fault_tolerant_grid_search
            }
        )

        self.wait()

    def status(self):
        """
        Get status of the H2O cluster.

        :returns: H2O cluster status as a string.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import H2oClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = H2oClient.get_cluster("test-cluster")
        >>> cluster.status()
        >>> # running

        """
        return self._fetch_cluster()['status']

    def stop(self, save_cluster_data=False):
        """
        Stop a running H2O cluster.

        :param save_cluster_data: (Optional) Set boolean value to indicate whether you want to save cluster data.
        Such cluster can be restarted with saved data automatically loaded.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import H2oClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = H2oClient.get_cluster("test-cluster")
        >>> cluster.stop(save_cluster_data=True)

        """
        cluster = self._fetch_cluster()
        self.api.stop_h2o_cluster(cluster['id'], save_cluster_data)
        print("H2O Cluster is stopping, please wait...")
        self._block_until_stopped()

    def delete(self):
        """
        Delete stopped H2O cluster.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import H2oClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = H2oClient.get_cluster("test-cluster")
        >>> cluster.delete()

        """
        cluster = self._fetch_cluster()
        self.api.delete_h2o_cluster(cluster['id'])

    def download_logs(self, path=None):
        """
        Download logs of the H2O cluster.

        :param path: Path where the H2O logs will be saved.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import H2oClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = H2oClient.get_cluster("test-cluster")
        >>> cluster.download_logs("/tmp/test-cluster-logs")

        """
        if path is None:
            raise Exception("Must enter path where logs will be saved")

        self.api.download('/download/h2o/logs/%d' % self.id, path)

        print("H2O Cluster logs saved to %s" % path)

    def connect(self):
        """
        Connect to the H2O cluster using the H2O Python client.

        :examples:

        >>> import h2o
        >>> import h2osteam
        >>> from h2osteam.clients import H2oClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = H2oClient.get_cluster("test-cluster")
        >>> cluster.connect()

        """
        cluster = self._fetch_cluster()
        if cluster['status'] != "running":
            raise Exception("H2O cluster is not running")

        self._connect_with_conf()

    def _connect_with_conf(self):
        cluster = self._fetch_cluster()
        config = self.get_config()
        h2o = importlib.import_module("h2o")
        if _needs_connect_workaround(cluster['h2o_engine_version']):
            conf = h2o.backend.H2OConnectionConf(config=config["connect_params"])
            h2o.connect(url=conf.url, verify_ssl_certificates=conf.verify_ssl_certificates, cacert=conf.cacert,
                        auth=conf.auth, proxy=conf.proxy, cookies=conf.cookies, verbose=conf.verbose)
        else:
            h2o.connect(config=config)

    def get_config(self):
        """
        Get connection config of the H2O cluster.

        Get connection config of the H2O cluster that can be used as a parameter to h2o.connect.
        Use only if H2oCluster.connect() does not work for you.

        :examples:

        >>> import h2o
        >>> import h2osteam
        >>> from h2osteam.clients import H2oClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = H2oClient.get_cluster("test-cluster")
        >>> h2o.connect(config=cluster.get_config())

        """
        cluster = self._fetch_cluster()

        connect_params = {'https': self.api.scheme == "https",
                          'verify_ssl_certificates': self.api.verify_ssl,
                          'context_path': cluster['context_path'].replace("/", "", 1),
                          'cookies': ["steam-session=%s" % self.api.cookie],
                          'ip': self.api.host,
                          'port': self.api.port}

        if self.api.cacert is not None:
            if _supports_cacert(cluster['h2o_engine_version']):
                connect_params['cacert'] = self.api.cacert
            else:
                raise Exception("This version of H2O does not support cacert parameter")

        return {'name': cluster['cluster_name'], 'connect_params': connect_params}

    def wait(self):
        """
        Wait for H2O cluster to finish launching.

        """
        self._block_until_running()

    def _fetch_cluster(self):
        return self.api.get_h2o_cluster(self.id)

    def _block_until_running(self):
        current_status = self.status()

        while True:
            new_status = self.status()

            if current_status != new_status:
                current_status = new_status

            if current_status == "starting" or current_status == "connecting":
                time.sleep(5)
                continue
            elif current_status == "running":
                print("H2O Cluster is running")
                break
            else:
                raise Exception("H2O Cluster failed to start")

    def _block_until_stopped(self):
        current_status = self.status()

        while True:
            new_status = self.status()

            if current_status != new_status:
                current_status = new_status

            if current_status == "stopping":
                time.sleep(5)
                continue
            elif current_status == "stopped":
                print("H2O Cluster stopped")
                break
            else:
                raise Exception("H2O Cluster failed to stop")


def _supports_cacert(version):
    return LooseVersion(version) >= LooseVersion("3.26.0.11")


def _needs_connect_workaround(version):
    return _supports_cacert(version) and LooseVersion(version) <= LooseVersion("3.30.0.3")
