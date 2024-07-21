from .all_courses import DEFINITION as ALL_COURSES_QUERY
from .all_courses import AllCoursesQueryData
from .canvas_course_data import DEFINITION as COURSE_DATA_FRAGMENT
from .canvas_course_data import (
    Assignment,
    AssignmentConnection,
    AssignmentGroup,
    AssignmentGroupConnection,
)
from .canvas_course_data import CanvasCourseData as Course
from .canvas_course_data import (
    File,
    Module,
    ModuleConnection,
    ModuleItem,
    ModuleItemInterface,
    Page,
    Term,
)
from .course_mail import DEFINITION as COURSE_MAIL_QUERY
from .course_mail import ConversationParticipant, CourseMailQueryData
from .single_course import DEFINITION as SINGLE_COURSE_QUERY
from .single_course import SingleCourseQueryData
