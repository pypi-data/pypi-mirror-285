# -*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import h2osteam
from h2osteam.utils import set_scalable_cluster_params, validate_dataset_params

from .sparkling_cluster import SparklingSession


class SparklingClient:

    @staticmethod
    def launch_sparkling_cluster(name=None,
                                 version=None,
                                 profile_name=None,
                                 dataset_size_gb=None,
                                 dataset_dimension=None,
                                 using_xgboost=False,
                                 python_environment_name=None,
                                 driver_cores=None,
                                 driver_memory_gb=None,
                                 executors=None,
                                 executor_cores=None,
                                 executor_memory_gb=None,
                                 h2o_nodes=None,
                                 h2o_node_memory_gb=None,
                                 h2o_node_cpus=None,
                                 h2o_extra_memory_percent=None,
                                 max_idle_h=None,
                                 max_uptime_h=None,
                                 timeout_s=None,
                                 yarn_queue="",
                                 spark_properties=None,
                                 save_cluster_data=False):

        """
        Launch a new Sparkling Water cluster.

        Launches a new Sparkling Water cluster using the parameters described below.
        You do not need to specify all parameters. In that case they will be filled
        based on the default value of the selected profile.
        The process of launching a cluster can take up to 5 minutes.

        :param name: Name of the cluster.
        :param version: Version of Sparkling Water that will be used in the cluster.
        :param dataset_size_gb: (Optional) Specify size of your uncompressed dataset. For compressed data source, use dataset_dimension parameter. Cluster parameters will be preset to accommodate your dataset within selected profile limits. Does not override user-specified values.
        :param dataset_dimension: (Optional) Tuple of (n_rows, n_cols) representing an estimation of dataset dimensions. Use this parameter when you intend to use compressed data source like Parquet format. Cluster parameters will be preset to accommodate your dataset within selected profile limits. Does not override user-specified values.
        :param using_xgboost: (Optional) Set boolean value to indicate whether you want to use XGBoost on your cluster. extra_memory_percent parameter will be set accordingly. Does not override user-specified value.
        :param profile_name: (Optional) Name of the profile for the cluster.
        :param python_environment_name: (Optional) Specify the Python environment name you want to use.
        :param driver_cores: (Optional) Number of Spark driver cores.
        :param driver_memory_gb: (Optional) Amount of Spark driver memory in GB.
        :param executors: (Optional) Number of Spark executors.
        :param executor_cores: (Optional) Number of Spark executor cores.
        :param executor_memory_gb: (Optional) Amount of Spark executor memory in GB.
        :param h2o_nodes: (Optional) Specify the number of H2O nodes for the cluster.
        :param h2o_node_memory_gb: (Optional) Specify the amount of memory that should be available on each H2O node.
        :param h2o_node_cpus: (Optional) Number of CPUs/threads used by H2O on a single node. Specify '0' to use all available CPUs/threads.
        :param h2o_extra_memory_percent: (Optional) Specify the amount of extra memory for internal JVM use outside of the Java heap.
        :param max_idle_h: (Optional) Maximum amount of time in hours the cluster can be idle before shutting down.
        :param max_uptime_h: (Optional) Maximum amount of time in hours the cluster will be up before shutting down.
        :param timeout_s: (Optional) Maximum amount of time in seconds to wait for the H2O cluster to start.
        :param spark_properties: (Optional) Specify additional spark properties as a Python dictionary.
        :param yarn_queue: (Optional) Name of the YARN queue where the cluster will be placed.
        :param save_cluster_data: (Optional) Set boolean value to indicate whether you want to save cluster data
        (default False). Cluster data will be saved when the cluster reaches its uptime or idle time limit.
        Such cluster can be restarted with saved data automatically loaded.


        :returns: Sparkling cluster as an :class:`SparklingSession` object.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import SparklingClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> SparklingClient.launch_sparkling_cluster(name="test-cluster", version="3.28.0.2", dataset_size_gb=2)

        """
        if name is None:
            raise Exception("Must enter valid cluster name")
        if profile_name is None:
            profile_name = "default-sparkling-internal"

        spark_properties_string = ""
        if spark_properties is not None:
            for key, value in spark_properties.items():
                spark_properties_string = '%s;%s=%s' % (spark_properties_string, key, value)

        sparkling_engine_id, h2o_engine_id = h2osteam.api().get_sparkling_engine_by_version(version)

        environment_id = -1
        if python_environment_name is not None:
            environment_id = h2osteam.api().get_python_environment_by_name(python_environment_name)['id']

        profile = h2osteam.api().get_profile_by_name(profile_name)
        profile_type = profile['profile_type']

        if driver_cores is None:
            driver_cores = profile[profile_type]['driver_cores']['initial']
        if driver_memory_gb is None:
            driver_memory_gb = profile[profile_type]['driver_memory']['initial']
        if executor_cores is None:
            executor_cores = profile[profile_type]['executor_cores']['initial']
        if h2o_node_cpus is None:
            h2o_node_cpus = profile[profile_type]['h2o_threads']['initial']
        if max_idle_h is None:
            max_idle_h = profile[profile_type]['max_idle_time']['initial']
        if max_uptime_h is None:
            max_uptime_h = profile[profile_type]['max_uptime']['initial']
        if timeout_s is None:
            timeout_s = profile[profile_type]['start_timeout']['initial']
        if spark_properties is None:
            spark_properties_string = profile[profile_type]['spark_properties']

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
        executors, executor_memory_gb, h2o_extra_memory_percent = set_scalable_cluster_params(profile,
                                                                                              rec_cluster_memory,
                                                                                              executors,
                                                                                              executor_memory_gb,
                                                                                              h2o_extra_memory_percent)

        if profile_type == "sparkling_external":
            if h2o_nodes is None:
                h2o_nodes = profile[profile_type]['h2o_nodes']['initial'] if dataset_size_gb is None else executors
            if h2o_node_memory_gb is None:
                h2o_node_memory_gb = profile[profile_type]['h2o_memory']['initial'] if dataset_size_gb is None else executor_memory_gb
        else:
            h2o_nodes = -1
            h2o_node_memory_gb = -1

        print("Sparkling Water cluster is starting, please wait...")

        clid = h2osteam.api().launch_sparkling_cluster(parameters={
            "cluster_name": name,
            "h2o_engine_id": h2o_engine_id,
            "sparkling_engine_id": sparkling_engine_id,
            "profile_id": profile['id'],
            "environment_id": environment_id,

            "driver_cores": driver_cores,
            "driver_memory": driver_memory_gb,
            "num_executors": executors,

            "executor_cores": executor_cores,
            "executor_memory": executor_memory_gb,

            "h2o_nodes": h2o_nodes,
            "h2o_memory": h2o_node_memory_gb,
            "h2o_threads": h2o_node_cpus,
            "h2o_extramempercent": h2o_extra_memory_percent,

            "max_idle_time": max_idle_h,
            "max_uptime": max_uptime_h,
            "start_timeout": timeout_s,

            "spark_properties": spark_properties_string,
            "yarn_queue": yarn_queue,

            "rec_memory": rec_cluster_memory["total_memory_gb"],
            "rec_extra_memory_percent": rec_cluster_memory["extra_mem_percent"],

            "save_cluster_data": save_cluster_data

        })

        cluster = SparklingSession(h2osteam.api().get_sparkling_cluster(clid))
        cluster.wait()
        return cluster

    @staticmethod
    def get_cluster(name=None):
        """
        Get an existing Sparkling Water cluster.

        :param name: Name of the cluster.
        :returns: Sparkling Water cluster as an :class:`SparklingSession` object.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import SparklingClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> SparklingClient.get_cluster("test-cluster")

        """
        cluster = h2osteam.api().get_sparkling_cluster_by_name(name)
        return SparklingSession(cluster)

    @staticmethod
    def get_clusters():
        """
        Get all Sparkling Water clusters available to this user.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import SparklingClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> SparklingClient.get_clusters()

        """
        return h2osteam.api().get_sparkling_clusters()
