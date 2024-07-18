import logging
from typing import Sequence

from gql import gql
from qcanvas_api_clients.canvas import CanvasClient
from qcanvas_api_clients.util import cachedasyncmethod_for_development
from shelved_cache.keys import autotuple_hashkey

from qcanvas_backend import gql_queries
from qcanvas_backend.gql_queries import (
    AllCoursesQueryData,
    ConversationParticipant,
    Course,
    CourseMailQueryData,
    Term,
)
from qcanvas_backend.net.canvas.course_mail_item import CourseMailItem
from qcanvas_backend.util import CollectingTaskGroup

_logger = logging.getLogger(__name__)


class CanvasDataAggregator:
    def __init__(self, canvas_client: CanvasClient):
        self._canvas_client = canvas_client

    async def pull_user_id(self) -> str:
        return await self._canvas_client.get_current_user_id()

    @cachedasyncmethod_for_development(key=autotuple_hashkey)
    async def get_all_course_mail(self, current_user_id: str) -> list[CourseMailItem]:
        _logger.info("Fetching all course mail")

        result = await self._gql_query(
            gql_queries.COURSE_MAIL_QUERY, user_id=current_user_id
        )

        raw_mail_data = CourseMailQueryData(
            **result
        ).legacy_node.conversations_connection.nodes

        return self._convert_mail(raw_mail_data)

    @staticmethod
    def _convert_mail(
        raw_mail_data: list[ConversationParticipant],
    ):
        return [CourseMailItem.from_query_result(mail) for mail in raw_mail_data]

    @cachedasyncmethod_for_development(key=autotuple_hashkey)
    async def pull_new_and_latest_courses(
        self, already_indexed_course_ids: Sequence[str]
    ) -> list[Course]:
        shallow_courses = await self._get_shallow_course_data()
        shallow_courses = self._ignore_blackboard_courses(shallow_courses)
        latest_term = self._find_latest_term(shallow_courses)

        course_ids_to_pull = [
            course.q_id
            for course in shallow_courses
            if self._course_belongs_to_term(course, latest_term)
            or course.q_id not in already_indexed_course_ids
        ]

        return await self._pull_detailed_courses_by_id(course_ids_to_pull)

    @staticmethod
    def _course_belongs_to_term(course: Course, term: Term) -> bool:
        return course.term.q_id == term.q_id

    async def _get_shallow_course_data(self) -> list[Course]:
        result = await self._gql_query(gql_queries.ALL_COURSES_QUERY, detailed=False)

        return AllCoursesQueryData(**result).all_courses

    @staticmethod
    def _ignore_blackboard_courses(course_list: list[Course]) -> list[Course]:
        return [course for course in course_list if course.term.start_at.year >= 2022]

    async def _pull_detailed_courses_by_id(self, course_ids: list[str]) -> list[Course]:
        _logger.info("Fetching index for course ids %s", ", ".join(course_ids))

        async with CollectingTaskGroup() as tg:
            for course_id in course_ids:
                tg.create_task(
                    self._gql_query(
                        gql_queries.SINGLE_COURSE_QUERY,
                        course_id=course_id,
                        detailed=True,
                    )
                )

        return self._convert_courses(tg.results)

    async def _gql_query(self, query: str, **kwargs):
        return await self._canvas_client.graphql_query(gql(query), kwargs)

    @staticmethod
    def _convert_courses(results: list[dict]) -> list[Course]:
        return [
            gql_queries.SingleCourseQueryData(**task_result).course
            for task_result in results
        ]

    @staticmethod
    def _find_latest_term(courses: list[Course]) -> Term:
        terms = [course.term for course in courses if course.term is not None]
        sorted_terms = sorted(terms, key=lambda term: term.end_at)

        return sorted_terms[-1]
