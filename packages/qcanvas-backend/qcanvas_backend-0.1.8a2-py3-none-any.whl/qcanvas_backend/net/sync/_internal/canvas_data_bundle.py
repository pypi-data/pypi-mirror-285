from dataclasses import dataclass
from typing import List

from qcanvas_api_clients.canvas import Announcement

from qcanvas_backend.gql_queries import Course
from qcanvas_backend.net.canvas import CourseMailItem, PageWithContent


@dataclass
class CanvasDataBundle:
    """
    A CanvasDataBundle is a collection of various data retrieved from canvas
    """

    courses: List[Course]
    pages: List[PageWithContent]
    messages: List[CourseMailItem | Announcement]
    course_panopto_folders: dict[str, str]
