import pytest
from utils import random_uuid
from mock_client import mock_client


@pytest.fixture
def slug():
    return "hectiq-ai/test2"


@pytest.fixture
def teardown_config():
    yield
    import os

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dummy/configs.toml"))
    if os.path.exists(path):
        os.remove(path)


def test_project_create():
    from pyhectiqlab.const import DISABLE_PROJECT_CREATION
    from pyhectiqlab.project import Project
    from pyhectiqlab.client import Client
    import uuid

    id = str(uuid.uuid4())[:6]
    if DISABLE_PROJECT_CREATION:
        return

    with mock_client(Client):
        project = Project.create(name="test" + id)
        assert project["name"] == "test" + id
        assert project["slug"] == "test" + id


def test_project_retrieve(slug):
    from pyhectiqlab.project import Project

    project = Project.retrieve(slug)
    assert project["name"] == slug
    assert project["slug"] == slug


def test_project_exists(slug):
    from pyhectiqlab.project import Project
    import uuid

    fake_id = str(uuid.uuid4())[:6]

    assert Project.exists(slug)
    assert not Project.exists(slug + fake_id)


def test_project_set_get(slug):
    from pyhectiqlab.project import Project

    Project._slug = None

    assert Project.get() == None
    Project.set(slug)
    assert Project.get() == slug


if __name__ == "__main__":
    pass
