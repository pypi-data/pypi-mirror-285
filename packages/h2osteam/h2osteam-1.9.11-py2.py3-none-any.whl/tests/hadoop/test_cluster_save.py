import h2o
import h2osteam
from h2osteam.clients import H2oClient, SparklingClient
from h2o.estimators.glm import H2OGeneralizedLinearEstimator
from . import helper, test_h2o_client, test_sparkling_client


def launch_h2o_cluster_save():
    return H2oClient.launch_cluster(name="cluster-save-test",
                                    version=test_h2o_client.get_h2o_version(),
                                    nodes=1,
                                    node_memory_gb=5,
                                    save_cluster_data=True,
                                    timeout_s=600)


def launch_sparkling_cluster_save():
    return SparklingClient.launch_sparkling_cluster(name="cluster-save-test",
                                                    version=test_sparkling_client.get_h2o_version(),
                                                    executors=1,
                                                    executor_memory_gb=5,
                                                    save_cluster_data=True,
                                                    timeout_s=600)


def train_h2o_model(model_name):
    titanic = h2o.import_file(
        "https://s3.amazonaws.com/h2o-public-test-data/smalldata/gbm_test/titanic.csv"
    )
    predictors = ["home.dest", "cabin", "embarked", "age"]
    response = "survived"
    titanic["survived"] = titanic["survived"].asfactor()
    train, valid, test = titanic.split_frame(ratios=[0.8, 0.1], destination_frames=["train", "valid", "test"])
    model = H2OGeneralizedLinearEstimator(seed=1234, family="binomial")
    model.train(
        model_id=model_name,
        x=predictors,
        y=response,
        training_frame=train,
        validation_frame=valid,
    )


def train_sparkling_model(session, model_name):
    session.send_statement("from h2o.estimators.glm import H2OGeneralizedLinearEstimator")
    session.send_statement('titanic = h2o.import_file("https://s3.amazonaws.com/h2o-public-test-data/smalldata/gbm_test/titanic.csv")')
    session.send_statement('predictors = ["home.dest", "cabin", "embarked", "age"]')
    session.send_statement('response = "survived"')
    session.send_statement('titanic["survived"] = titanic["survived"].asfactor()')
    session.send_statement('train, valid, test = titanic.split_frame(ratios=[0.8, 0.1], destination_frames=["train", "valid", "test"])')
    session.send_statement('model = H2OGeneralizedLinearEstimator(seed=1234, family="binomial")')
    session.send_statement('model.train( model_id="%s",x=predictors,y=response,training_frame=train,validation_frame=valid,)'% model_name)


# Locally this wont work, use h2o.ls()["key"].tolist() instead
def get_sparkling_models(session):
    return session.send_statement('h2o.ls()')


def update_profile_set_cluster_saving_enabled(profile, type, isEnabled):
    helper.connect_as_admin()
    profile = h2osteam.api().get_profile_by_name(profile)
    profile[type]["is_cluster_saving_enabled"] = isEnabled
    h2osteam.api().update_profile(profile)


class TestClusterSave:

    def test_h2o_cluster_save(self):
        update_profile_set_cluster_saving_enabled("default-h2o", "h2o", True)
        helper.connect_as_std()
        cluster = launch_h2o_cluster_save()
        cluster.connect()
        train_h2o_model("titanic_glm_1")
        cluster.stop(save_cluster_data=True)
        cluster.start(nodes=1,
                      node_memory_gb=5,
                      save_cluster_data=True)
        train_h2o_model("titanic_glm_2")
        cluster.stop(save_cluster_data=True)
        cluster.start()
        models = h2o.ls()
        cluster.stop(save_cluster_data=False)
        cluster.delete()
        update_profile_set_cluster_saving_enabled("default-h2o", "h2o", False)
        assert ["titanic_glm_1"] in models
        assert ["titanic_glm_2"] in models

    def test_sparkling_cluster_save(self):
        update_profile_set_cluster_saving_enabled("default-sparkling-internal", "sparkling_internal", True)
        helper.connect_as_std()
        cluster = launch_sparkling_cluster_save()
        train_sparkling_model(cluster, "titanic_glm_1")
        cluster.stop(save_cluster_data=True)
        cluster.start()
        train_sparkling_model(cluster, "titanic_glm_2")
        cluster.stop(save_cluster_data=True)
        cluster.start()
        models = get_sparkling_models(cluster)
        cluster.stop()
        cluster.delete()
        update_profile_set_cluster_saving_enabled("default-sparkling-internal", "sparkling_internal", False)
        assert "titanic_glm_1" in models
        assert "titanic_glm_2" in models
