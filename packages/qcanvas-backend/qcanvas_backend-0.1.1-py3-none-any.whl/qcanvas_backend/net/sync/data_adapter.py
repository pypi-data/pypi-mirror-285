import logging

from qcanvas_api_clients.canvas import Announcement

import qcanvas_backend.gql_queries as gql
from qcanvas_backend.net.canvas import CourseMailItem, PageWithContent
from qcanvas_backend.net.sync._internal.canvas_data_bundle import CanvasDataBundle
from qcanvas_backend.net.sync.api_data_importer import APIDataImporter

_logger = logging.getLogger(__name__)


class DataAdapter:
    """
    A DataAdapter deeply iterates over everything in a CanvasDataBundle and adds this data to the database using an APIDataImporter
    """

    def __init__(self, importer: APIDataImporter):
        self._converter = importer

    async def convert_and_add_to_database(self, canvas_sync_data: CanvasDataBundle):
        await self._store_partial_course_data(
            courses=canvas_sync_data.courses,
            course_panopto_folders=canvas_sync_data.course_panopto_folders,
        )
        await self._store_pages(canvas_sync_data.pages)
        await self._store_messages(
            canvas_sync_data.messages,
            known_course_ids=[course.q_id for course in canvas_sync_data.courses],
        )

    async def _store_partial_course_data(
        self, courses: list[gql.Course], course_panopto_folders: dict[str, str]
    ):
        for term in self._flatten_terms(courses):
            await self._converter.convert_and_store_term(term)

        for course in courses:
            await self._converter.convert_and_store_course(
                course=course,
                panopto_folder_id=course_panopto_folders.get(course.q_id, None),
            )

            for position, module in enumerate(course.modules_connection.nodes):
                await self._converter.convert_and_store_module(
                    module=module, course_id=course.q_id, position=position
                )

            for position, assignment_group in enumerate(
                course.assignment_groups_connection.nodes
            ):
                if self._assignment_group_is_empty(assignment_group):
                    continue

                await self._converter.convert_and_store_assignment_group(
                    assignment_group=assignment_group,
                    course_id=course.q_id,
                    position=position,
                )

                for assignment in assignment_group.assignments_connection.nodes:
                    await self._converter.convert_and_store_assignment(
                        assignment=assignment, group_id=assignment_group.q_id
                    )

    @staticmethod
    def _assignment_group_is_empty(assignment_group: gql.AssignmentGroup) -> bool:
        return len(assignment_group.assignments_connection.nodes) == 0

    @staticmethod
    def _flatten_terms(courses: list[gql.Course]) -> list[gql.Term]:
        term_id_map: dict[str, gql.Term] = {}

        for course in courses:
            term_id_map[course.term.q_id] = course.term

        return list(term_id_map.values())

    async def _store_pages(self, pages: list[PageWithContent]):
        for page in pages:
            await self._converter.convert_and_store_page(page)

    async def _store_messages(
        self, messages: list[CourseMailItem | Announcement], known_course_ids: list[str]
    ):
        for message in messages:
            if isinstance(message, CourseMailItem):
                # Canvas includes mail for information "courses", but they're not visible in the allCourses graphql item.
                # Since they are not indexed anywhere else, we will discard them here
                if message.course_id in known_course_ids:
                    await self._converter.convert_and_store_mail_item(message)
                else:
                    _logger.debug(
                        'Discarding mail item "%s" (id="%s") because it\'s from an un-indexed course (id="%s")',
                        message.subject,
                        message.id,
                        message.course_id,
                    )
            elif isinstance(message, Announcement):
                await self._converter.convert_and_store_announcement(message)
