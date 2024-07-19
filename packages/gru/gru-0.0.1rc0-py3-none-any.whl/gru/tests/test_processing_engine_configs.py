import pytest, os
from gru.features.processing_engine_configs import ProcessingEngineConfigs


@pytest.fixture
def custom_yaml_processing_engine_configs_fixture():
    """
    Fixtures gives us the ability to define a generic function that
    can be used multiple times. Here custom_yaml_processing_engine_configs
    will be passed as an object where it is defined as an arg in function call.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "data", "test_default_processing_config_batch.yaml")
    return ProcessingEngineConfigs(config_path=config_path)


def test_to_json(custom_yaml_processing_engine_configs_fixture):
    """
    Takes a custom yaml fixture to get the json configs

    Parameters
    ----------
    custom_yaml_processing_engine_configs_fixture : fixture object

    Returns
    -------
    pytest true/false
    """
    expected_result = {
        "deploy-mode": "foo1",
        "spark.kubernetes.driver.memory": "bar1",
        "spark.kubernetes.executor.memory": "foo2",
        "spark.kubernetes.authenticate.driver.serviceAccountName": "bar2",
        "spark.hadoop.fs.s3a.aws.credentials.provider": "foo3",
        "spark.kubernetes.container.image.pullSecrets": "bar3",
        "spark.kubernetes.file.upload.path": "/path/to/config/file",
        "spark.kubernetes.namespace": "foo4",
        "num-executors": 10,
        "spark.executor.cores": 1,
        "spark.driver.cores": 1,
        "spark.kubernetes.driver.limit.cores": "bar4",
        "spark.kubernetes.executor.limit.cores": "foo5",
        "spark.executor.instances": 1,
    }
    assert custom_yaml_processing_engine_configs_fixture.to_json() == expected_result
