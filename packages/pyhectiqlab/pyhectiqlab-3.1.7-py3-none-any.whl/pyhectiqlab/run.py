import os
import tempfile
import slugify
import clisync

from typing import Any, List, Optional, Union, Literal, Tuple

from pyhectiqlab import API_URL
from pyhectiqlab import Config
from pyhectiqlab.project import Project
from pyhectiqlab.artifact import Artifact
from pyhectiqlab.tag import Tag
from pyhectiqlab.model import Model
from pyhectiqlab.dataset import Dataset
from pyhectiqlab.versions import PackageVersion
from pyhectiqlab.step import Step

from pyhectiqlab.client import Client
from pyhectiqlab.decorators import classproperty, functional_alias, no_git_diff
from pyhectiqlab.metrics import MetricsManager
from pyhectiqlab.logging import hectiqlab_logger as logger


class Run:
    _metrics: Optional[MetricsManager] = None
    _tmp_artifacts: Optional[str] = None
    _id: Optional[str] = None
    _rank: Optional[int] = None
    _slug: Optional[str] = None
    _step: Optional[int] = None
    _config: Optional[dict] = None
    _client: Client = Client

    def __init__(
        self,
        rank: Optional[int] = None,
        title: Optional[str] = None,
        project: Optional[str] = None,
        category: Literal[None, "develop", "evaluation", "test", "training"] = None,
        config: Optional[dict] = None,
        reuse: Optional[bool] = False,
    ):
        if rank is not None and isinstance(rank, int):
            self.retrieve(rank, project)
        elif isinstance(rank, str) or rank is None:
            title = title or rank  # support for positional argument
            if title is None:
                logger.warning("No run title or rank provided, using `Untitled run` as title.")
                title = "Untitled run"
            self.create(title=title, project=project, category=category, config=config, reuse=reuse)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._metrics:
            self._metrics.flush_cache()
        if Run.id is None:
            return
        if exc_type is not None:
            if Step.id:
                Step.end(status="failed")
            Run._update(run_id=Run.id, status="failed", package_versions=PackageVersion.all())
        else:
            if Step.id:
                Step.end(status="completed")
            Run._update(run_id=Run.id, status="completed", package_versions=PackageVersion.all())

    @staticmethod
    @functional_alias()
    def track_version(repos: Union[str, List[str], None] = None, run_id: Optional[str] = None):
        """Track the git status of the given repositories.

        Args:
            repos (List[str]): List of modules for which the files are located in a git repertoire.
            run_id (str): Id of the run to update. If None, the current run ID is used. Default: None.
        """
        if not isinstance(repos, list) and (repos is not None):
            repos = [repos]
        if info := PackageVersion.all(repos=repos):
            Run._update(run_id=run_id, package_versions=info)

    @staticmethod
    def setup(**kwargs):
        """Setup the run with the given `id` and `rank`."""
        Run._id = kwargs.get("id")
        Run._rank = kwargs.get("rank")

    @classproperty
    def tmp_artifacts(cls):
        if cls._tmp_artifacts is None:
            cls._tmp_artifacts = tempfile.mkdtemp()
        return cls._tmp_artifacts

    @classproperty
    def rank(cls) -> Optional[int]:
        return cls._rank

    @classproperty
    def slug(cls) -> Optional[str]:
        if cls._slug is None and cls._id is not None:
            run_info = cls.retrieve_by_id(run_id=cls._id)
            cls._slug = slugify.slugify(run_info.get("title")) if run_info is not None else None
        return cls._slug

    @classproperty
    def id(cls) -> Optional[str]:
        return cls._id

    @classproperty
    def category(cls) -> Optional[str]:
        if cls._category is None:
            cls._category = (cls.get(["category"]) or {}).get("category")
        return cls._category

    @classproperty
    def config(cls) -> Optional[dict]:
        return cls._config

    @staticmethod
    @functional_alias("get_run_id")
    def get_id(id: Optional[str] = None):
        return id or Run.id

    @staticmethod
    @functional_alias("get_run_rank")
    def get_rank(rank: Optional[int] = None) -> Optional[int]:
        return rank or Run.rank

    @staticmethod
    @functional_alias("get_run_slug")
    def get_slug(slug: Optional[str] = None) -> Optional[str]:
        return slug or Run.slug

    @staticmethod
    @functional_alias("run_is_ready")
    def ready() -> bool:
        """Check if the run is ready."""
        return Run.id is not None

    @staticmethod
    @functional_alias("create_run")
    @no_git_diff()
    @clisync.include()
    def create(
        title: Optional[str] = None,
        project: Optional[str] = None,
        category: Literal[None, "develop", "evaluation", "test", "training"] = None,
        config: Union[dict, None] = None,
        tags: Optional[List[str]] = None,
        reuse: bool = False,
    ) -> dict:
        """
        Creates a new run.

        Args:
            title (str): The title of the run.
            project (str): The project of the run. If None, the current project is used.
            category (str): The category of the run in [None, 'develop', 'evaluation', 'test', 'training']. Default: None.
            config (dict): The configuration dict of the run. Default: None.
            tags (list): The tags of the run. Default: None.
            reuse (bool): Set to True to reuse the run if the title already exists. Default: False.

        Raises:
            logging.error: If the project is not found, creation is skipped and offline mode is enabled.
        """

        project = Project.get(project)
        if project is None:
            # If project is None, we either are or must be in offline mode.
            if Run._client.online():
                logger.error(f"Could not create run `{title}`, project not found. Continuing in offline mode...")
                Run._client.online(False)
            return
        Project.set(project)

        data = dict(
            title=title,
            project=project,
            category=category,
            config=config or {},
            tags=tags or [],
            get_if_title_collision=reuse,
        )
        run = Run._client.post("/app/runs", json=data, wait_response=True)
        if run is None:
            logger.error("Run failed to create.")
            return False
        if run.get("reused"):
            logger.warning(
                f"`{title}` already exists in this project. You've been connected to this existing run (rank {run.get('rank')})."
            )

        Run.setup(**run)
        Run._update(run_id=Run.id, status="initiated", package_versions=PackageVersion.all())
        return run

    @staticmethod
    @functional_alias("retrieve_run")
    @no_git_diff()
    @clisync.include()
    def retrieve(
        rank: Optional[int] = None,
        project: Optional[str] = None,
        fields: Optional[List[str]] = None,
        setup_with: bool = True,
    ):
        """
        Retrieves a run from the server.
        Use this method to attach to an existing run.

        Args:
            rank (int, optional): The rank of the run. If None, the current run rank is used. Default: None.
            project (str, optional): The project of the run. If None, the project is taken from the context. Default: None.
            fields (List[str]): The fields to retrieve. Default: None.
            setup_with (bool): Set to True to setup the run with the result. Default: True.

        Raises:
            logging.error: If the project is not found, retrieval is skipped and offline mode is enabled.
        """
        rank = rank or Run.rank
        project = Project.get(project)
        if project is None:
            # If project is None, we either are or must be in offline mode.
            if Run._client.online():
                logger.error(f"Could not retrieve run {rank}, project not found. Continuing in offline mode...")
                Run._client.online(False)
            return
        Project.set(project)

        run_info = Run._client.get(
            "/app/runs/retrieve", params=dict(rank=rank, project=project, fields=fields), wait_response=True
        )
        if run_info is None:
            logger.error(f"No run with {rank} found in project {project}")
            return
        if setup_with:
            Run.setup(**run_info)
        return run_info

    @staticmethod
    @functional_alias("retrieve_run_by_id")
    @no_git_diff()
    @clisync.include()
    def retrieve_by_id(
        run_id: Optional[str] = None,
        fields: Optional[List[str]] = None,
        setup_with_result: Optional[bool] = False,
    ):
        """
        Retrieves a run from the server.
        Use this method to attach to an existing run.

        Args:
            id (int): The ID of the run. If None, the current run ID is used. Default: None.
            fields (List[str]): The fields to retrieve. Default: None.
            setup_with_result (bool): Set to True to setup the run with the result. Default: False.

        Raises:
            logging.error: If the run is not found, retrieval is skipped and None is returned.
        """

        run_id = run_id or Run.id
        if run_id is None:
            logger.error("Could not retrieve run by ID, no ID found.")
            return
        run_info = Run._client.get(f"/app/runs/{run_id}", params=dict(fields=fields), wait_response=True)
        if run_info is None:
            logger.error(f"Could not retrieve run {run_id} by ID, run not found.")
            return
        if setup_with_result:
            Run.setup(**run_info)
        return run_info

    @staticmethod
    @functional_alias()
    @clisync.include()
    def retrieve_config_by_id(run_id: Optional[str] = None) -> dict:
        """Retrieve a config from a run.
        If the run does not have a config, an empty config is returned.

        Args:
            run_id (str, optional): The ID of the run. If None, the current run ID is used. Default: None.
            project (str, optional): Project name. If None, the current project is used. Default: None.

        Raises:
            logging.error: If the run is not found, returns an empty dict.
        """
        run_info = Run.retrieve_by_id(run=run_id, fields=["config"], setup_with_result=False)
        if run_info is None:
            logger.error(f"Could not retrieve config by run id {run_id}, run not found")
            return {}

        return run_info.get("config", {})

    @staticmethod
    @functional_alias()
    @clisync.include()
    def retrieve_config(rank: Optional[int] = None, project: Optional[str] = None) -> dict:
        """Retrieve a config from a run.
        If the run does not have a config, an empty config is returned.

        Args:
            rank (int): Run rank. If None, the current run rank is used. Default: None.
            project (str, optional): Project name. If None, the current project is used. Default: None.

        Raises:
            logging.error: If the run is not found, returns an empty dict.
        """
        run_info = Run.retrieve(rank=rank, project=project, fields=["config"], setup_with=False)
        if run_info is None:
            logger.error(f"Could not retrieve config from run {rank} in project {project}, run not found.")
            return {}

        return run_info.get("config", {})

    @staticmethod
    @functional_alias("run_exists")
    @clisync.include()
    def exists(rank: int, project: Optional[str] = None) -> bool:
        """
        Check if a run exists.

        Args:
            rank (int): The rank of the run.
            project (str): The project of the run. If None, the project is taken from the context. Default: None.
        """
        res = Run._client.get("/app/runs/retrieve", params=dict(rank=rank, project=project), wait_response=True)
        return res is not None

    @staticmethod
    def _update(run_id: Optional[str] = None, wait_response: bool = False, **kwargs):
        """Update the run.

        Args:
            run_id (str, optional): The ID of the run. If None, the current run ID is used. Default: None.
            wait_response (bool): Set to True to wait for the response. Default: False.
            **kwargs: Additional arguments to update.

        Raises:
            logging.error: If the run is not found, the update is not performed and it returns None.
        """
        run_id = run_id or Run.id
        if run_id is None:
            logger.error("No run to update, ID not found.")
            return
        return Run._client.patch(f"/app/runs/{run_id}", json=kwargs, wait_response=wait_response)

    @staticmethod
    @functional_alias("set_run_category")
    @clisync.include()
    def set_category(category: Literal["develop", "evaluation", "test", "training"], run_id: Optional[str] = None):
        """Set the category of the run."""
        Run._update(run_id=run_id, category=category)

    @staticmethod
    @functional_alias("rename_run")
    @clisync.include()
    def rename(title: str, run_id: Optional[str] = None):
        """Rename the run with a new title.

        Args:
            title (str): The new title of the run.
        """
        Run._update(run_id=run_id, title=title)

    @staticmethod
    @functional_alias()
    @clisync.include()
    def add_artifact(
        path: str,
        name: Optional[str] = None,
        step: Optional[int] = None,
        run_id: Optional[str] = None,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """
        Log a file as an artifacts. If a file already exists with the name, it will be overwritten.

        Args:
            path (str) : Path to the file.
            name (str, optional): Name of the artifact or the group of artifacts. If None, the name is the basename of the file. Default: None.
            step (int, optional): The optional step stamp of the artifacts. If None, the artifacts is not considered as a step artifact. Default: None.
            run_id (str, optional): ID of the run. If None, the current run ID is used. Default: None.
            project (str, optional): The project of the artifact. If None, the current project is used. Default: None.
            wait_response (bool): Set to true to upload sync. If False, the upload is made in background. Default: False.
            verbose (bool): Set to True to show the upload progress. Default: True.

        Raises:
            logging.error: If the project is not found or if the run ID is not found, the artifact creation is not performed.
        """
        run_id = Run.get_id(run_id)
        project = Project.get(project)
        if project is None:
            logger.error("Could not create artifact, project not found.")
            return
        if run_id is None:
            logger.error("Could not create artifact, run ID not found.")
            return
        return Artifact.create(
            path,
            Run.get_id(run_id),
            Project.get(project),
            name=name,
            group=name,
            step=step,
            wait_response=wait_response,
        )

    @staticmethod
    @functional_alias()
    def add_figure(
        figure,
        name: str,
        step: Optional[int] = None,
        dpi: int = 200,
        extension: str = "png",
        wait_response: bool = False,
        run_id: Optional[str] = None,
        project: Optional[str] = None,
        **kwargs,
    ):
        """
        Save a matplotlib figure on a temp dir and push the image to the lab.

        Args:
            figure (matplotlib.pyplot.Figure): The figure to save.
            name (str): The name of the artifact.
            step (int): The optional step stamp of the artifacts. If None, the artifacts is not considered as a step artifact. Default: None.
            dpi (int): The dpi of the figure. Default: 200.
            extension (str): The extension of the figure. Default: "png".
            wait_response [bool]: Set to true to upload sync. If False, the upload is made in background. Default: False.
            run_id (str): The ID of the run. If None, the current run ID is used. Default: None.
            project (str): The project of the artifact. If None, the current project is used. Default: None.
            **kwargs: Additional arguments to pass to the savefig method.
        """

        basename, name_ext = os.path.splitext(name)
        if name_ext != "":
            extension = name_ext.strip(".")
        else:
            extension = (extension or "png").strip(".")

        slug_name = slugify.slugify(basename)
        fname = os.path.join(Run.tmp_artifacts, slug_name + "." + extension)
        figure.savefig(fname, dpi=dpi, format=extension, bbox_inches="tight", **kwargs)

        return Run.add_artifact(
            fname, name=name, step=step, wait_response=wait_response, run_id=run_id, project=project
        )

    @staticmethod
    @functional_alias()
    def add_config(config: Union[Config, dict[str, Any]], run_id: Optional[str] = None):
        """Attach a config to the run."""
        if isinstance(config, Config):
            config = config.to_dict()
        Run._config = config
        return Run._update(run_id=run_id, config=config)

    @staticmethod
    @functional_alias()
    def add_metric(key: str, step: int, value: float):
        """
        Add a metric to the run.

        Args:
            key (str): The key of the metric.
            step (int): The step of the metric.
            value (float): The value of the metric.

        Note:
            The metrics are not pushed immediately. They are pushed when the `Run._push_metrics`
            method is called inside the MetricsManager. See `pyhectiqlab.metrics.MetricsManager`.
        """
        if Run._metrics is None:
            Run._metrics = MetricsManager(push_method=Run._push_metrics, run_id=Run.id)
        return Run._metrics.add(key, step, value)

    @staticmethod
    @functional_alias()
    def get_agg_metrics(key: str, run_id: Optional[str] = None) -> List[Tuple[Union[int, float], Union[int, float]]]:
        """Get the aggregated metrics for the given key.

        Args:
            key (str): The key of the metric.
            run_id (str, optional): The ID of the run. If None, the current run ID is used. Default: None.

        Returns:
            list[tuple[number]]: The aggregated metrics.

        Raises:
            logging.error: If the run ID is not found, it returns an empty list.
        """
        run_id = run_id or Run.id
        if run_id is None:
            logger.error("No run to get aggregated metrics from.")
            return []
        # This does not work. Need to fix it.
        return MetricsManager.get_agg(key, run_id)

    @staticmethod
    def _push_metrics(
        key: str,
        values: List[Tuple[Union[int, float], Union[int, float], Union[int, float]]],
        run_id: Optional[str] = None,
    ):
        """Push the metrics to the server.
        Do not use this method directly. Use the `add_metric` method instead.
        values is a list of tuples (step, value, timestamp).

        Args:
            key (str): The key of the metric.
            values (List[Tuple[Union[int, float], Union[int, float], Union[int, float]]): The values of the metric.
            run_id (str, optional): The ID of the run. If None, the current run ID is used. Default: None.
        """
        run_id = run_id or Run.id
        if key is None or run_id is None or len(values) == 0:
            return
        data = dict(name=key, values=values, run=run_id)
        Run._client.post("/app/metrics", json=data, wait_response=False)

    @staticmethod
    @functional_alias("start_step")
    def start(
        name: str,
        run_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
        status: Optional[str] = None,
    ):
        """
        Start a new step.

        Args:
            title (str): Title of the step.
        """
        if Step.id is not None:
            Step.end()

        return Step.start(
            name=name,
            run_id=Run.get_id(run_id),
            description=description,
            metadata=metadata,
            status=status,
        )

    @staticmethod
    @functional_alias("end_step")
    def end(run_id: Optional[str] = None, status: Optional[str] = None):
        """End the current step."""
        return Step.end(status=status)

    @staticmethod
    @functional_alias()
    def attach_model(
        name: str,
        version: str,
        run_id: Optional[str] = None,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """
        Attach a model to the run.

        Args:
            name (str): The name of the model.
            version (str): The version of the model. If None, the latest version is attached. Default: None.
            run_id (str, optional): The ID of the run. If None, the current run ID is used. Default: None.
            project (str, optional): The project of the run. If None, the current project is used. Default: None.
            wait_response (bool): Set to true to detach sync. If False, the detachment is made in background. Default: False.
        """
        return Model.attach(
            name=name,
            version=version,
            run_id=Run.get_id(run_id),
            project=Project.get(project),
            wait_response=wait_response,
        )

    @staticmethod
    @functional_alias()
    def detach_model(
        name: str,
        version: str,
        run_id: Optional[int] = None,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """
        Detach a model from the run.

        Args:
            name (str): The name of the model.
            version (str): The version of the model. If None, the latest version is detached. Default: None.
            run_id (str, optional): The ID of the run. If None, the current run ID is used. Default: None.
            project (str, optional): The project of the run. If None, the current project is used. Default: None.
            wait_response (bool): Set to true to detach sync. If False, the detachment is made in background. Default: False.
        """

        return Model.detach(
            name=name,
            version=version,
            run_id=Run.get_id(run_id),
            project=Project.get(project),
            wait_response=wait_response,
        )

    @staticmethod
    @functional_alias()
    def attach_dataset(
        name: str,
        version: str,
        run_id: Optional[int] = None,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """
        Attach a dataset to the run.

        Args:
            name (str): The name of the dataset.
            version (str): The version of the dataset.  If None, the latest version is detached. Default: None.
            run_id (str, optional): The ID of the run. If None, the current run ID is used. Default: None.
            project (str, optional): The project of the run. If None, the current project is used. Default: None.
            wait_response (bool): Set to true to detach sync. If False, the detachment is made in background. Default: False.
        """
        return Dataset.attach(
            name=name,
            version=version,
            run_id=Run.get_id(run_id),
            project=Project.get(project),
            wait_response=wait_response,
        )

    @staticmethod
    @functional_alias()
    def detach_dataset(
        name: str,
        version: str,
        run_id: Optional[int] = None,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """
        Detach a dataset to the run.

        Args:
            name (str): The name of the dataset.
            version (str): The version of the dataset.  If None, the latest version is detached. Default: None.
            run_id (str, optional): The ID of the run. If None, the current run ID is used. Default: None.
            project (str, optional): The project of the run. If None, the current project is used. Default: None.
            wait_response (bool): Set to true to detach sync. If False, the detachment is made in background. Default: False.
        """
        return Dataset.detach(
            name=name,
            version=version,
            run_id=Run.get_id(run_id),
            project=Project.get(project),
            wait_response=wait_response,
        )

    @staticmethod
    @functional_alias("set_run_status")
    @clisync.include()
    def set_status(status: str, run_id: Optional[str] = None):
        """Set the run to the given status."""
        Run._update(run_id=run_id, status=status)

    @staticmethod
    @functional_alias("failed")
    @clisync.include()
    def failed(run_id: Optional[str] = None):
        """Set the run to the failed status."""
        Run.set_status(run_id=run_id, status="failed")

    @staticmethod
    @functional_alias("stopped")
    @clisync.include()
    def stopped(run_id: Optional[str] = None):
        """Set the run to the stopped status."""
        Run.set_status(run_id=run_id, status="stopped")

    @staticmethod
    @functional_alias("completed")
    @clisync.include()
    def completed(run_id: Optional[str] = None):
        """Set the run to the completed with success status."""
        Run.set_status(run_id=run_id, status="completed")

    @staticmethod
    @functional_alias("pending")
    @clisync.include()
    def pending(run_id: Optional[str] = None):
        """Set the run to the pending status."""
        Run.set_status(run_id=run_id, status="pending")

    @staticmethod
    @functional_alias("running")
    @clisync.include()
    def running(run_id: Optional[str] = None):
        """Set the run to the running status."""
        Run.set_status(run_id=run_id, status="running")

    @staticmethod
    @functional_alias("training")
    @clisync.include()
    def training(run_id: Optional[str] = None):
        """Set the run to the training status."""
        Run.set_status(run_id=run_id, status="training")

    @staticmethod
    @functional_alias("add_tags_to_run")
    @clisync.include()
    def add_tags(tags: Union[str, List[str]], run_id: Optional[str] = None, project: Optional[str] = None):
        """Add a tag to the run.
        For functional alias, use `attach_tags_to_run`.

        Args:
            title (str): The new title of the run.
            run_id (str): The ID of the run. If None, the current run ID is used. Default: None.
            project (str): The project of the run. If None, the current project is used. Default: None.

        Raises:
            logging.error: If the run ID is not found, the tag is not attached.
        """
        if isinstance(tags, str):
            tags = [tags]

        run_id = Run.get_id(run_id)
        if run_id is None:
            logger.error("No run to attach tags to.")
            return
        Tag.attach_to_run(tags, run_id=Run.get_id(run_id), project=Project.get(project))

    @staticmethod
    @functional_alias("detach_tag_from_run")
    @clisync.include()
    def detach_tag(tag: str, run_id: Optional[str] = None, project: Optional[str] = None):
        """Remove a tag from the run.
        For functional alias, use `detach_tag_from_run`.

        Args:
            title (str): The new title of the run.
            run_id (str): The ID of the run. If None, the current run ID is used. Default: None.
            project (str): The project of the run. If None, the current project is used. Default: None.

        Raises:
            logging.error: If the run ID is not found, the tag is not detached.
        """

        run_id = Run.get_id(run_id)
        if run_id is None:
            logger.error("No run to attach tags to.")
            return
        Tag.detach_from_run(tag=tag, run_id=run_id, project=Project.get(project))

    def __str__(self):
        pad = 8
        path = "/" + Project.get() + "/runs/" + str(self.rank)  # TBD
        return (
            f"<Run {self.rank}>"
            f"\n{'Project'.ljust(pad)}: {Project.get()}"
            f"\n{'author'.ljust(pad)}: {self._client.auth.user}"
            f"\n{'online'.ljust(pad)}: {self._client.auth.online}"
            f"\n{'url'.ljust(pad)}: {API_URL+path} "
        )
