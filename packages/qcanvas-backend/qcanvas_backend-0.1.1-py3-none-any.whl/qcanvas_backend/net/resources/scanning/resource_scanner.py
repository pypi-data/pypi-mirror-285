import logging
from typing import NamedTuple, Optional, Sequence

import bs4
from asynctaskpool import AsyncTaskPool
from asynctaskpool.task_failed_exception import TaskFailedError
from bs4 import Tag

import qcanvas_backend.database.types as db
from qcanvas_backend.net.resources.extracting.extractors import Extractors
from qcanvas_backend.net.resources.extracting.no_extractor_error import NoExtractorError
from qcanvas_backend.net.resources.scanning.page_resources import PageResources
from qcanvas_backend.util import CollectingTaskGroup, remove_unwanted_whitespaces
from qcanvas_backend.util.dev_failed_resource_list import FailedResourcesList

_logger = logging.getLogger(__name__)


class _HiddenResource(NamedTuple):
    resource: db.Resource
    is_hidden: bool


class ResourceScanner:
    """
    A ResourceScanner uses Extractors to extract resources from course content
    """

    def __init__(self, extractors: Extractors):
        self._cache = AsyncTaskPool[db.Resource]()
        self._extractor_collection = extractors
        self._failed_resources = FailedResourcesList.create_if_enabled()

    def add_existing_resources(self, existing_resources: Sequence[db.Resource]):
        resources_mapped_by_id = {
            resource.id: resource for resource in existing_resources
        }
        self._cache.update_results(resources_mapped_by_id)

    async def scan_pages_for_resources(
        self, pages: Sequence[db.CourseContentItem]
    ) -> list[PageResources]:
        _logger.info("Scanning %i pages for resources", len(pages))
        async with CollectingTaskGroup() as tg:
            for page in pages:
                tg.create_task(self._extract_page_resources(page))

        return tg.results

    async def _extract_page_resources(
        self, page: db.CourseContentItem
    ) -> PageResources:
        async with CollectingTaskGroup() as tg:
            for tag in self._tags_from_page(page):
                tg.create_task(
                    self._extract_resource(tag=tag, course_id=page.course_id)
                )

        invisible_resources = []
        visible_resources = []

        for resource, is_invisible in filter(None, tg.results):
            if is_invisible:
                invisible_resources.append(resource)
            else:
                visible_resources.append(resource)

        _logger.debug(
            "Found %i resources (%i invisible) on page %s (id='%s')",
            len(invisible_resources) + len(visible_resources),
            len(invisible_resources),
            page.name,
            page.id,
        )

        return PageResources(
            page_id=page.id,
            resources=visible_resources,
            invisible_resources=invisible_resources,
        )

    async def _extract_resource(
        self, tag: Tag, course_id: str
    ) -> Optional[_HiddenResource]:
        file_id = None

        try:
            extractor = self._extractor_collection.extractor_for_tag(tag)
            file_id = extractor.resource_id_from_tag(tag)

            if await self._failed_resources.failed(file_id):
                _logger.info("File %s has failed before, skipping", file_id)
                return None

            result = await self._cache.submit(
                task_id=file_id,
                future=extractor.resource_from_tag(
                    tag, course_id=course_id, resource_id=file_id
                ),
            )

            return _HiddenResource(
                resource=result, is_hidden=self._is_link_invisible(tag)
            )
        except TaskFailedError as e:
            await self._failed_resources.record_failure(file_id)

            _logger.warning(
                "Extraction failed for file_id=%s",
                file_id or "(no id)",
            )
            _logger.debug(
                "Extraction failed for file_id=%s",
                file_id or "(no id)",
                exc_info=e,
            )
        except NoExtractorError:
            pass

    @staticmethod
    def _is_link_invisible(tag: Tag) -> bool:
        return tag.name == "a" and remove_unwanted_whitespaces(tag.text) == ""

    def _tags_from_page(self, page: db.CourseContentItem) -> list[Tag]:
        if page.body is None:
            return []

        doc = bs4.BeautifulSoup(page.body, "html.parser")
        return doc.find_all(self._extractor_collection.tag_whitelist)
