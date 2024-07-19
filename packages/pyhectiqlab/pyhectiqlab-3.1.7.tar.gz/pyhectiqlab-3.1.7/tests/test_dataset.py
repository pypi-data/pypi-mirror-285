import pytest
import os

import logging

logger = logging.getLogger()
from utils import random_uuid

from pyhectiqlab.project import Project

Project.set("hectiq-ai/test")
logger.info("🚨 Testing pyhectiqlab.")
logger.info(f"Version: {__import__('pyhectiqlab').__version__}")
logger.info(f"Path: {__import__('pyhectiqlab').__file__}")
logger.info(f"Project: {Project.get()}")


@pytest.fixture
def source():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "dummy/"))


@pytest.fixture
def source_single_file():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "dummy/image.png"))

@pytest.fixture
def save_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))


@pytest.fixture
def clear_data(data_path):
    yield
    import shutil

    shutil.rmtree(data_path, ignore_errors=True)


def test_dataset_create():
    from pyhectiqlab import Dataset

    dataset = Dataset.create(name="test", source="dummy")
    logger.info(f"Dataset created: {dataset}")


def test_dataset_create_cli():
    import os

    project = Project.get()
    os.system(f"hectiq-lab Dataset.create --name test --source dummy --project {project}")


def test_dataset_create_with_run():
    from pyhectiqlab import Dataset, Run

    run = Run(title=f"test {random_uuid()}")
    dataset = Dataset.create(name="test", source="dummy")
    logger.info(f"Dataset created with run: {dataset}")


def test_dataset_create_and_upload(source):
    from pyhectiqlab import Dataset

    dataset = Dataset.create(name="test", source=source, project="hectiq-ai/test", upload=True)
    logger.info(f"Dataset created and uploaded: {dataset}")

def test_dataset_create_and_upload_single_file(source_single_file):
    from pyhectiqlab import Dataset

    dataset = Dataset.create(name="single-file", source=source_single_file, project="hectiq-ai/test", upload=True)
    logger.info(f"Dataset created and uploaded: {dataset}")

def test_dataset_create_and_upload_cli(source):
    import os

    project = Project.get()
    os.system(f"hectiq-lab Dataset.create --name test --source {source} --project {project} --upload")


def test_download(save_path):
    from pyhectiqlab import Dataset

    dataset = Dataset.download(name="test", version="1.2", project="hectiq-ai/test", path=save_path)
    logger.info(f"Dataset downloaded: {dataset}")


def test_download_with_run(save_path):
    from pyhectiqlab import Dataset, Run

    run = Run(title=f"test {random_uuid()}")
    from pyhectiqlab.run import Run

    run_id = Run.get_id()
    logger.info(f"Run ID: {run_id}")
    dataset = Dataset.download(name="test", version="1.2", project="hectiq-ai/test", path=save_path)
    logger.info(f"Dataset downloaded with run: {dataset}")


def test_download_cli(save_path):
    import os

    project = Project.get()
    os.system(f"hectiq-lab Dataset.download --name test --version 1.2 --project {project} --path {save_path} ")


def test_dataset_retrieve():
    from pyhectiqlab import Dataset

    dataset = Dataset.retrieve(name="test-dataset", version="1.3", project="hectiq-ai/test")
    assert dataset["name"] == "test-dataset"
    assert dataset["version"] == "1.3"


def test_dataset_add_tag():
    from pyhectiqlab import Dataset

    Dataset.add_tags(tags=["test", "dataset"], name="test-dataset", version="1.3", project="hectiq-ai/test")


if __name__ == "__main__":
    pass
