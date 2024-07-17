import pytest
import h2osteam
from h2osteam.backend.connection import RPCError
from h2osteam.clients import H2oClient
from h2osteam.clients.h2o import H2oCluster
import os
from . import helper


def get_h2o_version():
    return h2osteam.api().get_h2o_engines()[0]["h2o_version"]


def stop_delete_h2o_clusters(preserve='default-h2o-client-cluster'):
    # Removes all clusters except preserve
    clusters = H2oClient.get_clusters()
    for cluster in clusters:
        if cluster['status'] != 'stopped' and cluster['status'] != 'failed':
            H2oClient.get_cluster(cluster['cluster_name']).stop()
        if cluster['cluster_name'] != preserve:
            H2oClient.get_cluster(cluster['cluster_name']).delete()


def _quick_launch_cluster(name='test'):
    return H2oClient.launch_cluster(name=name,
                                    version=get_h2o_version(),
                                    nodes=1,
                                    node_memory_gb=1)


def setup_module():
    helper.connect_as_std()
    stop_delete_h2o_clusters(preserve='')
    _quick_launch_cluster('default-h2o-client-cluster')


def teardown_module():
    helper.connect_as_std()
    stop_delete_h2o_clusters(preserve='')


class TestH2oClusters:

    def setup_method(self, method):
        helper.connect_as_std()
        # Delete all new clusters
        stop_delete_h2o_clusters()

    def teardown_method(self, method):
        stop_delete_h2o_clusters()

    def test_get_existing_cluster_connection_std_user(self):
        cluster = H2oClient.get_cluster(name='default-h2o-client-cluster')
        assert cluster.status() == 'stopped' or cluster.status() == 'running', 'failed to connect to existing cluster'

    def test_existing_cluster_connection_wrong_user(self):
        helper.connect_as_rclient()
        with pytest.raises(RPCError):
            H2oClient.get_cluster(name='default-h2o-client-cluster')

    def test_min_param_cluster_launch_std_user(self):
        cluster = _quick_launch_cluster('test1')
        assert cluster.status() == 'running', \
            'Launch Failed (status: ' + cluster.status() + ') When Min Number of Params Specified'

    def test_max_param_cluster_launch_std_user(self):
        cluster = H2oClient.launch_cluster(name="python_client_all_params_test",
                                           version=get_h2o_version(),
                                           profile_name="default-h2o",
                                           dataset_size_gb=20,
                                           using_xgboost=True,
                                           nodes=1,
                                           node_cpus=0,
                                           yarn_vcores=0,
                                           node_memory_gb=1,
                                           extra_memory_percent=15,
                                           max_idle_h=12,
                                           max_uptime_h=12,
                                           timeout_s=600,
                                           yarn_queue="",
                                           leader_node_id=0)
        assert cluster.status() == 'running', \
            'Launch Failed (status = ' + cluster.status() + ') When All Params Specified'

    def test_max_param_dimensions_cluster_launch_std_user(self):
        cluster = H2oClient.launch_cluster(name="python_client_all_params_dimensions_test",
                                           version=get_h2o_version(),
                                           profile_name="default-h2o",
                                           dataset_dimension=(10000, 10000),
                                           using_xgboost=True,
                                           nodes=1,
                                           node_cpus=0,
                                           yarn_vcores=0,
                                           node_memory_gb=1,
                                           extra_memory_percent=15,
                                           max_idle_h=12,
                                           max_uptime_h=12,
                                           timeout_s=600,
                                           yarn_queue="",
                                           leader_node_id=0)

        assert cluster.status() == 'running', \
            'Launch Failed (status = ' + cluster.status() + ') When All Params Specified'

    def test_cluster_launch_too_little_memory(self):
        with pytest.raises(RPCError, match='.*value lower than allowed.*'):
            H2oClient.launch_cluster(name='launch_test_fail',
                                     version=get_h2o_version(),
                                     nodes=1,
                                     node_memory_gb=0)

    def test_get_all_clusters(self):
        cluster1 = _quick_launch_cluster(name='test1')
        cluster1.stop()  # multiple running clusters is separate test
        _quick_launch_cluster(name='test2')
        clusters = H2oClient.get_clusters()
        assert len(clusters) >= 2, 'Failed To Get All Existing Clusters'

    def test_stop_cluster(self):
        cluster = _quick_launch_cluster(name='test')
        if cluster.status() == 'running':
            cluster.stop()
        assert cluster.status() == 'stopped', 'Failed To Stop Running Cluster'

    def test_too_many_nodes(self):
        with pytest.raises(RPCError, match='.*number of nodes: value higher than allowed.*'):
            H2oClient.launch_cluster(name='launch_test_fail',
                                     version=get_h2o_version(),
                                     nodes=999999,
                                     node_memory_gb=1)

    def test_multiple_cluster_launch(self):
        cluster1 = _quick_launch_cluster(name='test1')
        cluster2 = _quick_launch_cluster(name='test2')
        assert cluster2.status() == cluster1.status() == 'running', 'Failed to launch two clusters at once'

    def test_xgboost(self):
        # Skip if LOCAL env variable is set - not enough memory to run this test
        if "LOCAL" in os.environ:
            pytest.skip('Wont create external XGBoost cluster on local environment')

        cluster = _quick_launch_cluster(name='testxgb')
        cluster.connect()

        import h2o
        from h2o.estimators import H2OXGBoostEstimator

        df = h2o.import_file(path="https://s3.amazonaws.com/h2o-public-test-data/smalldata/gbm_test/ecology_model.csv")
        df["Angaus"] = df["Angaus"].asfactor()
        model = H2OXGBoostEstimator()
        model.train(x=list(range(2, df.ncol)), y="Angaus", training_frame=df)

        cluster.stop()
