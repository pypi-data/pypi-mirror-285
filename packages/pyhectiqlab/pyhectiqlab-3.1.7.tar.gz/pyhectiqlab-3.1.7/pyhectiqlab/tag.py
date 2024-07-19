import clisync

from typing import Optional, List

from pyhectiqlab.client import Client
from pyhectiqlab.decorators import functional_alias


class Tag:

    @staticmethod
    @functional_alias("create_tag")
    @clisync.include()
    def create(
        name: str,
        project: str,
        color: Optional[str] = None,
        wait_response: bool = False,
    ):
        """Create a new tag.

        Args:
            name (str): Name of the tag.
            project (str): Project name.
            color (str, optional): Color of the tag. Default: None.
            wait_response (bool): Set to true to create sync. If False, the creation is made in background. Default: False.
        """
        json = {"name": name, "color": color, "project": project}
        return Client.post("/app/tags", wait_response=wait_response, json=json)

    @staticmethod
    @clisync.include()
    def attach_to_run(
        tags: List[str],
        run_id: str,
        project: str,
        wait_response: bool = False,
    ):
        """Attach tags to a run.

        Args:
            tags (List[str]): List of tags to attach.
            run_id (str): Run ID.
            project (str): Project name. Default: None.
            wait_response (bool): Set to true to attach sync. If False, the attachment is made in background. Default: False.
        """
        json = {"run": run_id, "tags": tags, "project": project}
        return Client.post("/app/tags/attach-to-run", wait_response=wait_response, json=json)

    @staticmethod
    @clisync.include()
    def detach_from_run(
        tag: str,
        run_id: str,
        project: str,
        wait_response: bool = False,
    ):
        """Detach a tag from a run.

        Args:
            tag (str): Tag name.
            run_id (str): Run ID.
            project (str, optional): Project name. Default: None.
            wait_response (bool): Set to true to detach sync. If False, the detachment is made in background. Default: False.
        """
        return Client.post(
            f"/app/tags/detach-from-run",
            wait_response=wait_response,
            json={"run": run_id, "tag": tag, "project": project},
        )

    @staticmethod
    @clisync.include()
    def attach_to_model(
        tags: List[str],
        model_id: str,
        project: str,
        wait_response: bool = False,
    ):
        """Attach a tag to a model.

        Args:
            tag (str): Tag name.
            model_id (str): Model ID.
            project (str, optional): Project name. Default: None.
            wait_response (bool): Set to true to attach sync. If False, the attachment is made in background. Default: False.
        """
        body = {"model": model_id, "tags": tags, "project": project}
        return Client.post("/app/tags/attach-to-model", json=body, wait_response=wait_response)

    @staticmethod
    @functional_alias("detach_tag_from_model")
    @clisync.include()
    def detach_from_model(
        tag: str,
        model_id: str,
        project: str,
        wait_response: bool = False,
    ):
        """Detach a tag from a model.

        Args:
            tag (str): Tag name.
            model_id (str): Model ID.
            project (str): Project name. Default: None.
            wait_response (bool): Set to true to detach sync. If False, the detachment is made in background. Default: False.
        """
        return Client.post(
            f"/app/tags/detach-from-model",
            wait_response=wait_response,
            json={"model": model_id, "tag": tag, "project": project},
        )

    @staticmethod
    @clisync.include()
    def attach_to_dataset(
        tags: List[str],
        dataset_id: str,
        project: str,
        wait_response: bool = False,
    ):
        """Attach a tag to a dataset.

        Args:
            tags (list[str]): List of tag names.
            dataset_id (str): Dataset ID.
            project (str): Project name.
            wait_response (bool): Set to true to attach sync. If False, the attachment is made in background. Default: False.
        """
        return Client.post(
            f"/app/tags/attach-to-dataset",
            wait_response=wait_response,
            json={"dataset": dataset_id, "tags": tags, "project": project},
        )

    @staticmethod
    @functional_alias("detach_tag_from_dataset")
    @clisync.include()
    def detach_from_dataset(
        tag: str,
        dataset_id: str,
        project: str,
        wait_response: bool = False,
    ):
        """Detach a tag from a dataset.

        Args:
            dataset_id (str): Dataset ID.
            tag (str): Tag name.
            project (str): Project name.
            wait_response (bool): Set to true to detach sync. If False, the detachment is made in background. Default: False.
        """
        return Client.post(
            f"/app/tags/detach-from-dataset",
            wait_response=wait_response,
            json={"dataset": dataset_id, "tag": tag, "project": project},
        )

    @staticmethod
    @functional_alias("list_tags")
    @clisync.include()
    def list(
        project: Optional[str] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 100,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
    ):
        """Get tags.

        Args:
            project (str, optional): Project name. Default: None.
            page (int, optional): Page number. Default: 1.
            limit (int, optional): Number of tags per page. Default: 100.
            order_by (str, optional): Order by field. Default: None.
            order_direction (str, optional): Order direction. Default: None.
        """
        if not project:
            return
        return Client.get(
            "/app/tags",
            wait_response=True,
            params={
                "project": project,
                "page": page,
                "limit": limit,
                "order_by": order_by,
                "order_direction": order_direction,
            },
        )
