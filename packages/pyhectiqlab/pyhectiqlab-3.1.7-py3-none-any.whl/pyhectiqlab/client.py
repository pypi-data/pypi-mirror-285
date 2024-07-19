import httpx
import asyncio
import threading
import logging
import os
import io
from contextlib import contextmanager

from typing import Any, Optional, List, Type, Union
from functools import partial
from google.resumable_media.requests import ResumableUpload


from pyhectiqlab.auth import Auth
from pyhectiqlab.decorators import classproperty, request_handle, execute_online_only
from pyhectiqlab.settings import getenv
from pyhectiqlab.utils import ProgressHandler
from pyhectiqlab import API_URL


logger = logging.getLogger()

ResponseType = Union[dict[str, Any], bytes, Type[None]]


class Client:
    """
    Client singleton for making sync and async requests in the Hectiq Lab API. This client
    can be used in a context manager, or as a singleton. For performing async requests, the object
    must be instanciated.

    Example:
    ```python
    from pyhectiqlab.client import Client
    import asyncio

    client = Client()

    # Sync request
    response = client.get("/app/auth/is-logged-in")

    # Async request
    response = asyncio.run(client.async_get("/app/auth/is-logged-in"))
    ```
    """

    _auth: Auth = None
    _client: httpx.Client = None
    _online: bool = True
    _timeout: float = 30.0  # seconds
    _progress: Optional[ProgressHandler] = None
    _logged_error_messages: set[str] = set()

    @classproperty
    def auth(cls) -> Auth:
        if cls._auth is None:
            cls._auth = Auth()
        return cls._auth
    
    @classproperty
    def progress(cls) -> ProgressHandler:
        if cls._progress is None:
            cls.initiate_progress()
        return cls._progress

    @classproperty
    def client(cls) -> httpx.Client:
        if cls._client is None:
            cls._client = httpx.Client(auth=cls.auth, timeout=cls._timeout)
        return cls._client

    @staticmethod
    def is_logged():
        return Client.auth.is_logged()

    @staticmethod
    def online(status: Optional[bool] = None):
        if status is not None:
            Client._online = status
        if getenv("HECTIQLAB_OFFLINE_MODE"):
            return False
        return Client.auth.online and Client._online

    @staticmethod
    def get(url: str, wait_response: bool = False, **kwargs: Any) -> ResponseType:
        return Client.request("get", url, wait_response=wait_response, **kwargs)

    @staticmethod
    @execute_online_only
    def post(url: str, wait_response: bool = False, **kwargs: Any) -> ResponseType:
        return Client.request("post", url, wait_response=wait_response, **kwargs)

    @staticmethod
    @execute_online_only
    def patch(url: str, wait_response: bool = False, **kwargs: Any) -> ResponseType:
        return Client.request("patch", url, wait_response=wait_response, **kwargs)

    @staticmethod
    @execute_online_only
    def put(url: str, wait_response: bool = False, **kwargs: Any) -> ResponseType:
        return Client.request("put", url, wait_response=wait_response, **kwargs)

    @staticmethod
    @execute_online_only
    def delete(url: str, wait_response: bool = False, **kwargs: Any) -> ResponseType:
        return Client.request("delete", url, wait_response=wait_response, **kwargs)

    @staticmethod
    @execute_online_only
    def upload_sync(local_path: str, policy: dict) -> ResponseType:
        """Upload a file."""
        upload_method = policy.get("upload_method")
        if not upload_method:
            return

        if upload_method == "fragment":
            res = Client.upload_fragment_sync(local_path, policy)
        elif upload_method == "single":
            res = Client.upload_single_sync(local_path, policy.get("policy"), bucket=policy.get("bucket_name"))
        return res

    @staticmethod
    @execute_online_only
    async def upload_async(local_path: str, policy: dict) -> ResponseType:
        """Upload a file."""
        upload_method = policy.get("upload_method")
        if not upload_method:
            return

        async with httpx.AsyncClient(timeout=Client._timeout) as asyncClient:
            if upload_method == "fragment":
                res = await Client.upload_fragment_async(local_path, policy, client=asyncClient)
            elif upload_method == "single":
                res = await Client.upload_single_async(
                    local_path,
                    policy.get("policy"),
                    bucket=policy.get("bucket_name"),
                    client=asyncClient,
                )
        return res

    @staticmethod
    def get_upload_method(policy: dict) -> dict[str, Any]:
        """Get the upload method from the policy."""
        if "upload_method" in policy:
            return policy.get("upload_method")
        return policy.get("policy", {}).get("upload_method")

    @staticmethod
    @execute_online_only
    def upload_many_sync(paths: List[str], policies: List[dict]) -> None:
        """Upload many files synchronously."""
        single_upload_files = []
        fragment_upload_files = []
        for path, policy in zip(paths, policies):
            if not policy:
                continue
            method = Client.get_upload_method(policy)
            if method == "fragment":
                fragment_upload_files.append((path, policy))
            elif method == "single":
                single_upload_files.append((path, policy))

        for path, policy in single_upload_files:
            Client.upload_single_sync(path, policy.get("policy"), bucket=policy.get("bucket_name"))
        for path, policy in fragment_upload_files:
            Client.upload_fragment_sync(path, policy)

    @staticmethod
    @execute_online_only
    async def upload_many_async(paths: List[str], policies: List[dict]) -> None:
        """Upload many files asynchronously."""
        single_upload_files = []
        fragment_upload_files = []
        for path, policy in zip(paths, policies):
            if not policy:
                continue
            method = Client.get_upload_method(policy)
            if method == "fragment":
                fragment_upload_files.append((path, policy))
            elif method == "single":
                single_upload_files.append((path, policy))

        async with httpx.AsyncClient() as client:
            tasks = []
            for path, policy in single_upload_files:
                task = Client.upload_single_async(
                    path, policy.get("policy"), bucket=policy.get("bucket_name"), client=client
                )
                tasks.append(asyncio.ensure_future(task))
            for path, policy in fragment_upload_files:
                task = Client.upload_fragment_async(path, policy, client=client)
                tasks.append(asyncio.ensure_future(task))
            await asyncio.gather(*tasks)

    @staticmethod
    @execute_online_only
    def upload_fragment_sync(local_path: str, policy: dict, chunk_size: int = 1024 * 1024 * 32) -> None:
        """Upload a file in fragments."""
        upload = ResumableUpload(upload_url=policy.get("url"), chunk_size=chunk_size)
        with open(local_path, "rb") as f:
            data = f.read()
        upload._stream = io.BytesIO(data)
        upload._total_bytes = len(data)
        upload._resumable_url = policy.get("url")

        filename = os.path.basename(local_path)
        task_desc = f"Upload {filename if len(filename) <= 15 else filename[:12] + '...'}"
        task_id = Client.progress.add_task(task_desc, total=upload.total_bytes)

        bytes_uploaded = 0
        while upload.finished == False:
            method, url, payload, headers = upload._prepare_request()
            if headers.get("content-type") == None:
                headers["content-type"] = "application/octet-stream"
            result = httpx.request(method, url, data=payload, headers=headers, timeout=Client._timeout)
            upload._process_resumable_response(result, len(payload))
            Client.progress.update(task_id, advance=upload.bytes_uploaded - bytes_uploaded)
            bytes_uploaded = upload.bytes_uploaded
        Client.progress.stop_task(task_id)

    @staticmethod
    @execute_online_only
    async def upload_fragment_async(
        local_path: str,
        policy: dict,
        chunk_size: int = 1024 * 1024 * 32,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """Upload a file in fragments."""
        upload = ResumableUpload(upload_url=policy.get("url"), chunk_size=chunk_size)
        with open(local_path, "rb") as f:
            data = f.read()
        upload._stream = io.BytesIO(data)
        upload._total_bytes = len(data)
        upload._resumable_url = policy.get("url")

        filename = os.path.basename(local_path)
        task_desc = f"Upload {filename if len(filename) <= 15 else filename[:12] + '...'}"
        task_id = Client.progress.add_task(task_desc, total=upload.total_bytes)

        bytes_uploaded = 0
        while upload.finished == False:
            method, url, payload, headers = upload._prepare_request()
            if headers.get("content-type") == None:
                headers["content-type"] = "application/octet-stream"
            result = await (client or httpx).request(
                method, url, data=payload, headers=headers, timeout=Client._timeout
            )
            upload._process_resumable_response(result, len(payload))
            Client.progress.update(task_id, advance=upload.bytes_uploaded - bytes_uploaded)
            bytes_uploaded = upload.bytes_uploaded
        Client.progress.stop_task(task_id)

    @staticmethod
    @execute_online_only
    def upload_single_sync(local_path: str, policy: dict, bucket: str) -> ResponseType:
        """Upload a file in a single request synchronously."""
        url = policy.get("url")
        num_bytes = os.path.getsize(local_path)
        with open(local_path, "rb") as content:
            files = {"file": (bucket, content)}
            upload_method = request_handle(httpx.post)

            filename = os.path.basename(local_path)
            task_desc = f"Upload {filename if len(filename) <= 15 else filename[:12] + '...'}"
            task_id = Client.progress.add_task(task_desc, total=num_bytes)

            res = upload_method(url, data=policy.get("fields"), files=files)
        Client.progress.update(task_id, advance=num_bytes)
        Client.progress.stop_task(task_id)
        return res

    @staticmethod
    @execute_online_only
    async def upload_single_async(
        local_path: str,
        policy: dict,
        bucket: str,
        client: Optional[httpx.AsyncClient] = None,
    ) -> ResponseType:
        """Upload a file in a single request asynchronously."""
        url = policy.get("url")
        with open(local_path, "rb") as content:
            num_bytes = os.path.getsize(local_path)
            files = {"file": (bucket, content)}
            upload_method = client.post if client else request_handle(httpx.post)
            filename = os.path.basename(local_path)
            task_desc = f"Upload {filename if len(filename) <= 15 else filename[:12] + '...'}"
            task_id = Client.progress.add_task(task_desc, total=num_bytes)
            res = await upload_method(url, data=policy.get("fields"), files=files)
        Client.progress.update(task_id, advance=num_bytes)
        Client.progress.stop_task(task_id)
        return res

    @staticmethod
    def download_sync(url: str, local_path: str, num_bytes: Optional[int] = None) -> str:
        """Download a file synchronously.

        Args:
            url (str): URL of the file to download.
            local_path (str): Local path to save the file (includes the file name)
            num_bytes (Optional[int], optional): Number of bytes to download. Default: None.
        """

        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            filename = os.path.basename(local_path)
            task_desc = f"Download {filename if len(filename) <= 15 else filename[:12] + '...'}"
            task_id = Client.progress.add_task(task_desc, total=num_bytes)
            with httpx.stream("GET", url) as r:
                for data in r.iter_bytes():
                    f.write(data)
                    Client.progress.update(task_id, advance=len(data))
        return local_path

    @staticmethod
    async def download_async(
        url: str,
        local_path: str,
        num_bytes: Optional[int] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> str:
        """Download a file asynchronously.

        Args:
            url (str): URL of the file to download.
            local_path (str): Local path to save the file (includes the file name)
            num_bytes (Optional[int], optional): Number of bytes to download. Default: None.
            client: (httpx.Client, optional): Alternative client to use (may be AsyncClient). Default: None.
            progress: (rich.progress.Progress, optional): Progress object for track download. Default: None.
        """
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            filename = os.path.basename(local_path)
            task_desc = f"Download {filename if len(filename) <= 15 else filename[:12] + '...'}"
            task_id = Client.progress.add_task(task_desc, total=num_bytes)
            async with (client or httpx.AsyncClient()).stream("GET", url) as r:
                async for data in r.aiter_bytes():
                    f.write(data)
                    Client.progress.update(task_id, advance=len(data))
        Client.progress.stop_task(task_id)
        return local_path

    @staticmethod
    def download_many_sync(urls: List[str], local_paths: List[str], num_bytes: List[int], **kwargs) -> None:
        """Download many files synchronously.

        Args:
            urls (List[str]): URLs of the files to download.
            local_paths (List[str]): Local paths to save the files (includes the file names)
            num_bytes (List[int]): Number of bytes to download.
        """
        for url, local_path, byt in zip(urls, local_paths, num_bytes):
            Client.download_sync(url, local_path, byt)

    @staticmethod
    async def download_many_async(urls: List[str], local_paths: List[str], num_bytes: List[int], **kwargs) -> None:
        """Download many files asynchronously.

        Args:
            urls (List[str]): URLs of the files to download.
            local_paths (List[str]): Local paths to save the files (includes the file names)
            num_bytes (List[int]): Number of bytes to download.
        """
        async with httpx.AsyncClient() as client:
            tasks = []
            for url, local_path, byt in zip(urls, local_paths, num_bytes):
                task = Client.download_async(url, local_path, byt, client=client)
                tasks.append(asyncio.ensure_future(task))
            await asyncio.gather(*tasks)

    @staticmethod
    def request(call: str, url: str, wait_response: bool = False, **kwargs) -> ResponseType:
        """Execute a request to the Hectiq Lab API."""
        url = Client.format_url(url)
        method = request_handle(partial(getattr(Client.client, call), url=url))
        return Client.execute(method=method, wait_response=wait_response, **kwargs)

    @staticmethod
    def execute(
        method: callable,
        wait_response: bool = False,
        is_async_method: bool = False,
        with_progress: bool = False,
        **kwargs,
    ) -> ResponseType:

        def execution_handler(**kwargs):
            """Execute a request in the background or in the main thread."""
            if wait_response:
                if is_async_method:
                    return asyncio.run(method(**kwargs))
                return method(**kwargs)

            def threading_method(**kwargs):
                if is_async_method:
                    return asyncio.run(method(**kwargs))
                return method(**kwargs)

            t = threading.Thread(target=threading_method, kwargs=kwargs)
            t.start()
            return

        if not with_progress:
            return execution_handler(**kwargs)

        with Client.progress_context():
            result = execution_handler(**kwargs)
        return result

    @staticmethod
    @contextmanager
    def progress_context():
        Client.initiate_progress()
        yield
        Client.reset_progress()

    @staticmethod
    def initiate_progress():
        Client._progress = ProgressHandler()
        try:
            Client._progress.start()
        except:
            msg = (
                "Could not start progress handler. "
                "This is likely caused by the rich libary, you may have many Progress instances "
                "in the same process. Try registering the root Progress instance before executing "
                "the script using `hl.register_progress(progress)`. Continuing without progress."
            )
            if msg not in Client._logged_error_messages:
                logger.warning(msg)
                Client._logged_error_messages.add(msg)

            Client._progress.progress = None

    @staticmethod
    def reset_progress():
        if Client.progress is None:
            return
        Client.progress.stop()
        Client._progress = None

    @staticmethod
    def format_url(url: str) -> str:
        if not url.startswith("http") and url[0] == "/":
            url = API_URL + url
        return url
