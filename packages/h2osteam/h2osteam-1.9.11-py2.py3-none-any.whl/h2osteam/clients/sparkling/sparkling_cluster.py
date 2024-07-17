# -*- encoding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import time
import cmd
import h2osteam
import importlib

from h2osteam.utils import set_scalable_cluster_params, validate_dataset_params
from distutils.version import LooseVersion


class SparklingSession(object):
    def __init__(self, cluster):
        self.api = h2osteam.api()
        self.cluster = cluster

    def start(self,
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
        Start saved Sparkling Water cluster.

        Starts a saved Sparkling Water cluster using the parameters described below.
        You dont need to provide any parameters. Unless provided, all launch parameters are copied from the stopped
        cluster except save_cluster_data which is set to False by default.
        You can override following launch parameters.
        The process of starting a cluster can take up to 5 minutes.

        :param dataset_size_gb: (Optional) Specify size of your uncompressed dataset. For compressed data source, use dataset_dimension parameter. Cluster parameters will be preset to accommodate your dataset within selected profile limits. Does not override user-specified values.
        :param dataset_dimension: (Optional) Tuple of (n_rows, n_cols) representing an estimation of dataset dimensions. Use this parameter when you intend to use compressed data source like Parquet format. Cluster parameters will be preset to accommodate your dataset within selected profile limits. Does not override user-specified values.
        :param using_xgboost: (Optional) Set boolean value to indicate whether you want to use XGBoost on your cluster. extra_memory_percent parameter will be set accordingly. Does not override user-specified value.
        :param profile_name: (Optional) Specify name of an existing profile that will be used for this cluster.
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
        :param yarn_queue: (Optional) Name of the YARN queue where the cluster will be placed.
        :param spark_properties: (Optional) Specify additional spark properties as a Python dictionary.
        :param save_cluster_data: (Optional) Set boolean value to indicate whether you want to save cluster data
        (default False). Cluster data will be saved when the cluster reaches its uptime or idle time limit.
        Such cluster can be restarted with saved data automatically loaded.

        :returns: Sparkling cluster as an :class:`SparklingSession` object.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import SparklingClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = SparklingClient.get_cluster(name="test-cluster")
        >>> cluster.stop(save_cluster_data=True)
        >>> cluster.start(dataset_size_gb=500, using_xgboost=False, save_cluster_data=True)

        """

        # Set unspecified cluster params from the original cluster
        if profile_name is None:
            profile_name = self.cluster["profile_name"]
        if python_environment_name is None:
            python_environment_name = self.cluster["python_environment_name"]
        if driver_cores is None:
            driver_cores = self.cluster["driver_cores"]
        if driver_memory_gb is None:
            driver_memory_gb = self.cluster["driver_memory"]
        if executors is None:
            executors = self.cluster["num_executors"]
        if executor_cores is None:
            executor_cores = self.cluster["executor_cores"]
        if executor_memory_gb is None:
            executor_memory_gb = self.cluster["executor_memory"]
        if h2o_nodes is None:
            h2o_nodes = self.cluster["h2o_nodes"]
        if h2o_node_memory_gb is None:
            h2o_node_memory_gb = self.cluster["h2o_memory"]
        if h2o_node_cpus is None:
            h2o_node_cpus = self.cluster["h2o_threads"]
        if h2o_extra_memory_percent is None:
            h2o_extra_memory_percent = self.cluster["h2o_extramempercent"]
        if max_idle_h is None:
            max_idle_h = self.cluster["max_idle_time"]
        if max_uptime_h is None:
            max_uptime_h = self.cluster["max_uptime"]
        if timeout_s is None:
            timeout_s = self.cluster["start_timeout"]
        if yarn_queue is None:
            yarn_queue = self.cluster["yarn_queue"]

        # Resolve Spark properties
        spark_properties_string = ""
        if spark_properties is not None:
            for key, value in spark_properties.items():
                spark_properties_string = '%s;%s=%s' % (spark_properties_string, key, value)

        if spark_properties is None:
            spark_properties_string = self.cluster["spark_properties"]

        # Resolve environment
        environment_id = -1
        if python_environment_name is not None and python_environment_name is not "":
            print("ENV NAME", python_environment_name)
            environment_id = h2osteam.api().get_python_environment_by_name(python_environment_name)['id']

        # Resolve profile
        profile = h2osteam.api().get_profile_by_name(profile_name)
        profile_type = profile['profile_type']

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

        h2osteam.api().start_sparkling_cluster(
            id=self.cluster["id"],
            parameters={
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

                "save_cluster_data": save_cluster_data
            }
        )

        self.wait()

    def status(self):
        """
        Get status of the Sparkling Water cluster.

        :returns: Sparkling Water cluster status as a string.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import SparklingClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = SparklingClient.get_cluster("test-cluster")
        >>> cluster.status()
        >>> # running

        """
        self._update_cluster()
        return self.cluster['cluster_state']

    def session(self):
        """
        Connect to the remote Spark session and issue commands.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import SparklingClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = SparklingClient.get_cluster("test-cluster")
        >>> cluster.session()

        """
        SparklingShell(self).cmdloop()

    def connect_h2o(self):
        """
        Connects to the underlying H2O cluster. Useful for generating an H2O Autodoc report.

        :returns: H2o session object connected to the cluster.

        :examples:

        >>> # Example code for generating an H2O Autodoc report using h2o() function
        >>> import h2osteam
        >>> import h2o
        >>> from h2o_autodoc import Config
        >>> from h2o_autodoc import render_autodoc
        >>> from h2osteam.clients import SparklingClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> session = SparklingClient.get_cluster("test-cluster")
        >>> h2o_cluster = session.connect_h2o()
        >>> model = h2o_cluster.get_model("my_model")
        >>> config = Config(output_path="report.docx")
        >>> render_autodoc(h2o_cluster, config, model)

        """
        h2o = importlib.import_module("h2o")
        return h2o.connect(config=self.get_h2o_config())

    def get_h2o_config(self):
        """
        Get connection config of the H2O cluster.

        Get connection config of the H2O cluster that can be used as a parameter to h2o.connect.

        :examples:

        >>> import h2o
        >>> import h2osteam
        >>> from h2osteam.clients import SparklingClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = SparklingClient.get_cluster("test-cluster")
        >>> h2o.connect(config=cluster.get_h2o_config())

        """

        connect_params = {'https': self.api.scheme == "https",
                          'verify_ssl_certificates': self.api.verify_ssl,
                          'context_path': self.cluster['context_path'].replace("/", "", 1),
                          'cookies': ["steam-session=%s" % self.api.cookie],
                          'ip': self.api.host,
                          'port': self.api.port}

        if self.api.cacert is not None:
            if _supports_cacert(self.cluster['h2o_version']):
                connect_params['cacert'] = self.api.cacert
            else:
                raise Exception("This version of H2O does not support cacert parameter")

        return {'name': self.cluster['cluster_name'], 'connect_params': connect_params}

    def send_statement(self, statement=None):
        """
        Send a single statement to the remote spark session.

        :param statement: A string representation of statement for the Spark session.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import SparklingClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = SparklingClient.get_cluster("test-cluster")
        >>> cluster.send_statement("f_crimes = h2o.import_file(path ="../data/chicagoCrimes10k.csv",col_types =column_type)")

        """
        return self.api.send_sparkling_statement(self.cluster['id'], statement, 'pyspark')

    def stop(self, save_cluster_data=False):
        """
       Stop a running Sparkling Water cluster.

       :param save_cluster_data: (Optional) Set boolean value to indicate whether you want to save cluster data.
        Such cluster can be restarted with saved data automatically loaded.


       :examples:

       >>> import h2osteam
       >>> from h2osteam.clients import SparklingClient
       >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
       >>> cluster = SparklingClient.get_cluster("test-cluster")
       >>> cluster.stop(save_cluster_data=True)

       """
        self.api.stop_sparkling_cluster(self.cluster['id'], save_cluster_data)
        print("Sparkling Water cluster is stopping, please wait...")
        self._block_until_stopped()

    def delete(self):
        """
        Delete stopped Sparkling Water cluster.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import SparklingClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = SparklingClient.get_cluster("test-cluster")
        >>> cluster.delete()

        """
        self.api.delete_sparkling_cluster(self.cluster['id'])

    def download_logs(self, path=None):
        """
        Download logs of the Sparkling cluster.

        :param path: Path where the Sparkling logs will be saved.

        :examples:

        >>> import h2osteam
        >>> from h2osteam.clients import SparklingClient
        >>> h2osteam.login(url="https://steam.h2o.ai:9555", username="user01", password="token-here", verify_ssl=True)
        >>> cluster = SparklingClient.get_cluster("test-cluster")
        >>> cluster.download_logs("/tmp/test-cluster-logs")

        """
        if path is None:
            raise Exception("Must enter path where logs will be saved")

        self.api.download('/download/sparkling/logs/%d' % self.cluster['id'], path)

        print("Sparkling cluster logs saved to %s" % path)

    def wait(self):
        """
        Wait for the Sparkling Water cluster to finish launching.

        """
        self._block_until_running()

    def _update_cluster(self):
        self.cluster = self.api.get_sparkling_cluster(self.cluster['id'])

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
                print("Sparkling cluster is running")
                break
            else:
                raise Exception("Sparkling cluster failed to start")

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
                print("Sparkling cluster stopped")
                break
            else:
                raise Exception("Sparkling cluster failed to stop")


class SparklingShell(cmd.Cmd, object):
    def __init__(self, session):
        super(SparklingShell, self).__init__()
        self.prompt = '>>> '
        self.session = session

    def preloop(self):
        print('Entering interactive PySparkling session.')
        print('Press Ctrl+D or type \'EOF\' to exit.')
        print('----------------------------------')
        print('SparkSession available as \'spark\'.')
        print('H2OContext available as \'hc\'.')

    def postloop(self):
        print('')
        print('Left interactive PySparkling session.')

    def onecmd(self, s):
        if s == 'EOF':
            return True

        if s != "":
            response = self.session.send_statement(statement=s)
            if response != "":
                print(response)


def _supports_cacert(version):
    return LooseVersion(version) >= LooseVersion("3.26.0.11")
