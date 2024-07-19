import slugify
import clisync
import logging

from typing import Optional, List
from pyhectiqlab.settings import getenv
from pyhectiqlab.client import Client
from pyhectiqlab.decorators import classproperty, functional_alias
from pyhectiqlab.logging import hectiqlab_logger as logger


class Project:
    """
    Project class for handling project related operations.

    Attributes:
        slug (str): Slug of the project.
    """

    _slug: str = None
    _repos: Optional[List[str]] = None
    _client: Client = Client

    @classproperty
    def slug(cls) -> str:
        if cls._slug is None and getenv("HECTIQLAB_PROJECT") is not None:
            cls.set(getenv("HECTIQLAB_PROJECT"))
        return cls._slug

    @classmethod
    def allow_dirty(cls) -> bool:
        if not Client.online():
            return True
        if getenv("HECTIQLAB_ALLOW_DIRTY") == "no":
            return False
        return True

    @classmethod
    def repos(cls) -> List[str]:
        if cls._repos is None and getenv("HECTIQLAB_REPOS") is not None:
            cls._repos = getenv("HECTIQLAB_REPOS").split(",")
        return cls._repos

    @staticmethod
    @clisync.include()
    def create(
        name: str,
        repo: Optional[str] = None,
        force_no_git_diff: bool = True,
    ) -> Optional[str]:
        """
        Create a project.

        Args:
            name (str): Name of the project.
            repo (str, optional): Repository URL. Default: None.
            force_no_git_diff (bool): Force no git diff. Default: True.
        """
        from pyhectiqlab.const import DISABLE_PROJECT_CREATION

        if DISABLE_PROJECT_CREATION:
            logger.error("Project creation is disabled. Continuing anyway...")
            return
        slug = "/".join([slugify.slugify(n) for n in name.split("/")])
        body = {
            "slug": slug,
            "name": name,
            "repo": repo,
            "force_no_git_diff": force_no_git_diff,
        }
        project = Project._client.post("/app/projects", json=body, wait_response=True)
        if project is None:
            logger.error("Failed to create project.")
            return
        logger.info(f"Project `{slug}` created.")
        return slug

    @staticmethod
    def exists(slug: str) -> bool:
        project = Project._client.get(f"/app/projects/{slug}", wait_response=True)
        if project is None:
            return False
        return True

    @staticmethod
    @functional_alias("retrieve_project")
    @clisync.include()
    def retrieve(
        slug: str,
        fields: Optional[List[str]] = [],
    ) -> Optional[dict]:
        """Retrieve a project info.

        Args:
            slug (str): Slug of the project.
            fields (List): Fields to retrieve.
        """
        info = Project._client.get(f"/app/projects/{slug}", params={"fields": fields}, wait_response=True)
        return info

    @staticmethod
    @functional_alias("get_project")
    def get(slug: Optional[str] = None):
        return slug or Project.slug

    @staticmethod
    @functional_alias("set_project")
    def set(slug: str):
        if slug is None:
            return
        if not Project.exists(slug):
            # If project does not exist, we either are or must be offline.
            if Project._client.online():
                logger.error(f"The project `{slug}` does not exist. Continuing in offline mode.")
                Project._client.online(False)
            return
        Project._slug = slug
