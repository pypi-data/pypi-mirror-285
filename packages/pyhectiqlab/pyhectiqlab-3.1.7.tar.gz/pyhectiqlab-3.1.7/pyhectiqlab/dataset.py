import os
import clisync
import shutil

from typing import Optional, List, Union

from pyhectiqlab.tag import Tag
from pyhectiqlab.project import Project
from pyhectiqlab.client import Client
from pyhectiqlab.utils import is_running_event_loop
from pyhectiqlab.decorators import functional_alias
from pyhectiqlab.settings import getenv
from pyhectiqlab.logging import hectiqlab_logger as logger
from .utils import batched, list_all_files_in_dir, extract_host_from_source


class Dataset:
    _client: Client = Client

    @staticmethod
    @functional_alias("create_dataset")
    @clisync.include()
    def create(
        name: str,
        source: str,
        host: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        run_id: Optional[str] = None,
        project: Optional[str] = None,
        upload: Optional[bool] = True,
    ):
        """Create a dataset.

        Supported cloud storages:
        - Amazon S3
        - Google Cloud Storage

        Args:
            name (str): Name of the dataset.
            source (str): Path to the dataset. If your dataset is located in a local directory, the source should be the directory path (e.g., "/path/to/dataset"). If
                the dataset is located in a cloud storage, the source should be the URL of the dataset (e.g., "s3://bucket/dataset").
            host (str, optional): Host of the dataset. Default: None. If the dataset is located in a local directory,
                the host could be your hostname or leave it empty. If the dataset is located in a cloud storage, the host should be the cloud storage name ("s3" or "gs")
            description (str, optional): Description of the dataset. Default: None.
            version (str]): Version of the dataset. If None, the created dataset version increments the minor of the latter version if it exists, and uses 1.0 otherwise. Default: None.
            run_id (str, optional): ID of the run to attach to the dataset. If None, the dataset is not attached. Default: None.
            project (str, optional): Project of the dataset. Default: None.
            upload (bool): If True, uploads the dataset to the Lab. Default: True.

        Raises:
            logger.error: If the `name` or `source` parameters are not provided, the project is not found or the dataset creation failed, it does nothing and returns None.

        Skips dataset creation if the project is not found, or if the dataset creation failed.
        """

        if name is None:
            logger.error("The `name` parameter is required for dataset creation.")
            return

        if source is None:
            logger.error("The `source` parameter is required for dataset creation.")
            return

        from pyhectiqlab.run import Run

        project = Project.get(project)
        run_id = Run.get_id(run_id)
        if project is None:
            msg = f"Could not create dataset {name}, project not found."
            if not Dataset._client.online():
                msg = msg[:-1] + " (offline mode)."
            msg += " Skipping dataset creation."
            logger.error(msg)
            return
        source = os.path.abspath(source)
        host = extract_host_from_source(source)

        data = {
            "name": name,
            "description": description,
            "version": version,
            "host": host,
            "source": source,
            "project": project,
            "root_run": run_id,
        }
        dataset = Dataset._client.post("/app/datasets", wait_response=True, json=data)

        if dataset is None or "id" not in dataset:
            logger.error(f"Failed to create dataset {name}.")
            return
        if upload and host not in ["s3", "gs"]:
            Dataset.upload(id=dataset["id"], source=source)

        if run_id is not None:
            Dataset.attach(name=name, version=version, run_id=run_id, project=project)
        return dataset

    @staticmethod
    @functional_alias("retrieve_dataset")
    @clisync.include()
    def retrieve(name: str, version: str, project: str, fields: Optional[List[str]] = None):
        """Retrieve a dataset

        Args:
            name (str): Name of the dataset
            project (str): Project of the dataset
            version (str): Version of the dataset
            fields (list[str], optional): Fields to retrieve. Default: None.

        Raises:
            logger.error: If the project is not found, it does nothing and returns None.
        """
        project = Project.get(project)
        if project is None:
            msg = f"Could not retrieve the dataset {name}-{version}, project not found."
            if not Dataset._client.online():
                msg = msg[:-1] + " (offline mode)."
            msg += " Skipping dataset retrieval."
            logger.error(msg)
            return
        body = Dataset._client.get(
            "/app/datasets/retrieve",
            params={
                "name": name,
                "project": project,
                "version": version,
                "fields": fields or [],
            },
            wait_response=True,
        )
        return body

    @staticmethod
    @functional_alias("dataset_exists")
    @clisync.include()
    def exists(name: str, version: str, project: Optional[str] = None):
        """Check if a dataset exists

        Args:
            name (str): Name of the dataset
            project (str): Project of the dataset
            version (str): Version of the dataset
        """
        return Dataset.retrieve(name=name, project=project, version=version, fields=["id"]) is not None

    @staticmethod
    @functional_alias("list_datasets")
    @clisync.include()
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
    ):
        """List the datasets

        Args:
            project (str, optional): Project of the dataset.
            search (str, optional): Search string.
            author (str, optional): Author of the dataset.
            keep_latest_version (bool, optional): If True, group by the latest version of dataset name and return only the latest version of each dataset name.
            fields (list[str], optional): Fields to retrieve.
            page (int, optional): Page number.
            limit (int, optional): Limit of the datasets.
            order_by (str, optional): Order by.
            order_direction (str, optional): Order direction.
            wait_response (bool): Wait for the response from the server. Default: False.
        """
        params = {
            "project": project,
            "search": search,
            "author": author,
            "keep_latest_version": keep_latest_version,
            "fields": fields,
            "page": page or 1,
            "limit": limit or 100,
            "order_by": order_by,
            "order_direction": order_direction,
        }

        return Dataset._client.get("/app/datasets", params=params, wait_response=True)

    @staticmethod
    @functional_alias("update_dataset")
    @clisync.include(wait_response=True)
    def update(
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        wait_response: bool = False,
    ):
        """Update a dataset, with new name, description, and/or version.

        Args:
            id (str): ID of the dataset.
            name (str, optional): Name of the dataset.
            description (str, optional): Description of the dataset.
            version (str, optional): Version of the dataset.
            wait_response (bool): Wait for the response from the server. Default: False

        Raises:
            logging.error: If the `id` parameter is not provided, it does nothing and returns None.
        """
        if not id:
            logger.error("The `id` parameter is required.")
            return
        return Dataset._client.put(
            f"/app/datasets/{id}",
            json={"name": name, "description": description, "version": version},
            wait_response=wait_response,
        )

    @staticmethod
    @functional_alias("delete_dataset")
    @clisync.include(wait_response=True)
    def delete(
        id: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """Delete a dataset.

        Args:
            id (str): ID of the dataset.
            name (str, optional): Name of the dataset.
            version (str, optional): Version of the dataset.
            project (str, optional): Project of the dataset.
            wait_response (bool): Wait for the response from the server. Default: False

        Raises:
            logging.error: If the `id` is not provided, or if all `name`, `version`, `project` parameters are not provided, or if the dataset is not found, it does nothing and returns None.
        """
        if id is None or (name is None or version is None or project is None):
            logger.error("The `id` or `name`, `version`, `project` parameters are required.")
            return

        if not id:
            dataset = Dataset.retrieve(name=name, project=project, version=version, fields=["id"])
            if not dataset:
                logger.error(f"Could not delete dataset {name}-{version}, dataset not found. Skipping deletion.")
                return
            id = dataset["id"]
        return Dataset._client.delete(f"/app/datasets/{id}", wait_response=wait_response)

    @staticmethod
    @clisync.include()
    @functional_alias("upload_dataset")
    @clisync.include()
    def upload(id: str, source: str) -> None:
        """Upload local files to a dataset hosted in the Lab.

        Args:
            id (str): ID of the dataset.
            path (str): Path to the directory containing the files to upload.
        """
        all_files = list_all_files_in_dir(source) if os.path.isdir(source) else [source]
        batch_size = 50
        Dataset._id = dataset_id = id
        def composition_sync(**kwargs):
            for batch in batched(all_files, batch_size):
                # Create many files
                batch_body = [
                    {"name": os.path.relpath(f, start=source if os.path.isdir(source) else os.path.dirname(f)), 
                     "num_bytes": os.path.getsize(f)} for f in batch
                ]
                files = Dataset._client.post(
                    f"/app/datasets/{dataset_id}/files", wait_response=True, json={"files": batch_body}
                )["results"]

                # For each file in batch, get the policy in files (use name for finding the file)
                sorted_files = []
                for el in batch:
                    file = [
                        f.get("upload_policy")
                        for f in files
                        if f["name"]
                        == os.path.relpath(el, start=source if os.path.isdir(source) else os.path.dirname(el))
                    ][0]
                    sorted_files.append(file)
                # Upload dataset files
                Dataset._client.upload_many_sync(paths=batch, policies=sorted_files, **kwargs)

        async def composition_async(**kwargs):
            for batch in batched(all_files, batch_size):
                # Create many files
                batch_body = [
                    {"name": os.path.relpath(f, start=source if os.path.isdir(source) else os.path.dirname(f)), 
                     "num_bytes": os.path.getsize(f)} for f in batch
                ]
                files = Dataset._client.post(
                    f"/app/datasets/{dataset_id}/files", wait_response=True, json={"files": batch_body}
                )["results"]

                # For each file in batch, get the policy in files (use name for finding the file)
                sorted_files = []
                for el in batch:
                    name = os.path.relpath(el, start=source if os.path.isdir(source) else os.path.dirname(el))
                    file = [
                        f.get("upload_policy")
                        for f in files
                        if f["name"]
                        == name
                    ][0]
                    sorted_files.append(file)
                # Upload dataset files
                await Dataset._client.upload_many_async(paths=batch, policies=sorted_files, **kwargs)

        if is_running_event_loop():
            Dataset._client.execute(composition_sync, wait_response=True, is_async_method=False, with_progress=True)
        else:
            Dataset._client.execute(composition_async, wait_response=True, is_async_method=True, with_progress=True)

    @staticmethod
    @functional_alias("download_dataset")
    @clisync.include()
    def download(
        name: str,
        version: str,
        project: Optional[str] = None,
        path: Optional[str] = None,
        overwrite: bool = False,
    ):
        """Download a dataset synchronously

        Args:
            name (str): Name of the dataset.
            version (str): Version of the dataset.
            project (str, optional): Project of the dataset.
            path (str): Path to download the dataset. If None, it uses the `HECTIQLAB_DATASETS_DOWNLOAD` environment variable or the current directory.
            overwrite (bool): Overwrite the existing files. Default: False.

        Raises:
            logger.error: If the project is not found, or if the dataset is not found, it does nothing and returns None.
        """

        from pyhectiqlab import Run

        project = Project.get(project)
        if project is None:
            msg = f"Could not download dataset {name}-{version}, project not found."
            if not Dataset._client.online():
                msg = msg[:-1] + " (offline mode)."
            msg += " Skipping dataset download."
            logger.error(msg)
            return
        if not Dataset.exists(name=name, version=version, project=project):
            logger.error(
                f"Could not download dataset {name}-{version}, dataset not found. Skipping datgaset download."
            )
            return

        path = path or getenv("HECTIQLAB_DATASETS_DOWNLOAD", ".")
        path = os.path.join(path, f"{name}-{version}")
        if os.path.exists(path):
            if not overwrite:
                logger.warning(
                    f"Directory {path} already exists. Set `overwrite=True` to overwrite the files. Skipping dataset download."
                )
                return path

            shutil.rmtree(path)

        os.makedirs(path, exist_ok=True)
        run_id = Run.get_id()
        if run_id is not None:
            Dataset.attach(name=name, version=version, run_id=run_id, project=project)

        def composition_sync(**kwargs):
            dataset = Dataset.retrieve(name=name, project=project, version=version, fields=["id"])
            if not dataset:
                return
            dataset_id = dataset["id"]

            num_results = 0
            total_results = 1
            page = 1
            while not num_results == total_results:
                files = Dataset._client.get(
                    f"/app/datasets/{dataset_id}/files/",
                    params={"page": page, "limit": 50, "fields": ["download_url", "name", "num_bytes"]},
                    wait_response=True,
                )
                total_results = files["total_results"]

                Dataset._client.download_many_sync(
                    urls=[file["download_url"] for file in files["results"]],
                    local_paths=[os.path.join(path, file["name"]) for file in files["results"]],
                    num_bytes=[file["num_bytes"] for file in files["results"]],
                    **kwargs,
                )
                num_results += len(files["results"])
                page += 1

            return Dataset._client.post(f"/app/datasets/{dataset_id}/on-download-completed", wait_response=False)

        async def composition_async(**kwargs):
            dataset = Dataset.retrieve(name=name, project=project, version=version, fields=["id"])
            if not dataset:
                return
            dataset_id = dataset["id"]

            num_results = 0
            total_results = 1
            page = 1
            while not num_results == total_results:
                files = Dataset._client.get(
                    f"/app/datasets/{dataset_id}/files/",
                    params={"page": page, "limit": 50, "fields": ["download_url", "name", "num_bytes"]},
                    wait_response=True,
                )
                total_results = files["total_results"]

                await Dataset._client.download_many_async(
                    urls=[file["download_url"] for file in files["results"]],
                    local_paths=[os.path.join(path, file["name"]) for file in files["results"]],
                    num_bytes=[file["num_bytes"] for file in files["results"]],
                    **kwargs,
                )
                num_results += len(files["results"])
                page += 1

            return Dataset._client.post(f"/app/datasets/{dataset_id}/on-download-completed", wait_response=False)

        logger.info(f"⏳ Downloading dataset {name}-{version} to {path}...")
        if is_running_event_loop():
            Dataset._client.execute(composition_sync, wait_response=True, is_async_method=False, with_progress=True)
        else:
            Dataset._client.execute(composition_async, wait_response=True, is_async_method=True, with_progress=True)
        logger.info(f"✅ Done.")
        return path

    @staticmethod
    @clisync.include()
    def attach(
        name: str,
        version: str,
        run_id: str,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """Attach a dataset to a run

        Args:
            name (str): Name of the dataset.
            version (str): Version of the dataset.
            run_id (str): ID of the run.
            project (str, optional): Project of the dataset.
            wait_response (bool): Wait for the response from the server. Default: False.

        Raises:
            logger.error:  If the `run_id` parameter is not provided or the dataset is not found, it does nothing and returns None.
        """
        if run_id is None:
            logger.error("The `run_id` parameter is required.")
            return
        dataset = Dataset.retrieve(name=name, project=project, version=version, fields=["id"])
        if dataset is None:
            logger.error(
                f"Could not attach run {run_id}, dataset {name}-{version} not found. Skipping attachment to run."
            )
            return
        return Dataset._client.post(
            f"/app/datasets/{dataset['id']}/attach-to-run/{run_id}", wait_response=wait_response
        )

    @staticmethod
    @clisync.include()
    def detach(
        name: str,
        version: str,
        run_id: str,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """Detach a dataset from a run

        Args:
            name (str): Name of the dataset.
            version (str): Version of the dataset.
            run_id (str): ID of the run.
            project (str, optional): Project of the dataset.
            wait_response (bool, optional): Wait for the response from the server. Default: False.

        Raises:
            ValueError: If the `run_id` parameter is not provided.


        Raises:
            logger.error:  If the `run_id` parameter is not provided or the dataset is not found, it does nothing and returns None.
        """
        if run_id is None:
            logger.error("The `run_id` parameter is required.")
            return
        dataset = Dataset.retrieve(name=name, project=project, version=version, fields=["id"])
        if not dataset:
            logger.error(
                f"Could not detach run {run_id}, dataset {name}-{version} not found. Skipping detachment from run."
            )
            return
        dataset_id = dataset["id"]
        return Dataset._client.post(
            f"/app/datasets/{dataset_id}/detach-from-run/{run_id}", wait_response=wait_response
        )

    @staticmethod
    @functional_alias("add_tags_to_dataset")
    @clisync.include()
    def add_tags(
        tags: Union[str, List[str]],
        name: str,
        version: str,
        project: Optional[str] = None,
        wait_response: Optional[bool] = False,
    ):
        """Add tags to a dataset

        Args:
            tags (Union[str, List[str]]): Tags to add.
            name (str): Name of the dataset.
            version (str): Version of the dataset.
            project (str, optional): Project name. Default: None.
            wait_response (bool, optional): Wait for the response from the server. Default: False.

        Raises:
            logger.error:  If the dataset is not found, it does nothing and returns None.
        """
        project = Project.get(project)
        dataset = Dataset.retrieve(name=name, project=project, version=version, fields=["id"])
        if not dataset:
            logger.error(
                f"Could not attach tags {tags}, dataset {name}-{version} not found. Skipping attachment of tags."
            )
            return
        dataset_id = dataset["id"]
        return Tag.attach_to_dataset(tags=tags, dataset_id=dataset_id, project=project, wait_response=wait_response)

    @staticmethod
    @functional_alias("detach_tag_from_dataset")
    @clisync.include()
    def detach_tag(
        tag: str,
        name: str,
        version: str,
        project: Optional[str] = None,
        wait_response: Optional[bool] = False,
    ):
        """Remove a tag from the run.
        For functional alias, use `detach_tag_from_run`.

        Args:
            title (str): The new title of the run.
            name (str): Name of the dataset.
            version (str): Version of the dataset.
            project (str, optional): Project name. Default: None.

        Raises:
            logger.error:  If the dataset is not found, it does nothing and returns None.
        """
        project = Project.get(project)
        dataset = Dataset.retrieve(name=name, version=version, project=project, fields=["id"])
        if not dataset:
            logger.error(
                f"Could not detach tag {tag}, dataset {name}-{version} not found. Skipping detachment of tag."
            )
            return
        dataset_id = dataset["id"]
        Tag.detach_from_dataset(tag=tag, dataset_id=dataset_id, project=project, wait_response=wait_response)
