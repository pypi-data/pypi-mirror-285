import os
import clisync
import shutil

from typing import Optional, List, Union

from pyhectiqlab.tag import Tag
from pyhectiqlab.project import Project
from pyhectiqlab.client import Client
from pyhectiqlab.decorators import functional_alias
from pyhectiqlab.utils import batched, list_all_files_in_dir, is_running_event_loop
from pyhectiqlab.logging import hectiqlab_logger as logger
from pyhectiqlab.settings import getenv


class Model:
    _client: Client = Client

    @staticmethod
    @functional_alias("create_model")
    @clisync.include()
    def create(
        name: str,
        path: Optional[str] = None,
        version: Optional[str] = None,
        run_id: Optional[str] = None,
        project: Optional[str] = None,
        description: Optional[str] = None,
        upload: bool = True,
    ):
        """Create a model

        Args:
            name (str): Name of the model
            path (str): Path to the model directory. If None, the model is created without files. Default: None.
            run_id (str, optional):  ID of the run
            project (str, optional): Project of the model
            version (str, optional): Version of the model
            description (str, optional): Description of the model
            upload (bool, optional): Upload the model files. Default: True

        Raises:
            logging.error: If the `name` parameter is not provided, the project is not found or the model creation fails, it does nothing and returns None.
        """
        from pyhectiqlab.run import Run

        if name is None:
            logger.error("The `name` parameter is required.")
            return

        project = Project.get(project)
        run_id = Run.get_id(run_id)

        if project is None:
            msg = f"Could not create the model {name}, project not found."
            if not Model._client.online():
                msg = msg[:-1] + " (offline mode)."
            logger.error(msg)
            return

        json = {
            "name": name,
            "description": description,
            "version": version,
            "project": project,
            "root_run": run_id,
        }

        model = Model._client.post("/app/models", wait_response=True, json=json)
        if model is None or "id" not in model:
            logger.error(f"Failed to create model {name}.")
            return

        if upload and path:
            Model.upload(id=model["id"], path=path)

        if run_id is not None:
            Model.attach(name=name, version=version, run_id=run_id, project=project, wait_response=True)
        return model

    @staticmethod
    @functional_alias("retrieve_model")
    @clisync.include()
    def retrieve(
        name: str,
        version: str,
        project: Optional[str] = None,
        fields: Optional[List[str]] = [],
    ):
        """Retrieve a model

        Args:
            name (str): Name of the model
            version (str): Version of the model
            project (str, optional): Project of the model. If None, the project of the current run is used. Default: None.
            fields (dict, optional): Fields to retrieve
            wait_response (bool, optional): Wait for the response from the server

        Raises:
            logging.error: If the project is not found, it does nothing and returns None.
        """
        project = Project.get(project)
        if project is None:
            msg = "Could not retrieve the model, project not found."
            if not Model._client.online():
                msg = msg[:-1] + " (offline mode)."
            msg += " Skipping model retrieval."
            logger.error(msg)
            return

        return Model._client.get(
            "/app/models/retrieve",
            params={
                "name": name,
                "project": project,
                "version": version,
                "fields": fields,
            },
            wait_response=True,
        )

    @staticmethod
    @functional_alias("model_exists")
    @clisync.include()
    def exists(name: str, version: str, project: Optional[str] = None):
        """Check if a model exists

        Args:
            name (str): Name of the model.
            version (str): Version of the model.
            project (str): Project of the model.
        """
        return Model.retrieve(name=name, project=project, version=version, fields=["id"]) is not None

    @staticmethod
    @functional_alias("list_models")
    @clisync.include(wait_response=True)
    def list(
        project: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None,
        keep_latest_version: bool = False,
        fields: Optional[List[str]] = [],
        page: Optional[int] = 1,
        limit: Optional[int] = 100,
        order_by: Optional[str] = "created_at",
        order_direction: Optional[str] = "desc",
        wait_response: bool = False,
    ):
        """List the models

        Args:
            project (str): Project of the model
            search (str, optional): Search string
            author (str, optional): Author of the model
            keep_latest_version (bool, optional): If True, group by the latest version of model name and return only the latest version of each model name
            fields (List[str], optional): Fields to retrieve
            page (int, optional): Page number
            limit (int, optional): Limit of the models
            order_by (str, optional): Order by
            order_direction (str, optional): Order direction
            wait_response (bool, optional): Wait for the response from the server
        """

        params = {
            "project": Project.get(project),
            "search": search,
            "author": author,
            "keep_latest_version": keep_latest_version,
            "fields": fields,
            "page": page or 1,
            "limit": limit or 100,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        return Model._client.get("/app/models", params=params, wait_response=wait_response)

    @staticmethod
    @functional_alias("update_model")
    @clisync.include(wait_response=True)
    def update(
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        wait_response: bool = False,
    ):
        """Update a model

        Args:
            id (str): ID of the model
            name (str, optional): Name of the model
            description (str, optional): Description of the model
            version (str, optional): Version of the model
            wait_response (bool, optional): Wait for the response from the server

        Raises:
            If the `id` parameter is not provided, it does nothing and returns None.
        """
        if not id:
            logger.error("The `id` parameter is required.")
            return

        return Model._client.put(
            f"/app/models/{id}",
            json={"name": name, "description": description, "version": version},
            wait_response=wait_response,
        )

    @staticmethod
    @functional_alias("delete_model")
    @clisync.include(wait_response=True)
    def delete(
        id: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """Delete a model

        Args:
            id (str): ID of the model
            name (str, optional): Name of the model
            version (str, optional): Version of the model
            project (str, optional): Project of the model
            wait_response (bool, optional): Wait for the response from the server

        Raises:
            logger.error: If the `id` parameter is not provided, or all of `name`, `version`, and `project` are not provided, it does nothing and returns None.
        """
        project = Project.get(project)
        if id is None and (name is None or version is None or project is None):
            raise ValueError("Either `id` or `name`, `version` and `project` are required.")
        if id is None:
            model = Model.retrieve(name=name, project=project, version=version, fields=["id"])
            if model is None:
                logger.error(f"Could not delete model {name}-{version}, model not found. Skipping model deletion.")
                return
            id = model["id"]
        return Model._client.delete(f"/app/models/{id}", wait_response=wait_response)

    @staticmethod
    @clisync.include()
    @functional_alias("upload_model")
    @clisync.include()
    def upload(id: str, path: str) -> None:
        """Upload local files to a model hosted in the Lab.

        Args:
            id (str): ID of the model.
            path (str): Path to the file or directory containing the files to upload.
        """
        all_files = list_all_files_in_dir(path) if os.path.isdir(path) else [path]
        batch_size = 50
        Model._id = model_id = id

        def composition_sync(**kwargs):
            for batch in batched(all_files, batch_size):
                # Create many files
                batch_body = [{"name": os.path.relpath(f, start=path if os.path.isdir(path) else os.path.dirname(f)), 
                               "num_bytes": os.path.getsize(f)} for f in batch]
                files = Model._client.post(
                    f"/app/models/{model_id}/files", wait_response=True, json={"files": batch_body}
                )["results"]

                # For each file in batch, get the policy in files (use name for finding the file)
                sorted_files = []
                for el in batch:
                    name = os.path.relpath(el, start=path if os.path.isdir(path) else os.path.dirname(el))
                    file = [
                        f.get("upload_policy")
                        for f in files
                        if f["name"]
                        == name
                    ][0]
                    sorted_files.append(file)
                # Upload dataset files
                Model._client.upload_many_sync(paths=batch, policies=sorted_files, **kwargs)

        async def composition_async(**kwargs):
            for batch in batched(all_files, batch_size):
                # Create many files
                batch_body = [{"name": os.path.relpath(f, start=path if os.path.isdir(path) else os.path.dirname(f)), 
                               "num_bytes": os.path.getsize(f)} for f in batch]
                files = Model._client.post(
                    f"/app/models/{model_id}/files", wait_response=True, json={"files": batch_body}
                )["results"]

                # For each file in batch, get the policy in files (use name for finding the file)
                sorted_files = []
                for el in batch:
                    name = os.path.relpath(el, start=path if os.path.isdir(path) else os.path.dirname(el))
                    file = [f.get("upload_policy") for f in files if f["name"] == name][0]
                    sorted_files.append(file)
                # Upload dataset files
                await Model._client.upload_many_async(paths=batch, policies=sorted_files, **kwargs)

        if is_running_event_loop():
            Model._client.execute(composition_sync, wait_response=True, is_async_method=False, with_progress=True)
        else:
            Model._client.execute(composition_async, wait_response=True, is_async_method=True, with_progress=True)

    @staticmethod
    @functional_alias("download_model")
    @clisync.include()
    def download(
        name: str,
        version: str,
        project: Optional[str] = None,
        path: Optional[str] = None,
        overwrite: bool = False,
    ):
        """Download a model

        Args:
            name (str): Name of the model
            project (str): Project of the model
            version (str): Version of the model
            path (str, optional): Path to download the model
            overwrite (bool, optional): Overwrite the files if they already exist

        Raises:
            logging.error: If the project is not found or the model does not exist, it does nothing and returns None.
        """
        project = Project.get(project)
        if project is None:
            msg = "Could not download the model, project not found."
            if not Model._client.online():
                msg = msg[:-1] + "(offline mode)."
            logger.error(msg)
            return
        if not Model.exists(name=name, version=version, project=project):
            logger.error(
                f"Could not download the model, model {name}-{version} does not exist. Skipping model download."
            )
            return
        path = path or getenv("HECTIQLAB_MODELS_DOWNLOAD") or "./"
        path = os.path.join(path, f"{name}-{version}")
        if os.path.exists(path):
            if not overwrite:
                logger.warning(
                    f"Directory {path} already exists. Set `overwrite=True` to overwrite the files. Skipping model download."
                )
                return path

            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)
        from pyhectiqlab import Run

        project = Project.get(project)

        def composition_sync(**kwargs):
            model = Model.retrieve(name=name, project=project, version=version, fields=["id"])
            if not model:
                return
            model_id = model["id"]

            if Run.id is not None:
                Model._client.post(f"/app/models/{model_id}/attach-to-run/{Run.id}", wait_response=False)

            num_results = 0
            total_results = 1
            page = 1
            while not num_results == total_results:
                files = Model._client.get(
                    f"/app/models/{model_id}/files/",
                    params={"page": page, "limit": 50, "fields": ["download_url", "name", "num_bytes"]},
                    wait_response=True,
                )
                total_results = files["total_results"]

                Model._client.download_many_sync(
                    urls=[file["download_url"] for file in files["results"]],
                    local_paths=[os.path.join(path, file["name"]) for file in files["results"]],
                    num_bytes=[file["num_bytes"] for file in files["results"]],
                    **kwargs,
                )
                num_results += len(files["results"])
                page += 1

            Model._client.post(f"/app/models/{model_id}/on-download-completed", wait_response=False)

        async def composition_async(**kwargs):
            model = Model.retrieve(name=name, project=project, version=version, fields=["id"])
            if not model:
                return
            model_id = model["id"]

            if Run.id is not None:
                Model._client.post(f"/app/models/{model_id}/attach-to-run/{Run.id}", wait_response=False)

            num_results = 0
            total_results = 1
            page = 1
            while not num_results == total_results:
                files = Model._client.get(
                    f"/app/models/{model_id}/files/",
                    params={"page": page, "limit": 50, "fields": ["download_url", "name", "num_bytes"]},
                    wait_response=True,
                )
                total_results = files["total_results"]

                await Model._client.download_many_async(
                    urls=[file["download_url"] for file in files["results"]],
                    local_paths=[os.path.join(path, file["name"]) for file in files["results"]],
                    num_bytes=[file["num_bytes"] for file in files["results"]],
                    **kwargs,
                )
                num_results += len(files["results"])
                page += 1

            Model._client.post(f"/app/models/{model_id}/on-download-completed", wait_response=False)

        logger.info(f"⏳ Downloading model {name}-{version} to {path}...")
        if is_running_event_loop():
            Model._client.execute(composition_sync, wait_response=True, is_async_method=False, with_progress=True)
        else:
            Model._client.execute(composition_async, wait_response=True, is_async_method=True, with_progress=True)

        logger.info("✅ Done.")
        return path

    @staticmethod
    def attach(
        name: str,
        version: str,
        run_id: str,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """Attach a model to a run

        Args:
            run_id (str): ID of the run.
            name (str): Name of the model.
            version (str): Version of the model.
            project (str, optional): Project of the model. If None, the project of the current run is used. Default: None.
            wait_response (bool, optional): Wait for the response from the server. Default: False.

        Raises:
            logging.error: If the `run_id` parameter is not provided, or if the model does not exist, it does nothing and returns None.

        """

        if run_id is None:
            logger.error("The `run_id` parameter is required.")
            return
        project = Project.get(project)
        model = Model.retrieve(name=name, project=project, version=version, fields=["id"])
        if not model:
            logger.error(
                f"Could not attach run {run_id}, model {name}-{version} not found. Skipping attachment to run."
            )
            return
        model_id = model["id"]
        return Model._client.post(f"/app/models/{model_id}/attach-to-run/{run_id}", wait_response=wait_response)

    @staticmethod
    def detach(
        name: str,
        version: str,
        run_id: str,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """Detach a model from a run

        Args:
            name (str): Name of the model.
            version (str): Version of the model.
            run_id (int): ID of the run.
            project (str, optional): Project of the model. If None, the project of the current run is used. Default: None.
            wait_response (bool, optional): Wait for the response from the server. Default: False.

        Raises:
            logging.error: If the model is not found, it does nothing and returns None.
        """
        project = Project.get(project)
        model = Model.retrieve(name=name, project=project, version=version, fields=["id"])
        if not model:
            logger.error(
                f"Could not detach run {run_id}, model {name}-{version} not found. Skipping detachment from run."
            )
            return
        model_id = model["id"]
        return Model._client.post(f"/app/models/{model_id}/detach-from-run/{run_id}", wait_response=wait_response)

    @staticmethod
    @functional_alias("add_tags_to_model")
    @clisync.include()
    def add_tags(
        tags: Union[str, List[str]],
        name: str,
        version: str,
        project: Optional[str] = None,
    ):
        """Add tags to a model

        Args:
            tags (Union[str, List[str]]): Tags to add.
            name (str): Name of the model.
            version (str): Version of the model.
            project (str): Project of the model. If None, the project of the current run is used. Default: None.

        Raises:
            logging.error: If the model is not found, it does nothing and returns None.
        """
        project = Project.get(project)
        model = Model.retrieve(name=name, project=project, version=version, fields=["id"])
        if not model:
            logger.error(
                f"Could not attach tags {tags}, model {name}-{version} not found. Skipping attachment of tags."
            )
            return
        model_id = model["id"]
        return Tag.attach_to_model(tags=tags, model_id=model_id, project=project)

    @staticmethod
    @functional_alias("detach_tag_from_model")
    @clisync.include()
    def detach_tag(
        tag: str,
        name: str,
        version: str,
        project: Optional[str] = None,
    ):
        """Remove a tag from the model.

        Args:
            title (str): The new title of the run.
            name (str): Name of the model.
            version (str): Version of the model.
            project (str): Project of the model. If None, the project of the current run is used. Default: None.

        Raises:
            logging.error: If the model is not found, it does nothing and returns
        """
        project = Project.get(project)
        model = Model.retrieve(name=name, version=version, project=project, fields=["id"])
        if not model:
            logger.error(f"Could not detach tag {tag}, model {name}-{version} not found. Skipping detachment of tag.")
            return
        model_id = model["id"]
        Tag.detach_from_model(tag=tag, model_id=model_id, project=project)
