import pytest
import h2osteam
from . import helper
from h2osteam.clients import H2oClient
from h2osteam.clients import SparklingClient


# Hook for failed tests
def pytest_runtest_logreport(report):
    if report.failed:
        try:
            helper.connect_as_std()

            # Download logs for all available H2O and Sparkling Water clusters
            clusters = H2oClient.get_clusters()
            for cluster in clusters:
                log_path = "/mount/logs-" + cluster["cluster_name"] + ".zip"
                H2oClient.get_cluster(cluster["cluster_name"]).download_logs(path=log_path)

            clusters = SparklingClient.get_clusters()
            for cluster in clusters:
                log_path = "/mount/logs-" + cluster["cluster_name"] + ".zip"
                SparklingClient.get_cluster(cluster["cluster_name"]).download_logs(path=log_path)
        except Exception as e:
            print("Test failover failed to collect logs - this could be OK, following exception..")
            print(e)