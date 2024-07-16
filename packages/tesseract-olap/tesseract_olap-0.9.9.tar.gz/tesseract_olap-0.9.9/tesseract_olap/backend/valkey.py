from io import BytesIO
from typing import TYPE_CHECKING, Union

import polars as pl
import redis as valkey

from tesseract_olap.backend import Result
from tesseract_olap.common import hide_dsn_password
from tesseract_olap.exceptions.backend import UpstreamInternalError, UpstreamNotPrepared

from .cache import CacheConnection, CacheConnectionStatus, CacheProvider

if TYPE_CHECKING:
    from tesseract_olap.query import AnyQuery


class ValkeyProvider(CacheProvider):
    def __init__(self, dsn: str, **kwargs):
        self.dsn = dsn
        self.pool = valkey.ConnectionPool.from_url(dsn, **kwargs)

    def __repr__(self):
        return f"{type(self).__name__}(dsn='{hide_dsn_password(self.dsn)}')"

    def connect(self):
        try:
            return ValkeyConnection(self.pool, single_connection_client=True)
        except valkey.ConnectionError as exc:
            raise UpstreamNotPrepared(*exc.args) from exc
        except valkey.RedisError as exc:
            raise UpstreamInternalError(*exc.args) from exc


class ValkeyConnection(CacheConnection):
    def __init__(self, pool: valkey.ConnectionPool, **kwargs):
        self.valkey = valkey.Redis(connection_pool=pool, **kwargs)

    @property
    def status(self) -> CacheConnectionStatus:
        return (
            CacheConnectionStatus.CONNECTED
            if self.valkey.connection is not None and self.valkey.ping()
            else CacheConnectionStatus.CLOSED
        )

    def close(self) -> None:
        return self.valkey.close()

    def exists(self, query: "AnyQuery") -> bool:
        return self.valkey.exists(query.key) == 1

    def store(self, query: "AnyQuery", result: "Result[pl.DataFrame]") -> None:
        dfio = result.data.write_ipc(file=None, compression="lz4")
        try:
            self.valkey.set(query.key, dfio.getvalue())
        except valkey.ConnectionError as exc:
            raise UpstreamNotPrepared(*exc.args) from exc
        except valkey.RedisError as exc:
            raise UpstreamInternalError(*exc.args) from exc

    def retrieve(self, query: "AnyQuery") -> Union["Result[pl.DataFrame]", None]:
        try:
            res: bytes = self.valkey.get(query.key)  # type: ignore
        except valkey.ConnectionError as exc:
            raise UpstreamNotPrepared(*exc.args) from exc
        except valkey.RedisError as exc:
            raise UpstreamInternalError(*exc.args) from exc

        if res is None:
            return None

        return Result(data=pl.read_ipc(BytesIO(res)), columns=query.columns)

    def ping(self) -> bool:
        return self.valkey.ping()  # type: ignore
