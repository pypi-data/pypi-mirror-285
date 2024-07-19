import clisync
import logging

from typing import Optional, Union, List
import datetime as dt

from pyhectiqlab.project import Project
from pyhectiqlab.run import Run
from pyhectiqlab.client import Client
from pyhectiqlab.decorators import functional_alias, execute_online_only
from pyhectiqlab.utils import is_running_event_loop

logger = logging.getLogger()

class Message:

    _client: Client = Client
    _cache: dict = {} # Cache str -> Message
    _last_get_all = None
    _delay_get_all = 5 # 5 seconds
    _observed_keys = set()

    def __init__(self, key: str, value: str, run_id: str):
        self.key = key
        self.value = value
        self._run_id = run_id

    @staticmethod
    @execute_online_only
    @functional_alias("publish_message")
    @clisync.include(wait_response=True)
    def publish(
        key: str,
        value: str,
        run: Optional[Union[str, int]] = None,
        project: Optional[str] = None,
        wait_response: bool = False,
    ):
        """Publish a message.

        Args:
            key (str): The key of the message.
            value (str): The value of the message.
            run (Union[str, int], optional): The run to publish the message to. Defaults to None.
            project (str, optional): The project to publish the message to. Defaults to None.
            wait_response (bool, optional): Whether to wait for a response. Defaults to False.
        """

        if not key:
            logger.error("A key must be provided.")
            return
        if not value:
            logger.error("A value must be provided.")
            return

        run_id = None
        project = Project.get(project)
        if isinstance(run, int):
            if not project:
                logger.error("A project must be provided when `run` is an integer.")
                return
            run = Run.retrieve(rank=run, project=project)
            if not run:
                logger.error(f"Run with rank {run} not found.")
                return
            run_id = run["id"]
        else:
            run_id = Run.get_id(run)
        
        if not run_id:
            logger.error("A run must be provided.")
            return
        
        
        return Message._client.post("/app/messages/publish", 
                                    json={"key": key, "value": value, "run": run_id}, 
                                    wait_response=wait_response)

    @staticmethod
    @execute_online_only
    @functional_alias("get_all_messages")
    # @clisync.include(wait_response=True)
    def get_all(
        run: Optional[Union[str, int]] = None,
        project: Optional[str] = None,
        wait_response: bool = True,
    ):
        """Get all messages for a run.

        Args:
            run (Union[str, int], optional): The run to get messages for. Defaults to None.
            project (str, optional): The project to get messages for. Defaults to None.

        Returns:
            List[Message]: A list of messages if `wait_response` is True. Otherwise, None.
          
        """
        if Message._last_get_all:
            diff = dt.datetime.now() - Message._last_get_all
            if diff.total_seconds() < Message._delay_get_all:
                logger.debug(f"Message.get_all() called too soon. Ignoring. Waited {diff.total_seconds()} seconds.")
                return

        Message._last_get_all = dt.datetime.now()

        if is_running_event_loop():
            logger.error("Messages cannot be fetched from an event loop (jupyter notebook). Future support will be added.")
            return

        project = Project.get(project)
        if isinstance(run, int):
            if not project:
                logger.error("A project must be provided when `run` is an integer.")
                return
            run = Run.retrieve(rank=run, project=project)
            if not run:
                logger.error(f"Run with rank {run} not found.")
                return
            run_id = run["id"]
        else:
            run_id = Run.get_id(run)
        
        if not run_id:
            logger.error("A run must be provided.")
            return
        if wait_response:
            results = Message._client.get("/app/messages", 
                                        params={"run": run_id}, 
                                        wait_response=True)
            results  = results or {}
            return [Message(key, value, run_id) for key, value in results.items()]
        else:
            def composition():
                results = Message._client.get("/app/messages", 
                                            params={"run": run_id}, 
                                            wait_response=True)
                for key, value in results.items():
                    # Cache the message
                    Message._cache[key] = Message(key, value, run_id)

            Message._client.execute(composition,
                                    wait_response=False, 
                                    is_async_method=False)
    
    def ack(self):
        """Acknowledge a message.
        """
        if not self.key:
            logger.error("`ack()` can only be called on a message object with `self.key`.")
            return
        if not self._run_id:
            logger.error("`ack()` can only be called on a message object with a self._run_id.")
            return
        # Remove from _cache
        if self.key in Message._cache:
            Message._cache.pop(self.key, None)
        return Message._client.post("/app/messages/ack", 
                                    json={"key": self.key, "run": self._run_id}, 
                                    wait_response=True)

    @staticmethod
    @execute_online_only
    @functional_alias("get_message")
    def get(key: str,
            run_id: Optional[str] = None):
        """Method to get a message by key. The message is retrieved from the cache 
        if it exists. When first called, it will fetch all messages for the active
        run.

        Args:
            key (str): The key of the message.
            run_id (Optional[str], optional): The run to get the message from. Defaults to None.
        """
        if not key:
            logger.error("A key must be provided.")
            return
        
        if key not in Message._observed_keys:
            Message._observed_keys.add(key)
            Message.declare_keys([key])

        Message.get_all(run=run_id, wait_response=False) # Warm up the cache
        return Message._cache.get(key)
    
    @staticmethod
    @execute_online_only
    @functional_alias("declare_observed_messages")
    def declare_keys(keys: List[str], 
                     run_id: Optional[str] = None,
                     wait_response: bool = False):
        """Declare the keys observed by the client.

        Args:
            keys (list): A list of keys observed by the client.
        """
        run_id = Run.get_id(run_id)
        return Message._client.post("/app/messages/declare", 
                                    json={"keys": keys, "run": run_id}, 
                                    wait_response=wait_response)

    def __str__(self):
        if not self.key:
            return "Message()"
        return f"Message(key={self.key}, value={self.value})"
    
    def __repr__(self):
        return str(self)