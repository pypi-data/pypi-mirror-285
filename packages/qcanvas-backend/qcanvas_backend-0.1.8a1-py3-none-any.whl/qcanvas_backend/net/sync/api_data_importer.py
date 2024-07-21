import logging
from typing import Any

import qcanvas_api_clients.canvas as canvas
from sqlalchemy.ext.asyncio import AsyncSession

import qcanvas_backend.database.types as db
import qcanvas_backend.gql_queries as gql
from qcanvas_backend.database.types import ModulePageType
from qcanvas_backend.net.canvas import CourseMailItem, PageWithContent
from qcanvas_backend.net.sync._internal.canvas_sync_observer import CanvasSyncObservable
from qcanvas_backend.util import remove_unwanted_whitespaces, strip_tz

_logger = logging.getLogger(__name__)


class APIDataImporter(CanvasSyncObservable):
    """
    An APIDataImporter accepts canvas API objects and converts and adds them to the database
    """

    _type_map = {
        gql.Course: db.Course,
        gql.Term: db.Term,
        gql.Module: db.Module,
        gql.Assignment: db.Assignment,
        gql.AssignmentGroup: db.AssignmentGroup,
        gql.File: db.ModulePage,
        PageWithContent: db.ModulePage,
        CourseMailItem: db.CourseMessage,
        canvas.Announcement: db.CourseMessage,
    }

    @staticmethod
    def _id_from_api_object(obj: Any) -> str | int:
        if isinstance(obj, (canvas.Announcement, CourseMailItem)):
            return obj.id
        elif hasattr(obj, "q_id"):
            return obj.q_id
        else:
            raise TypeError(f"{type(obj)} can not be handled")

    def __init__(self, session: AsyncSession):
        super().__init__()
        self._session = session

    async def convert_and_store_course(
        self, course: gql.Course, panopto_folder_id: str | None
    ):
        db_course: db.Course = await self._find_or_create_db_entry(course)
        is_new = self._is_record_new(db_course)

        db_course.id = course.q_id
        db_course.name = remove_unwanted_whitespaces(course.name)
        db_course.term_id = course.term.q_id

        if panopto_folder_id is not None:
            db_course.panopto_folder_id = panopto_folder_id

        if is_new:
            db_course.configuration = db.CourseConfiguration()
            self.notify_observers_for_updated_item(db_course)

    async def convert_and_store_module(
        self, module: gql.Module, course_id: str, position: int
    ):
        db_module: db.Module = await self._find_or_create_db_entry(module)

        is_new = self._is_record_new(db_module)

        db_module.id = module.q_id
        db_module.name = module.name
        db_module.course_id = course_id
        db_module.position = position

        if is_new:
            self.notify_observers_for_updated_item(db_module)

    async def convert_and_store_page(self, page: PageWithContent):
        db_page: db.ModulePage = await self._find_or_create_db_entry(page)

        if not (self._is_record_new_or_updated(db_object=db_page, api_object=page)):
            # Updating the record is not going to do anything
            return

        db_page.id = page.q_id
        db_page.course_id = page.course.q_id
        db_page.module_id = page.module.q_id
        db_page.name = remove_unwanted_whitespaces(page.name)
        db_page.body = remove_unwanted_whitespaces(page.content)
        db_page.creation_date = page.created_at
        db_page.last_modification_date = page.updated_at
        db_page.position = page.position
        db_page.page_type = ModulePageType.PAGE

        self.notify_observers_for_updated_item(db_page)

    async def convert_and_store_term(self, term: gql.Term):
        db_term: db.Term = await self._find_or_create_db_entry(term)

        is_new = self._is_record_new(db_term)

        db_term.id = term.q_id
        db_term.end_date = term.end_at
        db_term.start_date = term.start_at
        db_term.name = remove_unwanted_whitespaces(term.name)

        if is_new:
            self.notify_observers_for_updated_item(db_term)

    async def convert_and_store_assignment_group(
        self, assignment_group: gql.AssignmentGroup, course_id: str, position: int
    ):
        db_group: db.AssignmentGroup = await self._find_or_create_db_entry(
            assignment_group
        )

        is_new = self._is_record_new(db_group)

        db_group.id = assignment_group.q_id
        db_group.name = remove_unwanted_whitespaces(assignment_group.name)
        db_group.course_id = course_id
        db_group.group_weight = assignment_group.group_weight
        db_group.position = position

        if is_new:
            self.notify_observers_for_updated_item(db_group)

    async def convert_and_store_assignment(
        self, assignment: gql.Assignment, group_id: str
    ):
        db_assignment: db.Assignment = await self._find_or_create_db_entry(assignment)

        # todo the assignment submission object also has an updated date now, I'm not sure if we need to check both
        #  that, as well as the assignment's modify date?
        if not (
            self._is_record_new_or_updated(
                db_object=db_assignment, api_object=assignment
            )
        ):
            # Updating the record is not going to do anything
            return

        db_assignment.id = assignment.q_id
        db_assignment.course_id = assignment.course_id
        db_assignment.name = remove_unwanted_whitespaces(assignment.name)
        db_assignment.body = remove_unwanted_whitespaces(assignment.description)
        db_assignment.creation_date = assignment.created_at
        db_assignment.last_modification_date = assignment.updated_at
        db_assignment.due_date = assignment.due_at
        db_assignment.position = assignment.position
        db_assignment.group_id = group_id
        db_assignment.max_mark_possible = assignment.points_possible
        db_assignment.mark = self._get_assignment_mark(assignment)

        self.notify_observers_for_updated_item(db_assignment)

    @staticmethod
    def _get_assignment_mark(assignment: gql.Assignment) -> float | None:
        if assignment.submissions_connection is not None:
            submissions = assignment.submissions_connection.nodes
            if len(submissions) > 1:
                _logger.warning(
                    "Assignment %s has multiple submissions, expected only 1",
                    assignment.q_id,
                )

            if len(submissions) >= 1:
                return submissions[0].score

        return None

    async def convert_and_store_announcement(self, announcement: canvas.Announcement):
        db_message: db.CourseMessage = await self._find_or_create_db_entry(announcement)

        # Canvas doesn't seem to track last modification date on announcements for some reason
        # Otherwise, I would check for modification time here
        is_new = self._is_record_new(db_message)

        db_message.id = str(announcement.id)
        db_message.course_id = announcement.course_id
        db_message.creation_date = announcement.created_at
        db_message.name = remove_unwanted_whitespaces(announcement.title)
        db_message.body = remove_unwanted_whitespaces(announcement.message)
        db_message.sender_name = announcement.user_name
        db_message.has_been_read = False

        if is_new:
            self.notify_observers_for_updated_item(db_message)

    async def convert_and_store_mail_item(self, mail: CourseMailItem):
        db_message: db.CourseMessage = await self._find_or_create_db_entry(mail)

        is_new = self._is_record_new(db_message)

        db_message.id = mail.id
        db_message.course_id = mail.course_id
        db_message.creation_date = mail.date
        db_message.name = remove_unwanted_whitespaces(mail.subject)
        db_message.body = self._convert_plaintext_to_html(
            remove_unwanted_whitespaces(mail.body)
        )
        db_message.sender_name = mail.author_name
        db_message.has_been_read = False

        if is_new:
            self.notify_observers_for_updated_item(db_message)

    def _convert_plaintext_to_html(self, plaintext: str) -> str:
        return plaintext.replace("\n", "<br/>\n")

    async def _find_or_create_db_entry(self, obj: Any):
        obj_type = type(obj)

        if obj_type not in self._type_map.keys():
            raise TypeError(f"{obj_type} is not present in _type_map")

        obj_id = self._id_from_api_object(obj)
        db_type = self._type_map[obj_type]
        db_object = await self._session.get(db_type, obj_id)

        if db_object is None:
            _logger.debug(
                'Converting new %s (api) to %s (db) (id="%s")',
                obj_type.__name__,
                db_type.__name__,
                obj_id,
            )
            db_object = db_type()
            self._session.add(db_object)
        else:
            _logger.debug(
                'Found existing %s (db) for %s (api) (id="%s")',
                db_type.__name__,
                obj_type.__name__,
                obj_id,
            )

        return db_object

    @staticmethod
    def _is_record_new_or_updated(
        db_object: Any | db.ModificationDate, api_object: Any
    ):
        if APIDataImporter._is_record_new(db_object):
            return True
        elif hasattr(api_object, "updated_at") and isinstance(
            db_object, db.ModificationDate
        ):
            return db_object.last_modification_date < strip_tz(api_object.updated_at)
        else:
            return False

    @staticmethod
    def _is_record_new(db_obj: Any):
        return db_obj.id is None
