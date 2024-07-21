import platform
import re
from abc import ABC, abstractmethod
from pathlib import Path, PurePath
from typing import Sequence, Tuple

from asynctaskpool import AsyncTaskPool

import qcanvas_backend.database.types as db
from qcanvas_backend.database import QCanvasDatabase
from qcanvas_backend.net.resources.extracting.extractors import Extractors
from qcanvas_backend.net.resources.scanning.resource_scanner import ResourceScanner


class ResourceManager(ABC):
    def __init__(
        self,
        database: QCanvasDatabase,
        download_dest: Path,
        extractors: Extractors = Extractors(),
    ):
        super().__init__()
        self._download_pool = AsyncTaskPool[None]()
        self._db = database
        self._extractors = extractors
        self._scanner = ResourceScanner(extractors)
        self._download_dest = download_dest

    def add_existing_resources(self, existing_resources: Sequence[db.Resource]):
        self._scanner.add_existing_resources(existing_resources)

    async def download(self, resource: db.Resource) -> None:
        if resource.download_state != db.ResourceDownloadState.DOWNLOADED:
            await self._download_pool.submit(resource.id, self._download_task(resource))

    async def _download_task(self, resource: db.Resource):
        try:
            extractor = self._extractors.extractor_for_resource(resource)
            destination = self.resource_download_location(resource)

            destination.parent.mkdir(parents=True, exist_ok=True)

            async for progress in extractor.download(
                resource,
                destination=destination,
            ):
                self.on_download_progress(
                    resource=resource,
                    current=progress.downloaded_bytes,
                    total=progress.total_bytes,
                )
        except Exception as e:
            await self._db.record_resource_download_failed(resource, message=str(e))
            self.on_download_failed(resource)
            raise RuntimeError() from e
        else:
            await self._db.record_resource_downloaded(resource)
            self.on_download_finished(resource)

    def resource_download_location(self, resource: db.Resource) -> Path:
        file_name, file_suffix = ResourceManager._split_resource_name(resource)
        file_suffix = f" [{resource.id}]{file_suffix}"
        # Ensure the filename is not too long, most filesystems permit up to 255 chars
        file_name = file_name[: 255 - len(file_suffix)]

        return (
            self._download_dest
            / self._replace_illegal_chars(resource.course.name)
            / self._replace_illegal_chars(file_name + file_suffix)
        )

    @staticmethod
    def _split_resource_name(resource: db.Resource) -> Tuple[str, str]:
        file = PurePath(resource.file_name)
        return file.stem, file.suffix

    @staticmethod
    def _replace_illegal_chars(file_name: str) -> str:
        if platform.system() == "Windows":
            return re.sub(r"[<>:\"/\\|?*]", "_", file_name)
        else:
            return file_name.replace("/", "_")

    @property
    def scanner(self) -> ResourceScanner:
        return self._scanner

    @property
    def extractors(self) -> Extractors:
        return self._extractors

    @abstractmethod
    def on_download_progress(self, resource: db.Resource, current: int, total: int): ...

    @abstractmethod
    def on_download_failed(self, resource: db.Resource): ...

    @abstractmethod
    def on_download_finished(self, resource: db.Resource): ...
