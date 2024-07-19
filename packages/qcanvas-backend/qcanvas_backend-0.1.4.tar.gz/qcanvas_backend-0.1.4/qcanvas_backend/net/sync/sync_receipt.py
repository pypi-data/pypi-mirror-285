from dataclasses import dataclass, field

import qcanvas_backend.database.types as db
from qcanvas_backend.net.sync._internal.canvas_sync_observer import CanvasSyncObserver


@dataclass
class SyncReceipt(CanvasSyncObserver):
    updated_courses: set[str] = field(default_factory=set)
    updated_modules: set[str] = field(default_factory=set)
    updated_pages: set[str] = field(default_factory=set)
    updated_assignment_groups: set[str] = field(default_factory=set)
    updated_assignments: set[str] = field(default_factory=set)
    updated_resources: set[str] = field(default_factory=set)
    updated_messages: set[str | int] = field(default_factory=set)

    def new_content_found(self, content: object):
        if isinstance(content, db.Course):
            self.updated_courses.add(content.id)
        elif isinstance(content, db.Module):
            self.updated_modules.add(content.id)
        elif isinstance(content, db.ModulePage):
            self.updated_pages.add(content.id)
            self.updated_courses.add(content.course_id)
            self.updated_modules.add(content.module_id)
        elif isinstance(content, db.CourseMessage):
            self.updated_messages.add(content.id)
            self.updated_courses.add(content.course_id)
        elif isinstance(content, db.AssignmentGroup):
            self.updated_assignment_groups.add(content.id)
        elif isinstance(content, db.Assignment):
            self.updated_assignments.add(content.id)
            self.updated_assignment_groups.add(content.group_id)
            self.updated_courses.add(content.course_id)
        elif isinstance(content, db.Resource):
            self.updated_resources.add(content.id)
            self.updated_courses.add(content.course_id)
