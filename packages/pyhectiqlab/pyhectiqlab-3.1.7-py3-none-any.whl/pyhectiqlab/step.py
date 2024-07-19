import clisync

from typing import Optional, List, Union
from functools import partial

from pyhectiqlab.client import Client
from pyhectiqlab.decorators import functional_alias, classproperty
from pyhectiqlab.logging import stream_log, get_handler

import logging

logger = logging.getLogger()


class Step:
    _id: Optional[str] = None
    _is_listening_logs: bool = False
    _client: Client = Client

    @classproperty
    def id(cls):
        return cls._id

    def __init__(
        self,
        name: Optional[str] = "Untitled step",
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
        status: Optional[str] = None,
        run_id: Optional[str] = None,
    ):
        self.start(name=name, description=description, metadata=metadata, status=status, run_id=run_id)

    @staticmethod
    @functional_alias("start_step")
    def start(
        name: Optional[str] = "Untitled step",
        run_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
        status: Optional[str] = None,
    ) -> int:
        """
        Start a new step.

        Args:
            title (str): Title of the step.

        Raises:
            logger.error: If no run ID is found, it does not create the step and returns None.
        """
        from pyhectiqlab.run import Run

        run_id = Run.get_id(run_id)
        if run_id is None:
            logger.error("No active run found. Skipping step creation.")
            return

        if Step.id is not None:
            Step.end()

        json = {
            "name": name,
            "description": description,
            "metadata": metadata,
            "status": status,
            "run": run_id,
        }
        step = Step._client.post("/app/steps", wait_response=True, json=json)
        Step.id = step["id"]

        if Step._is_listening_logs:
            # Stop the previous listener
            handler = get_handler()
            if handler is not None:
                handler.close()
            Step._is_listening_logs = False

        # Start listening to the logs
        stream_log(on_dump=partial(Step._handle_log_dump, step=Step.id))
        Step._is_listening_logs = True
        return step

    @staticmethod
    @functional_alias("end_step")
    def end(status: Optional[str] = None, step: Optional[str] = None):
        """
        End the current step.

        Args:
            step (str, optional): Step name. If None, the current step is used. Default: None.

        Raises:
            logger.error: If no step ID is found, it does nothing and returns None.
        """
        step = step or Step.id
        if step is None:
            if Step._client.online():
                logger.error("No active step found. Skipping step end.")
            return

        status = status or "completed"
        handler = get_handler()
        logs = handler.value() if handler is not None else None
        if logs is not None and len(logs) > 0:
            if isinstance(logs, list):
                logs = "\n".join(logs)

        Step._client.post(f"/app/steps/{step}/end", wait_response=True, json={"status": status, "logs": logs})
        Step._id = None
        if handler:
            handler.close(flush=False)
            Step._is_listening_logs = False
        return

    @staticmethod
    @functional_alias("update_step")
    @clisync.include()
    def update(
        name: Optional[str] = None,
        description: Optional[str] = None,
        logs: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[dict] = None,
        step: Optional[str] = None,
    ):
        """
        Update the logs of the current step.

        Args:
            name (str, optional): Name of the step. If None, the current step is used. Default: None.
            description (str, optional): Description of the step. Default: None.
            logs (Union[str, List[str]]): Logs to update.
            status (str, optional): Status of the step. Default: None.
            metadata (dict, optional): Metadata to update. Default: None.
            step (str, optional): Step name. If None, the current step is used. Default: None.

        Raises:
            logger.error: If no active step is found, it does nothing and returns None.
        """
        step = step or Step.id
        if step is None:
            logger.error("No active step found. Skipping step update.")
            return
        body = {"name": name, "description": description, "logs": logs, "status": status, "metadata": metadata}
        body = {k: v for k, v in body.items() if v is not None}
        if len(body) == 0:
            return
        Client.put(f"/app/steps/{step}", wait_response=True, json=body)

    @staticmethod
    def _handle_log_dump(logs: Union[str, List[str]], step: Optional[str] = None):
        # Format the logs
        if len(logs) == 0:
            return
        if isinstance(logs, list):
            logs = "\n".join(logs)
        Step.update(logs=logs, step=step)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.end(status="failed")
        else:
            self.end(status="completed")
