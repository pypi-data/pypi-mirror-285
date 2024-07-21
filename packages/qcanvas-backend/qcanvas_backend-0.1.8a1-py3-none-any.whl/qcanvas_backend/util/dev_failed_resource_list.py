import asyncio
import logging
from typing import Union

from lightdb import LightDB
from qcanvas_api_clients.util import enable_api_caching

_logger = logging.getLogger(__name__)


class _NOPFailList:
    async def failed(self, id: str) -> bool:
        return False

    async def record_failure(self, id: str):
        pass


class FailedResourcesList:
    """
    Meant to be used as a development convenience only:
    Remembers if a resource couldn't be retrieved, so we don't bother getting it again. This is saved to disk.
    Should NOT be used for release builds!
    """

    @staticmethod
    def create_if_enabled() -> Union["FailedResourcesList", _NOPFailList]:
        if enable_api_caching:
            _logger.warning(
                'Using development "fail-db". You should not see this message in a release build!'
            )
            return FailedResourcesList()
        else:
            return _NOPFailList()

    def __init__(self):
        self.sem = asyncio.Semaphore()
        self.db = LightDB("debug_failed_resources.json")

    async def failed(self, id: str) -> bool:
        async with self.sem:
            return self.db.get(id, False)

    async def record_failure(self, id: str):
        async with self.sem:
            self.db[id] = True
            self.db.save()
