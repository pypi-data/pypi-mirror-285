import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, final

import httpx
from bs4 import Tag

import qcanvas_backend.database.types as db
from qcanvas_backend.net.resources.download.download_progress import DownloadProgress

# todo should allow an existing client to be passed into the constructor. we'll see after i figure out how to handle downloading resources
# Use a single client for the generic downloader, making a lot of clients is not a great idea
_generic_download_client = httpx.AsyncClient()

_logger = logging.getLogger(__name__)


class LinkExtractor(ABC):
    """
    Resource ids are formatted using this:
    <extractor name>{RESOURCE_ID_SEPARATOR}<resource id>
    E.g. canvas$12341234
    """

    RESOURCE_ID_SEPARATOR = "$"

    def __init__(self, extractor_id: str, tag_whitelist: list[str]):
        self._extractor_id = extractor_id
        self._tag_whitelist = tag_whitelist

    @final
    def accepts_tag(self, tag: Tag) -> bool:
        if tag.name not in self.tag_whitelist:
            return False
        else:
            return self._is_tag_valid(tag)

    @abstractmethod
    def _is_tag_valid(self, tag: Tag) -> bool: ...

    @final
    def resource_id_from_tag(self, tag: Tag) -> str:
        return f"{self.extractor_id}{self.RESOURCE_ID_SEPARATOR}{self._tag_id(tag)}"

    @abstractmethod
    def _tag_id(self, tag: Tag) -> str: ...

    @final
    async def resource_from_tag(
        self, tag: Tag, course_id: str, resource_id: str
    ) -> db.Resource:
        resource = await self._extract_resource(tag)
        resource.id = resource_id
        resource.course_id = course_id
        resource.discovery_date = datetime.now()

        return resource

    @abstractmethod
    async def _extract_resource(self, tag: Tag) -> db.Resource: ...

    async def download(
        self, resource: db.Resource, destination: Path
    ) -> AsyncIterator[DownloadProgress]:
        _logger.info("Using generic downloader for %s", resource.id)

        yield DownloadProgress(0, 0)

        async with _generic_download_client.stream(
            url=resource.url, method="get", follow_redirects=True
        ) as response:  # type: httpx.Response
            async for progress in self._download_stream_response(destination, response):
                yield progress

    @staticmethod
    async def _download_stream_response(
        destination: Path, response: httpx.Response
    ) -> AsyncIterator[DownloadProgress]:
        with open(destination, "wb") as out:
            async for chunk in response.aiter_bytes():
                out.write(chunk)

                yield DownloadProgress(
                    total_bytes=int(response.headers["content-length"]),
                    downloaded_bytes=int(response.num_bytes_downloaded),
                )

    @property
    def tag_whitelist(self):
        return self._tag_whitelist

    @property
    def extractor_id(self):
        return self._extractor_id
