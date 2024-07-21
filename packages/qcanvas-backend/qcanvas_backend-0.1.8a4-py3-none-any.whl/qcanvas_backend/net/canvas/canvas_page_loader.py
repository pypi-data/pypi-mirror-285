import logging
from asyncio import TaskGroup
from datetime import datetime

from qcanvas_api_clients.canvas import CanvasClient

from qcanvas_backend.gql_queries import Course, Module, ModuleItem, Page
from qcanvas_backend.net.canvas.page_with_content import PageWithContent
from qcanvas_backend.util import strip_tz

_logger = logging.getLogger(__name__)


class CanvasPageLoader:

    def __init__(self, canvas_client: CanvasClient):
        self._canvas_client = canvas_client

    async def load_all_updated_page_content(
        self, courses: list[Course], last_update_time: datetime
    ) -> list[PageWithContent]:
        flattened_page_list = self._get_outdated_page_list(
            courses=courses, last_update_time=last_update_time
        )

        _logger.info("Loading %i pages", len(flattened_page_list))

        async with TaskGroup() as tg:
            for page in flattened_page_list:
                _logger.debug(
                    '%s "%s" (id="%s") out of date',
                    type(page).__name__,
                    page.name,
                    page.q_id,
                )
                tg.create_task(self._load_page_content_inplace(page))

        return flattened_page_list

    def _get_outdated_page_list(
        self, courses: list[Course], last_update_time: datetime
    ) -> list[PageWithContent]:
        pages = []

        for course in courses:
            for module in course.modules_connection.nodes:
                for position, module_item in enumerate(module.module_items):
                    if isinstance(module_item.content, Page):
                        if self._is_module_item_out_of_date(
                            last_update_time, module_item
                        ):
                            pages.append(
                                self._convert_to_page_with_content(
                                    page=module_item.content,
                                    module=module,
                                    course=course,
                                    position=position,
                                )
                            )

        return pages

    @staticmethod
    def _is_module_item_out_of_date(
        last_update_time: datetime, module_item: ModuleItem
    ) -> bool:
        return strip_tz(module_item.content.updated_at) >= last_update_time

    @staticmethod
    def _convert_to_page_with_content(
        page: Page, module: Module, course: Course, position: int
    ):
        return PageWithContent(
            q_id=page.q_id,
            name=page.title,
            updated_at=page.updated_at,
            created_at=page.created_at,
            module=module,
            course=course,
            position=position,
        )

    async def _load_page_content_inplace(self, page: PageWithContent):
        result = await self._canvas_client.get_page(
            page_id=page.q_id, course_id=page.course.q_id
        )
        _logger.debug('Loaded page %s (id="%s")', page.name, page.q_id)
        page.content = result.body
