import asyncio
import logging
from pathlib import Path

from qcanvas_api_clients.canvas import Announcement, CanvasClient
from qcanvas_api_clients.panopto import PanoptoClient

import qcanvas_backend.gql_queries as gql
from qcanvas_backend.database import QCanvasDatabase
from qcanvas_backend.net.canvas import (
    CanvasDataAggregator,
    CanvasPageLoader,
    CourseMailItem,
)
from qcanvas_backend.net.panopto.panopto_data_aggregator import PanoptoDataAggregator
from qcanvas_backend.net.resources.scanning.resource_linker import ResourceLinker
from qcanvas_backend.net.resources.scanning.resource_scanner import ResourceScanner
from qcanvas_backend.net.sync._internal.canvas_data_bundle import CanvasDataBundle
from qcanvas_backend.net.sync._internal.new_content_observer import NewContentObserver
from qcanvas_backend.net.sync._internal.sync_meta import SyncMeta
from qcanvas_backend.net.sync.api_data_importer import APIDataImporter
from qcanvas_backend.net.sync.data_adapter import DataAdapter
from qcanvas_backend.net.sync.sync_receipt import SyncReceipt
from qcanvas_backend.util import CollectingTaskGroup, flatten

_logger = logging.getLogger(__name__)


class SynchronizationClient:
    """
    A SynchronizationClient uses a CanvasClient to retrieve data from canvas and a ResourceScanner to extract resources
    from each course. This data is added to the QCanvasDatabase.
    """

    def __init__(
        self,
        database: QCanvasDatabase,
        canvas_client: CanvasClient,
        panopto_client: PanoptoClient,
        resource_scanner: ResourceScanner,
        sync_meta_store_location: Path = Path(".sync_meta"),
    ):
        self._database = database
        self._canvas_client = canvas_client
        self._canvas_data_aggregator = CanvasDataAggregator(
            canvas_client=self._canvas_client
        )
        self._panopto_data_aggregator = PanoptoDataAggregator(
            panopto_client=panopto_client
        )
        self._sync_meta = SyncMeta(sync_meta_store_location)
        self._canvas_page_loader = CanvasPageLoader(canvas_client=self._canvas_client)
        self._resource_scanner = resource_scanner

    async def synchronise_canvas(self) -> SyncReceipt:
        receipt = SyncReceipt()
        new_content_tracker = NewContentObserver()
        sync_observers = [receipt, new_content_tracker]

        user_id = await self._canvas_client.get_current_user_id()
        canvas_sync_data = await self._fetch_remote_sync_data(user_id)

        async with self._database.session() as session:
            importer = APIDataImporter(session)
            resource_linker = ResourceLinker(session)
            adapter = DataAdapter(importer)

            importer.observers.extend(sync_observers)
            resource_linker.observers.extend(sync_observers)

            await adapter.convert_and_add_to_database(canvas_sync_data)

            scanned_resources = await self._resource_scanner.scan_pages_for_resources(
                new_content_tracker.new_content
            )
            await resource_linker.link_resources(scanned_resources)

        self._sync_meta.update_last_sync_time()

        _logger.info("Sync finished")
        _logger.debug(receipt)

        return receipt

    async def _fetch_remote_sync_data(self, user_id: str) -> CanvasDataBundle:
        _logger.info("Last sync time is %s", self._sync_meta.last_sync_time)

        courses = await self._canvas_data_aggregator.pull_new_and_latest_courses(
            await self._database.get_existing_course_ids()
        )
        pages = await self._canvas_page_loader.load_all_updated_page_content(
            courses=courses, last_update_time=self._sync_meta.last_sync_time
        )

        mail: list[CourseMailItem] = []
        announcements: list[Announcement] = []
        course_panopto_folders: dict[str, str] = {}

        async def get_mail():
            nonlocal mail
            nonlocal user_id
            mail = await self._canvas_data_aggregator.get_all_course_mail(user_id)

        async def get_announcements():
            nonlocal announcements
            nonlocal courses
            announcements = flatten(await self._get_announcements_for_courses(courses))

        async def get_panopto_folders():
            nonlocal course_panopto_folders
            nonlocal courses
            course_panopto_folders = (
                await self._panopto_data_aggregator.get_course_panopto_folders(courses)
            )

        await asyncio.gather(get_mail(), get_announcements(), get_panopto_folders())

        _logger.info(
            "%i courses, %i pages, %i mails, and %i announcements pulled from canvas",
            len(courses),
            len(pages),
            len(mail),
            len(announcements),
        )

        return CanvasDataBundle(
            courses=courses,
            pages=pages,
            messages=mail + announcements,
            course_panopto_folders=course_panopto_folders,
        )

    async def _get_announcements_for_courses(
        self, courses: list[gql.Course]
    ) -> list[Announcement]:
        _logger.info("Fetching announcements for %i courses", len(courses))

        async with CollectingTaskGroup() as tg:
            for course in courses:
                tg.create_task(self._canvas_client.get_announcements(course.q_id))

        return tg.results
