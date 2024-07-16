import abc
from enum import Enum
from typing import Union

import polars as pl
from lfudacache import LFUDACache

from tesseract_olap.query import AnyQuery

from .models import Result

CacheConnectionStatus = Enum("CacheConnectionStatus", ["CLOSED", "CONNECTED"])


class CacheProvider(abc.ABC):
    """Base class for the implementation of a cache layer for the Backend."""

    def __repr__(self):
        return f"{type(self).__name__}"

    @abc.abstractmethod
    def connect(self) -> "CacheConnection":
        raise NotImplementedError


class CacheConnection(abc.ABC):
    """Internal Base class for individual connections to the cache layer."""

    @property
    @abc.abstractmethod
    def status(self) -> "CacheConnectionStatus":
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def store(self, query: "AnyQuery", result: "Result[pl.DataFrame]") -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve(self, query: "AnyQuery") -> Union["Result[pl.DataFrame]", None]:
        raise NotImplementedError

    @abc.abstractmethod
    def ping(self) -> bool:
        raise NotImplementedError


class DummyProvider(CacheProvider):
    """A CacheProvider used when the user doesn't set a valid one. Will always MISS."""

    def connect(self):
        return DummyConnection()


class DummyConnection(CacheConnection):
    """The CacheConnection associated to DummyProvider. Will always MISS."""

    @property
    def status(self):
        return CacheConnectionStatus.CONNECTED

    def close(self):
        pass

    def store(self, query: "AnyQuery", result: "Result[pl.DataFrame]"):
        pass

    def retrieve(self, query: "AnyQuery"):
        return None

    def ping(self):
        return True


class LfuProvider(CacheProvider):
    """Stores elements in a dictionary under the Least Frequently Used caching stategy."""

    def __init__(self, maxsize: int = 64) -> None:
        self.store = LFUDACache(maxsize)

    def connect(self):
        return LfuConnection(self.store)


class LfuConnection(CacheConnection):
    """The CacheConnection associated to LfuProvider."""

    def __init__(self, store: "LFUDACache") -> None:
        self.storage = store

    @property
    def status(self):
        return CacheConnectionStatus.CONNECTED

    def close(self):
        pass

    def store(self, query: "AnyQuery", result: "Result[pl.DataFrame]"):
        self.storage[query.key] = result

    def retrieve(self, query: "AnyQuery") -> Union["Result[pl.DataFrame]", None]:
        return self.storage.get(query.key)

    def ping(self):
        return True
