# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import re
import warnings

import h2osteam
from h2osteam.clients import AdminClient, H2oClient, SparklingClient
from h2osteam.backend import SteamConnection


class SteamClient:
    """
        DEPRECATED!
        This class and its methods are deprecated and they will be removed in v1.9
    """

    def __init__(self, conn=None):
        self.conn = h2osteam.api() if conn is None else conn 

    def __repr__(self):
        return "<SteamClient connected to https://%s:%s>" % (self.conn.host, self.conn.port)

    @staticmethod
    def start_h2o_cluster(cluster_name=None,
                          profile_name=None,
                          num_nodes=0,
                          node_memory=None,
                          v_cores=0,
                          n_threads=0,
                          max_idle_time=0,
                          max_uptime=0,
                          extramempercent=10,
                          h2o_version=None,
                          yarn_queue=None,
                          callback_ip=None,
                          node_id=0):
        """
            DEPRECATED! Launch a new H2O cluster.
        """

        warnings.warn(
            "function is deprecated in favor of 'H2oClient.launch_cluster()' and will be removed in v1.9",
            stacklevel=2
        )

        return H2oClient.launch_cluster(name=cluster_name,
                                        version=h2o_version,
                                        profile_name=profile_name,
                                        nodes=num_nodes,
                                        node_cpus=n_threads,
                                        yarn_vcores=v_cores,
                                        node_memory_gb=int(re.sub(r'\D', "", node_memory)),
                                        extra_memory_percent=extramempercent,
                                        max_idle_h=max_idle_time,
                                        max_uptime_h=max_uptime,
                                        yarn_queue=yarn_queue,
                                        leader_node_id=node_id).get_config()

    @staticmethod
    def stop_h2o_cluster(config):
        """
            DEPRECATED! Stop H2O cluster.
        """

        warnings.warn(
            "function is deprecated in favor of 'H2oClient.get_cluster()' and will be removed in v1.9",
            stacklevel=2
        )

        return H2oClient.get_cluster(config['name']).stop()

    def get_python_environments(self):
        """
            DEPRECATED! Get Python environments.
        """
        warnings.warn(
            "function is deprecated and will be removed in v1.9",
            stacklevel=2
        )
        return self.conn.get_python_environments()

    @staticmethod
    def upload_conda_environment(name, path):
        """
            DEPRECATED! Upload Conda Python environments.
        """
        warnings.warn(
            "function is deprecated and will be removed in v1.9",
            stacklevel=2
        )
        return AdminClient.upload_conda_environment(name, path)

    def create_pyspark_python_path_environment(self, name, path):
        """
            DEPRECATED! Create Python Pyspark Path environment.
        """
        warnings.warn(
            "function is deprecated and will be removed in v1.9",
            stacklevel=2
        )
        return self.conn.create_python_environment(name, "", path, [])

    def delete_python_environment(self, environment_id):
        """
            DEPRECATED! Delete Python environment.
        """
        warnings.warn(
            "function is deprecated and will be removed in v1.9",
            stacklevel=2
        )
        return self.delete_python_environment(environment_id)

    @staticmethod
    def upload_engine(path):
        """
            DEPRECATED! Upload H2O engine.
        """
        warnings.warn(
            "function is deprecated in favor of AdminClient.upload_h2o_engine() and will be removed in v1.9",
            stacklevel=2
        )
        return AdminClient.upload_h2o_engine(path)

    @staticmethod
    def upload_sparkling_engine(path):
        """
            DEPRECATED! Upload Sparkling Water engine.
        """
        warnings.warn(
            "function is deprecated in favor of AdminClient.upload_sparkling_engine() and will be removed in v1.9",
            stacklevel=2
        )
        return AdminClient.upload_sparkling_engine(path)

    def get_h2o_clusters(self):
        """
            DEPRECATED! Get H2O clusters.
        """
        warnings.warn(
            "function is deprecated in favor of H2oClient.get_clusters() and will be removed in v1.9",
            stacklevel=2
        )
        return self.conn.get_h2o_clusters()

    @staticmethod
    def show_profiles():
        """
            DEPRECATED! Prints profiles available to this user.
        """
        warnings.warn(
            "'show_profiles' function is deprecated in favor of 'print_profiles' and will be removed in v1.9",
            stacklevel=2
        )
        return h2osteam.print_profiles()

    @staticmethod
    def get_h2o_cluster(cluster_name):
        """
            DEPRECATED! Get H2O cluster by name.
        """
        warnings.warn(
            "function is deprecated in favor of H2oClient.get_cluster() and will be removed in v1.9",
            stacklevel=2
        )
        return H2oClient.get_cluster(cluster_name).get_config()

    @staticmethod
    def get_sparkling_cluster(cluster_name):
        """
            DEPRECATED! Get Sparkling Water cluster by name.
        """
        warnings.warn(
            "function is deprecated in favor of SparklingClient.get_cluster() and will be removed in v1.9",
            stacklevel=2
        )
        return SparklingClient.get_cluster(cluster_name)

    def get_sparkling_clusters(self):
        """
            DEPRECATED! Get Sparkling Water clusters.
        """
        warnings.warn(
            "function is deprecated in favor of SparklingClient.get_clusters() and will be removed in v1.9",
            stacklevel=2
        )
        return self.conn.get_sparkling_clusters()

    @staticmethod
    def start_internal_sparkling_cluster(cluster_name=None,
                                         profile_name=None,
                                         h2o_version=None,
                                         driver_cores=0,
                                         driver_memory_gb=0,
                                         num_executors=0,
                                         executor_cores=0,
                                         executor_memory_gb=0,
                                         h2o_node_threads=0,
                                         start_timeout_sec=0,
                                         yarn_queue=None,
                                         python_environment_name="",
                                         spark_properties=None):
        """
            DEPRECATED! Launch Sparkling Water internal backend cluster.
        """
        warnings.warn(
            "function is deprecated if favor of SparklingClient.launch_sparkling_cluster() and will be removed in v1.9",
            stacklevel=2
        )
        return SparklingClient.launch_sparkling_cluster(name=cluster_name,
                                                        version=h2o_version,
                                                        profile_name=profile_name,
                                                        python_environment_name=python_environment_name,
                                                        driver_cores=driver_cores,
                                                        driver_memory_gb=driver_memory_gb,
                                                        executors=num_executors,
                                                        executor_cores=executor_cores,
                                                        executor_memory_gb=executor_memory_gb,
                                                        h2o_node_cpus=h2o_node_threads,
                                                        timeout_s=start_timeout_sec,
                                                        yarn_queue=yarn_queue,
                                                        spark_properties=spark_properties)

    @staticmethod
    def start_external_sparkling_cluster(cluster_name=None,
                                         profile_name=None,
                                         h2o_version=None,
                                         driver_cores=0,
                                         driver_memory_gb=0,
                                         num_executors=0,
                                         executor_cores=0,
                                         executor_memory_gb=0,
                                         h2o_nodes=0,
                                         h2o_node_memory_gb=0,
                                         h2o_node_threads=0,
                                         start_timeout_sec=0,
                                         yarn_queue=None,
                                         python_environment_name="",
                                         spark_properties=None):
        """
            DEPRECATED! Launch Sparkling Water external backend cluster.
        """
        warnings.warn(
            "function is deprecated if favor of SparklingClient.launch_sparkling_cluster() and will be removed in v1.9",
            stacklevel=2
        )

        return SparklingClient.launch_sparkling_cluster(name=cluster_name,
                                                        version=h2o_version,
                                                        profile_name=profile_name,
                                                        python_environment_name=python_environment_name,
                                                        driver_cores=driver_cores,
                                                        driver_memory_gb=driver_memory_gb,
                                                        executors=num_executors,
                                                        executor_cores=executor_cores,
                                                        executor_memory_gb=executor_memory_gb,
                                                        h2o_nodes=h2o_nodes,
                                                        h2o_node_memory_gb=h2o_node_memory_gb,
                                                        h2o_node_cpus=h2o_node_threads,
                                                        timeout_s=start_timeout_sec,
                                                        yarn_queue=yarn_queue,
                                                        spark_properties=spark_properties)
