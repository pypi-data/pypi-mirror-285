__version__ = "3.1.7"

from pyhectiqlab.settings import getenv

API_URL = getenv("HECTIQLAB_API_URL", "https://api.lab.hectiq.ai")

from pyhectiqlab.config import Config
from pyhectiqlab.dataset import Dataset
from pyhectiqlab.model import Model
from pyhectiqlab.run import Run
from pyhectiqlab.step import Step
from pyhectiqlab.artifact import Artifact
from pyhectiqlab.project import Project
from pyhectiqlab.message import Message
from pyhectiqlab import functional

from pyhectiqlab.logging import setup_logging
from pyhectiqlab.settings import load_env

setup_logging()
load_env()


__all__ = ["API_URL", "Artifact", "Dataset", "Step", "Model", "Run", "Message", "Config", "Project", "functional"]
