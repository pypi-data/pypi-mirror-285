import pytest

from pyhectiqlab import Run
from utils import random_uuid
from pyhectiqlab.logging import hectiqlab_logger


@pytest.fixture
def config():
    return {"param": "test", "x": 1}


def test_run_create():
    run = Run(title="test run", project="hectiq-ai/test")


def test_run_retrieve():
    run = Run(rank=1, project="hectiq-ai/test")


@pytest.mark.filterwarnings("error")
def test_run_retrieve_by_id():

    # retrieving first run by id
    run_id = "7abdd377-b702-452c-bfe5-df13f34a99d9"
    run = Run.retrieve_by_id(run_id=run_id)
    assert run is not None
    assert run["id"] == run_id


@pytest.mark.filterwarnings("error")
def test_run_retrieve_not_existing_rank_raises_nothing():
    invalid_rank = -1

    Run(rank=invalid_rank, project="hectiq-ai/test")
    hectiqlab_logger.warning("Expect to see the `No run with rank -1 found` error.")


def test_run_exists():
    assert Run.exists(rank=1, project="hectiq-ai/test") == True
    assert Run.exists(rank=1000, project="hectiq-ai/test") == False
    hectiqlab_logger.warning("Expect to see an error message.")


def test_run_add_config(config):
    run = Run(rank=1, project="hectiq-ai/test")
    config = {"param": "test", "x": 1}
    run.add_config(config)


def test_run_retrieve_config(config):
    run = Run(rank=1, project="hectiq-ai/test")
    assert run.retrieve_config() == config


def test_run_add_artifact():
    import os

    run = Run(rank=1, project="hectiq-ai/test")
    path = os.path.join(os.path.dirname(__file__), "dummy/artifact.txt")
    res = run.add_artifact(path, name="content.txt", wait_response=True)


def test_download_artifact():
    from pyhectiqlab.functional import download_artifact

    download_artifact(id="00d1a48e-39a7-4276-80ec-e763f9a6835c")


def test_run_add_figure():
    run = Run(title=random_uuid(), project="hectiq-ai/test")
    import matplotlib.pyplot as plt

    plt.style.use("dark_background")
    plt.figure(figsize=(3, 3))
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
    run.add_figure(plt, name="test-figure", wait_response=True)


def test_run_set_status():
    run = Run(rank=1, project="hectiq-ai/test")
    run.set_status("test status")


def test_run_add_tag():
    run = Run(rank=1, project="hectiq-ai/test")
    run.add_tags("some")


def test_run_detach_tag():
    run = Run(rank=1, project="hectiq-ai/test")
    run.add_tags("some")
    run.detach_tag("some")


def test_run_attach_dataset():
    run = Run(rank=1, project="hectiq-ai/test")
    print(run.attach_dataset(name="test-dataset", version="1.1", wait_response=True))


def test_run_attach_model():
    run = Run(rank=1, project="hectiq-ai/test")
    print(run.attach_model(name="test-model", version="1.0", wait_response=True))


if __name__ == "__main__":
    pass
