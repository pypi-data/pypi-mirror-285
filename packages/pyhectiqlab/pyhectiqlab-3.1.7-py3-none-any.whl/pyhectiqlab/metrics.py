from collections import defaultdict
from typing import Callable, List, Literal, Optional, Tuple, Union
from functools import partial

import threading
import numpy as np
import time
import datetime as dt
import logging

logger = logging.getLogger("pyhectiqlab")


class RepeatedTimer(threading.Thread):
    """
    RepeatedTimer class is used to run a method at a given interval.

    Args:
        method (callable): Method to run.
        delay (int): Delay between two executions.
    """

    def __init__(self, method: Callable[[], None], delay: int):
        super().__init__()
        self.daemon = True
        self._stopper = threading.Event()
        self.delay = delay
        self.method = method

    def run(self):
        while not self._stopper.wait(self.delay):
            self.method()

    def stopped(self):
        return self._stopper.is_set()

    def stop(self):
        self._stopper.set()


class MetricsManager:
    """
    MetricsManager class is used to manage the metrics cache and push data to the server.

    Args:
        push_method (callable, optional): Function to push data to the server
        max_cache_timeout (int): Maximum number of seconds in the cache
        max_cache_length (int): Number of elements in the cache to trigger a cache dump
        min_cache_flush_delay (int): Minimum number of seconds between two dumps
        aggregate_metrics (str): Wheter to push all data in cache or aggregate
    """

    __max_cache_quantity_per_second = 200

    def __init__(
        self,
        push_method: Callable[[str, List[float]], None],
        run_id: Optional[str] = None,
        max_cache_timeout: int = 10,
        max_cache_length: int = 100,
        min_cache_flush_delay: int = 5,
        aggregate_metrics: str = "none",
    ):
        self.cache = defaultdict(list)
        self.cache_last_push = {}
        self._warning_is_shown = False
        self.max_cache_length = max_cache_length
        self.min_cache_flush_delay = min_cache_flush_delay

        self.push_method = partial(push_method, run_id=run_id)
        self.set_aggr(aggregate_metrics)

        self.timer = RepeatedTimer(self.flush_cache, max_cache_timeout)
        self.timer.start()
        return

    def update_cache_settings(
        self,
        max_cache_timeout: Optional[int] = None,
        max_cache_length: Optional[int] = None,
        min_cache_flush_delay: Optional[int] = None,
    ):
        """
        Update cache settings.
        """

        if max_cache_timeout is not None:
            self.max_cache_timeout = max_cache_timeout
            self.timer.stop()
            self.timer = RepeatedTimer(self.flush_cache, max_cache_timeout)
            self.timer.start()
        if max_cache_length is not None:
            self.max_cache_length = max_cache_length
        if min_cache_flush_delay is not None:
            self.min_cache_flush_delay = min_cache_flush_delay

    def set_aggr(self, new_value: Literal["none", "sum", "max", "mean"]):
        vals = ["none", "sum", "max", "mean"]
        assert new_value in vals, f"Aggr must be in {vals}"
        self.aggregate_metrics = new_value

    def get_agg(self, key: str, run_id: str) -> List[Tuple[Union[int, float], Union[int, float]]]:
        # raise NotImplementedError()
        return []

    def add(self, key: str, step: int, value: float) -> None:
        """
        Add a new metric to the cache.
        """
        if value is None:
            return
        self.cache[key].append((float(step), float(value), dt.datetime.now(tz=dt.timezone.utc).timestamp()))
        if len(self.cache[key]) > self.max_cache_length:
            if key in self.cache_last_push:
                last_push_time = self.cache_last_push[key]
                elapsed = time.time() - last_push_time
                if elapsed < self.min_cache_flush_delay:
                    return
            self.push_data(key)

    def subsample(self, data: List[float]) -> List[float]:
        normalized_max = int(self.__max_cache_quantity_per_second * self.min_cache_flush_delay)
        if len(data) <= normalized_max:
            return data
        if self._warning_is_shown == False:
            logger.warning(
                f"Your metrics rate ({len(data)//self.min_cache_flush_delay} metrics/second) is exceeding the "
                "maximum rate ({MetricsManager.__max_cache_quantity_per_second}/second). Your metrics have been "
                "subsampled automatically."
            )
            logger.warning(
                "Consider reducing the number of metrics you push or setting an aggregation method with "
                "`run.set_metrics_aggr('mean')`."
            )
            logger.warning("See the documentation for details https://docs.hectiq.ai/objects/metrics/.")
            self._warning_is_shown = True
        indexes = np.linspace(0, len(data) - 1, normalized_max).astype(int)
        return np.array(data)[indexes].tolist()

    def push_data(self, key: str) -> None:
        self.cache_last_push[key] = time.time()
        if self.push_method is None:
            self.cache[key] = []
            if self._warning_is_shown == False:
                logger.warning(
                    "No push method has been set. Please set a push method with `run.set_metrics_push_method`."
                )
            return

        if self.aggregate_metrics == "none":
            data = self.subsample(self.cache[key])
            self.push_method(key, data)
        elif self.aggregate_metrics == "mean":
            k = [_[0] for _ in self.cache[key]]
            s = [_[1] for _ in self.cache[key]]
            t = [_[2] for _ in self.cache[key]]
            if len(k) > 0:
                self.push_method(key, [(float(np.max(k)), float(np.mean(s)), float(np.mean(s)))])
        elif self.aggregate_metrics == "max":
            k = [_[0] for _ in self.cache[key]]
            s = [_[1] for _ in self.cache[key]]
            t = [_[2] for _ in self.cache[key]]
            if len(k) > 0:
                self.push_method(key, [(float(np.max(k)), float(np.max(s)), float(np.mean(s)))])
        elif self.aggregate_metrics == "sum":
            k = [_[0] for _ in self.cache[key]]
            s = [_[1] for _ in self.cache[key]]
            t = [_[2] for _ in self.cache[key]]
            if len(k) > 0:
                self.push_method(key, [(float(np.max(k)), float(np.sum(s)), float(np.mean(t)))])
        self.cache[key] = []

    def __delete__(self):
        self.timer.stop()
        self.flush_cache()

    def flush_cache(self):
        for key in self.cache:
            self.push_data(key)
