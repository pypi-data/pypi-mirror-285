import os
import clisync

from typing import Optional, List

from pyhectiqlab.project import Project
from pyhectiqlab.client import Client
from pyhectiqlab.decorators import functional_alias
from pyhectiqlab.utils import is_running_event_loop
from pyhectiqlab.logging import hectiqlab_logger as logger


class Artifact:
    _client: Client = Client

    @staticmethod
    @clisync.include(wait_response=True)
    def create(
        local_path: str,
        run_id: str,
        project: str,
        name: Optional[str] = None,
        step: Optional[int] = None,
        group: Optional[str] = None,
        wait_response: bool = False,
    ):
        """
        Upload an artifact to a run.

        Args:
            local_path (str): Path to the file to upload.
            run_id (str): ID of the run.
            project (str): ID of the project.
            name (str, optional): Name of the artifact. If None, the basename of the file is used. Default: None.
            step (int, optional): Step number. If None, the artifact is not considered as a step artifact. Default: None.
            group (str, optional): Group name. If None, the group is determined from the local_path. Default: None.
            wait_response (bool): Set to true to upload sync. If False, the upload is made in background. Default: False.

        Raises:
            logger.error: If `local_path`, `run_id` and `project` are not provided, it does not upload the artifact and returns None.
        """

        if local_path is None or run_id is None or project is None:
            logger.error("Parameters `local_path`, `run_id` and `project` are required.")
            return
        name = name or os.path.basename(local_path)
        group = group or os.path.basename(local_path)
        num_bytes = os.path.getsize(local_path)
        extension = os.path.splitext(local_path)[1]

        json = {
            "name": name,
            "num_bytes": num_bytes,
            "group": group,
            "step": step,
            "project": project,
            "run": run_id,
            "extension": extension,
        }

        def composition_sync(**kwargs):
            artifact = Client.post("/app/artifacts", wait_response=True, json=json)
            if not artifact:
                return
            return Client.upload_sync(local_path=local_path, policy=artifact.get("upload_policy"), **kwargs)

        async def composition_async(**kwargs):
            artifact = Client.post("/app/artifacts", wait_response=True, json=json)
            if not artifact:
                return
            return await Client.upload_async(local_path=local_path, policy=artifact.get("upload_policy"), **kwargs)

        if is_running_event_loop():
            Client.execute(composition_sync, wait_response=wait_response, is_async_method=False, with_progress=True)
        else:
            Client.execute(composition_async, wait_response=wait_response, is_async_method=True, with_progress=True)
        return local_path

    @staticmethod
    @functional_alias("delete_artifact")
    @clisync.include(wait_response=True)
    def delete(
        id: str,
        wait_response: bool = False,
    ):
        """
        Delete an artifact.

        Args:
            id (str): ID of the artifact.
            wait_response (bool): Set to true to delete sync. If False, the deletion is made in background. Default: False.
        """
        return Client.delete(f"/app/artifacts/{id}", wait_response=wait_response)

    @staticmethod
    @functional_alias("get_artifact")
    @clisync.include()
    def retrieve(id: str, fields: Optional[List[str]] = None):
        """
        Retrieve an artifact.

        Args:
            id (str): ID of the artifact.
        """
        return Client.get(f"/app/artifacts/{id}", wait_response=True, params={"fields": fields})

    @staticmethod
    @functional_alias("download_artifact")
    @clisync.include()
    def download(
        id: str,
        path: str = "./",
    ):
        """
        Download an artifact from a run.

        Args:
            id (str): Id of the artifact.
            path (str): Path to save the file. Default: './'.
        """
        path = path or "./"

        def composition_sync(**kwargs):
            fields = ["download_url", "num_bytes", "name"]
            artifact = Client.get(f"/app/artifacts/{id}", wait_response=True, params={"fields": fields})
            if not artifact:
                return
            os.makedirs(path, exist_ok=True)
            Client.download_sync(
                url=artifact["download_url"],
                local_path=os.path.join(path, artifact["name"]),
                num_bytes=artifact["num_bytes"],
                **kwargs,
            )

        async def composition_async(**kwargs):
            fields = ["download_url", "num_bytes", "name"]
            artifact = Client.get(f"/app/artifacts/{id}", wait_response=True, params={"fields": fields})
            if not artifact:
                return
            os.makedirs(path, exist_ok=True)
            await Client.download_async(
                url=artifact["download_url"],
                local_path=os.path.join(path, artifact["name"]),
                num_bytes=artifact["num_bytes"],
                **kwargs,
            )

        if is_running_event_loop():
            Client.execute(composition_sync, wait_response=True, is_async_method=False, with_progress=True)
        else:
            Client.execute(composition_async, wait_response=True, is_async_method=True, with_progress=True)
        return path

    @staticmethod
    @functional_alias("list_artifacts")
    @clisync.include()
    def list(
        run_id: str,
        project: Optional[str] = None,
        fields: Optional[List[str]] = None,
        group_by_step: Optional[bool] = True,
        page: Optional[int] = 1,
        limit: Optional[int] = 50,
        order_by: Optional[str] = "name",
        order_direction: Optional[str] = "asc",
    ):
        """
        List the artifacts of a run.

        Args:
            run_id (str): ID of the run.
            project (str): ID of the project.
            fields (List[str], optional): List of fields to retrieve. Default: None.
            group_by_step (bool, optional): Set to True to group the artifacts by step. Default: True.
            page (int, optional): Page number. Default: 1.
            limit (int, optional): Number of artifacts to retrieve per page. Default: 50.
            order_by (str, optional): Field to order by. Default: "name".
            order_direction (str, optional): Order direction. Default: "asc".
        """
        project = Project.get(project)
        if not project:
            return

        return Client.get(
            "/app/artifacts",
            wait_response=True,
            params={
                "run": run_id,
                "project": project,
                "fields": fields,
                "keep_latest_step": True if group_by_step else False,
                "page": page,
                "limit": limit,
                "order_by": order_by,
                "order_direction": order_direction,
            },
        )
