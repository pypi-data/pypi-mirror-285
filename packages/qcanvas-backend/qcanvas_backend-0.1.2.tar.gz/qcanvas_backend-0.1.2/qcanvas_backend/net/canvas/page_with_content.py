from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from qcanvas_backend.gql_queries import Course, Module


@dataclass
class PageWithContent:
    q_id: str
    name: Optional[str]
    updated_at: Optional[datetime]
    created_at: Optional[datetime]
    module: Module
    course: Course
    position: int
    content: Optional[str] = None
