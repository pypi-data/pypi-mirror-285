import pytest
import h2osteam
from h2osteam.backend.connection import RPCError
from h2osteam.clients import SparklingClient
from . import helper


def get_h2o_version():
    return h2osteam.api().get_sparkling_engines()[0]["h2o_version"]


def _stop_delete_sw_clusters(preserve='default-sparkling-client-cluster'):
    clusters = SparklingClient.get_clusters()
    for cluster in clusters:
        if cluster['cluster_name'] == preserve:
            continue
        if cluster['cluster_state'] != 'stopped':
            SparklingClient.get_cluster(cluster['cluster_name']).stop()

        SparklingClient.get_cluster(cluster['cluster_name']).delete()


def _quick_launch_cluster(name='test'):
    return SparklingClient.launch_sparkling_cluster(name=name,
                                                    version=get_h2o_version(),
                                                    profile_name="default-sparkling-internal")


def setup_module():
    helper.connect_as_std()
    _stop_delete_sw_clusters(preserve='')
    _quick_launch_cluster('default-sparkling-client-cluster')


def teardown_module():
    helper.connect_as_std()
    _stop_delete_sw_clusters(preserve='')


class TestSwClusters:

    def setup_method(self, method):
        helper.connect_as_std()
        # Delete all new clusters
        _stop_delete_sw_clusters()

    def teardown_method(self, method):
        _stop_delete_sw_clusters()

    def test_get_existing_cluster_connection_std_user(self):
        cluster = SparklingClient.get_cluster(name='default-sparkling-client-cluster')
        assert cluster.status() == 'stopped' or cluster.status() == 'running', 'failed to connect to existing cluster'

    def test_existing_cluster_connection_wrong_user(self):
        helper.connect_as_rclient()
        with pytest.raises(RPCError):
            SparklingClient.get_cluster(name='default-sparkling-client-cluster')

    def test_existing_cluster_h2o_connect(self):
        cluster = SparklingClient.get_cluster(name='default-sparkling-client-cluster')
        cluster.get_h2o_config()
        cluster.connect_h2o()
        _stop_delete_sw_clusters(preserve="")  # delete default cluster

    def test_min_param_cluster_launch_std_user(self):
        cluster = _quick_launch_cluster('test1')
        assert cluster.status() == 'running', \
            'Launch Failed (status: ' + cluster.status() + ') When Min Number of Params Specified'

    def test_external_backend_launch(self):
        cluster = SparklingClient.launch_sparkling_cluster(name="python_client_external_be",
                                                           version=get_h2o_version(),
                                                           profile_name="default-sparkling-external")
        assert cluster.status() == 'running', \
            'Launch Failed (status: ' + cluster.status() + ') When External Backend Used'

    def test_max_param_cluster_launch_std_user(self):
        cluster = SparklingClient.launch_sparkling_cluster(name="python_client_all_params_test",
                                                           version=get_h2o_version(),
                                                           profile_name="default-sparkling-internal",
                                                           dataset_size_gb=5,
                                                           using_xgboost=False,
                                                           python_environment_name="Python 3.7 default",
                                                           driver_cores=1,
                                                           driver_memory_gb=1,
                                                           executors=1,
                                                           executor_cores=1,
                                                           executor_memory_gb=1,
                                                           h2o_nodes=1,
                                                           h2o_node_memory_gb=1,
                                                           h2o_node_cpus=0,
                                                           h2o_extra_memory_percent=15,
                                                           max_idle_h=12,
                                                           max_uptime_h=12,
                                                           timeout_s=420,
                                                           yarn_queue="",
                                                           spark_properties={
                                                               "spark.rpc.numRetries": "3",
                                                               "spark.rpc.lookupTimeout": "120s"
                                                           })
        assert cluster.status() == 'running', \
            'Launch Failed (status = ' + cluster.status() + ') When All Params Specified'

        assert cluster.cluster["spark_properties"] == \
               ";spark.rpc.numRetries=3;spark.rpc.lookupTimeout=120s;spark.driver.supervise:false;spark.logConf:false"

    def test_max_param_cluster_launch_dimensions_std_user(self):
        cluster = SparklingClient.launch_sparkling_cluster(name="python_client_all_params_dimension_test",
                                                           version=get_h2o_version(),
                                                           profile_name="default-sparkling-internal",
                                                           dataset_dimension=(5000, 5000),
                                                           using_xgboost=False,
                                                           python_environment_name="Python 3.7 default",
                                                           driver_cores=1,
                                                           driver_memory_gb=1,
                                                           executors=1,
                                                           executor_cores=1,
                                                           executor_memory_gb=1,
                                                           h2o_nodes=1,
                                                           h2o_node_memory_gb=1,
                                                           h2o_node_cpus=0,
                                                           h2o_extra_memory_percent=15,
                                                           max_idle_h=12,
                                                           max_uptime_h=12,
                                                           timeout_s=420,
                                                           yarn_queue="",
                                                           spark_properties={
                                                               "spark.rpc.numRetries": "3",
                                                               "spark.rpc.lookupTimeout": "120s"
                                                           })
        assert cluster.status() == 'running', \
            'Launch Failed (status = ' + cluster.status() + ') When All Params Specified'

        assert cluster.cluster["spark_properties"] == \
               ";spark.rpc.numRetries=3;spark.rpc.lookupTimeout=120s;spark.driver.supervise:false;spark.logConf:false"

    def test_get_all_clusters(self):
        cluster1 = _quick_launch_cluster(name='test1')
        cluster1.stop()  # multiple running clusters is separate test
        _quick_launch_cluster(name='test2')
        clusters = SparklingClient.get_clusters()
        assert len(clusters) >= 2, 'Failed To Get All Existing Clusters'

    def test_stop_cluster(self):
        cluster = _quick_launch_cluster(name='test')
        if cluster.status() == 'running':
            cluster.stop()
        assert cluster.status() == 'stopped', 'Failed To Stop Running Cluster'

    def test_too_many_nodes(self):
        return SparklingClient.launch_sparkling_cluster(name='too_many_nodes',
                                                        version=get_h2o_version(),
                                                        profile_name="default-sparkling-internal",
                                                        driver_cores=4,
                                                        h2o_nodes=9999
                                                        )

    def test_multiple_cluster_launch(self):
        cluster1 = _quick_launch_cluster(name='test1')
        cluster2 = _quick_launch_cluster(name='test2')
        assert cluster2.status() == cluster1.status() == 'running', 'Failed to launch two clusters at once'
