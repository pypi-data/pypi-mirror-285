import pytest
import os


@pytest.fixture
def path():
    return os.path.abspath(os.path.join(__file__, "../dummy/artifact.txt"))


def test_add_artifact(path):
    from pyhectiqlab import functional as hl, Run

    run = Run(rank=1, project="hectiq-ai/test")
    res = run.add_artifact(path)
