import os
import socket
import asyncio
import logging
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, FileSizeColumn, TimeRemainingColumn
from typing import List, Optional

from pyhectiqlab.settings import getenv
from pyhectiqlab.decorators import classproperty

logger = logging.getLogger()


def is_running_event_loop() -> bool:
    """Check if an event loop is running."""
    try:
        return asyncio.get_event_loop().is_running()
    except RuntimeError:
        return False


def batched(iterable, n):
    """Yield successive n-sized batches from iterable."""
    for i in range(0, len(iterable), n):
        i1 = min(i + n, len(iterable))
        yield iterable[i:i1]


def list_all_files_in_dir(local_folder: str) -> List[str]:
    """List all files in a directory.
    If the path is a file, the file is returned.

    Args:
        local_folder (str): The folder to list files from.
    """
    if not os.path.exists(local_folder):
        raise FileNotFoundError(f"Directory {local_folder} does not exist.")
    filenames = []
    if not os.path.isdir(local_folder):
        # If the path is a file, return the file
        return [local_folder]

    for el in os.walk(local_folder):
        for f in os.listdir(el[0]):
            complete_path = os.path.join(el[0], f)
            if not os.path.isdir(complete_path):
                if os.path.isfile(complete_path):
                    filenames.append(complete_path)
    return filenames


def extract_host_from_source(source: str) -> str:
    """Extract the resource from a path.

    If the path is a cloud path (e.g., s3://bucket/dataset), the resource is inferred from the path.
    If the path is a local path, the resource is set to "local" if not provided.

    Args:
        path (str): The path to extract the resource from.
        default_resource (str): The resource to compare the path with.
    """
    if source.startswith("s3://"):
        return "s3"
    elif source.startswith("gs://"):
        return "gs"
    else:
        return socket.gethostname()


async def queue_gather(tasks: List[callable], workers: Optional[int] = 10):
    """Gather tasks using a queue and workers.
    The tasks will be placed in a queue and workers will be
    created to process the tasks.
    The workers will be stopped when the queue is empty.

    Example usage:

    ```python
    async def task():
        await asyncio.sleep(1)
        return "done"
    tasks = [task() for _ in range(10)]
    results = await queue_gather(tasks)
    print(results)
    ```

    Args:
        tasks (List[callable]): A list of async methods
        workers (Optional[int], optional): The number of workers. Defaults to 10.
    """

    async def worker(i: int, queue: asyncio.Queue):
        """Worker to process tasks from a queue."""
        results = []
        while not queue.empty():
            logger.debug(f"Worker {i}. Queue size: {queue.qsize()}")
            idx, task = await queue.get()
            try:
                result = await task
                results.append((idx, result))
            except Exception as e:
                print(e)
                results.append((idx, None))
            finally:
                queue.task_done()
        return results

    queue = asyncio.Queue()
    [queue.put_nowait((i, task)) for i, task in enumerate(tasks)]
    # Create workers
    workers = [asyncio.create_task(worker(idx, queue)) for idx in range(workers)]
    await queue.join()
    for worker in workers:
        worker.cancel()
    results = await asyncio.gather(*workers, return_exceptions=True)
    flatten_results = [result for worker_results in results for result in worker_results]
    flatten_results.sort(key=lambda x: x[0])
    return [result for (_, result) in flatten_results]


class ProgressHandler:
    """Progress handler. This class wraps the rich Progress class and provides
    an interface to control the progress bar within `pyhectiqlab`.

    The progress bar can be hidden by setting the `hide` parameter to `True`.

    Note:
        When used jointly with `register_progress`, the progress object is not owned
        by the `ProgressHandler` object and it is not the `ProgressHandler`
        responsibility to start or stop the external progress. Therefore, the wrapped
        `Progress` object will not be started when calling `start` and not be stopped
        when calling `stop`.


    Example usage:
        ```python
        progress = ProgressHandler(hide=True)
        task_id = progress.add_task("Downloading...", total=10)
        for i in range(10):
            progress.update(task_id, advance=1)
        progress.stop_task(task_id)
        progress.stop()
        ```

    """

    _external_progress: Optional[Progress] = None

    def __init__(self):
        self.progress = None if getenv("HECTIQLAB_HIDE_PROGRESS") else self.prepare_progress()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @classmethod
    def using_external(cls):
        return cls._external_progress is not None

    @classproperty
    def external_progress(cls):
        return cls._external_progress

    @staticmethod
    def prepare_progress():
        """Prepares the progress object. If the external progress is used, it returns it. Otherwise
        it returns a new progress object."""
        # priority to external progress
        if ProgressHandler.using_external():
            return ProgressHandler.external_progress
        progress = Progress(
            TextColumn("[bold bright_blue]{task.description}", justify="left"),
            BarColumn(),
            TaskProgressColumn(text_format="[progress.iteration]{task.percentage:>3.0f}%", show_speed=True),
            FileSizeColumn(),
            TimeRemainingColumn(compact=False, elapsed_when_finished=True),
            transient=False,
        )
        return progress

    def add_task(self, desc: str, total: int):
        """Adds a task with `desc` and `total` to the progress bar. See `rich.progress.Progress.add_task`
        for more information."""
        if self.progress is None:
            return
        return self.progress.add_task(desc, total=total)

    def update(self, task_id: Optional[int], advance: int):
        """Updates the progress of a task with `task_id` by `advance`. See `rich.progress.Progress.update`
        for more information."""
        if self.progress is None or task_id is None:
            return
        self.progress.update(task_id, advance=advance)

    def stop_task(self, task_id: Optional[int]):
        """Stops the task with `task_id`. See `rich.progress.Progress.stop_task` for more information."""

        if self.progress is None or task_id is None:
            return
        self.progress.stop_task(task_id)
        if self.progress.live.transient or self.using_external():
            self.progress.remove_task(task_id)

    def start(self):
        """Starts the progress bar."""
        if self.progress is None or self.using_external():
            return
        self.progress.start()

    def stop(self):
        """Stops the progress bar."""
        # Cannot stop progress if is None or it is used elsewhere
        if self.progress is None or self.using_external():
            return
        self.progress.stop()


def register_progress(progress: Progress):
    """Register a `rich.progress.Progress` object."""
    if isinstance(progress, Progress):
        ProgressHandler._external_progress = progress
