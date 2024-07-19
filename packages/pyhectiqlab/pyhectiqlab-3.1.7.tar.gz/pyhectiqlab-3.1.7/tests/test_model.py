import pytest
import os
import logging

from utils import random_uuid

from pyhectiqlab.project import Project

logger = logging.getLogger()

Project.set("hectiq-ai/test")


@pytest.fixture
def path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "dummy/"))


@pytest.fixture
def save_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))


@pytest.fixture
def clear_data(data_path):
    yield
    import shutil

    shutil.rmtree(data_path, ignore_errors=True)


def test_model_create_basic(path):
    from pyhectiqlab import Model

    model = Model.create(name="test", path=path)
    logger.info(f"Model created: {model}")


def test_model_create_cli(path):
    import os

    project = Project.get()
    os.system(f"hectiq-lab Model.create --name test --path {path} --project {project}")


def test_model_create_with_run(path):
    from pyhectiqlab import Model, Run

    run = Run(title=f"test {random_uuid()}")
    model = Model.create(name="test", path=path)
    logger.info(f"Model created with run: {model}")


def test_model_create_and_upload(path):
    from pyhectiqlab import Model

    model = Model.create(name="test", path=path, project="hectiq-ai/test", upload=True)
    logger.info(f"Model created and uploaded: {model}")


def test_model_create_and_upload_cli(path):
    import os

    project = Project.get()
    os.system(f"hectiq-lab Model.create --name test --path {path} --project {project} --upload")


def test_download(save_path):
    from pyhectiqlab import Model

    model = Model.download(name="test", version="1.2", project="hectiq-ai/test", path=save_path)
    logger.info(f"Model downloaded: {model}")


def test_download_with_run(save_path):
    from pyhectiqlab import Model, Run

    run = Run(title=f"test {random_uuid()}")
    from pyhectiqlab.run import Run

    run_id = Run.get_id()
    logger.info(f"Run ID: {run_id}")
    model = Model.download(name="test", version="1.2", project="hectiq-ai/test", path=save_path)
    logger.info(f"Model downloaded with run: {model}")


def test_download_cli(save_path):
    import os

    project = Project.get()
    os.system(f"hectiq-lab Model.download --name test --version 1.2 --project {project} --path {save_path} ")


def test_model_retrieve():
    from pyhectiqlab import Model

    model = Model.retrieve(name="test-model", version="1.3", project="hectiq-ai/test")
    assert model["name"] == "test-model"
    assert model["version"] == "1.3"


def test_model_add_tag():
    from pyhectiqlab import Model

    Model.add_tags(tags=["test", "model"], name="test-model", version="1.3", project="hectiq-ai/test")


if __name__ == "__main__":
    pass
