# -*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import h2osteam
from h2osteam.utils import set_scalable_cluster_params, validate_dataset_params

from .h2o_cluster import H2oCluster


class H2oClient:

    @staticmethod
    def launch_cluster(name=None,
                       version=None,
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
                       save_cluster_data=False):
        """
        Launch a new H2O cluster.

        Launches a new H2O cluster using the parameters described below.
        You do not need to specify all parameters. In that case they will be filled
        based on the default values of the selected profile.
        The process of launching a cluster can take up to 5 minutes.

        :param name: Name of the new cluster.
        :param version: Version of H2O that will be used in the cluster.
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
        :returns: H2O cluster as an :class:`H2oCluster` object.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import H2oClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> H2oClient.launch_cluster(name="test-cluster", version="3.28.0.2", dataset_size_gb=2)

        """
        if name is None:
            raise Exception("Must enter valid cluster name")
        if version is None:
            raise Exception("Must enter H2O version")
        if profile_name is None:
            profile_name = "default-h2o"

        profile = h2osteam.api().get_profile_by_name(profile_name)

        if node_cpus is None:
            node_cpus = profile['h2o']['h2o_threads']['initial']
        if yarn_vcores is None:
            yarn_vcores = profile['h2o']['yarn_vcores']['initial']
        if max_idle_h is None:
            max_idle_h = profile['h2o']['max_idle_time']['initial']
        if max_uptime_h is None:
            max_uptime_h = profile['h2o']['max_uptime']['initial']
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

        cluster_id = h2osteam.api().launch_h2o_cluster(parameters={
            "name": name,
            "h2o_engine_id": h2osteam.api().get_h2o_engine_by_version(version)['id'],
            "profile_id": profile['id'],

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

            "rec_memory": rec_cluster_memory["total_memory_gb"],
            "rec_extra_memory_percent": rec_cluster_memory["extra_mem_percent"],

            "save_cluster_data": save_cluster_data,
            "recover_grid_search": False
        })

        cluster = H2oCluster(cluster_id=cluster_id)
        cluster.wait()

        return cluster

    @staticmethod
    def get_cluster(name):
        """
        Get an existing H2O cluster.

        :param name: Name of the cluster.
        :returns: H2O cluster as an :class:`H2oCluster` object.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import H2oClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> H2oClient.get_cluster("test-cluster")

        """
        cluster_id = h2osteam.api().get_h2o_cluster_by_name(name)['id']

        return H2oCluster(cluster_id=cluster_id)

    @staticmethod
    def get_clusters():
        """
        Get all H2O clusters available to this user.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import H2oClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> H2oClient.get_clusters()

        """
        return h2osteam.api().get_h2o_clusters()
