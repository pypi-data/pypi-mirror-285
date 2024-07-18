import qcanvas_backend.database.types as db
from qcanvas_backend.net.sync._internal.canvas_sync_observer import CanvasSyncObserver


class NewContentObserver(CanvasSyncObserver):
    def __init__(self):
        super().__init__()
        self._new_content: list[db.CourseContentItem] = []

    def new_content_found(self, content: object):
        if isinstance(content, db.CourseContentItem):
            self._new_content.append(content)

    @property
    def new_content(self) -> list[db.CourseContentItem]:
        return self._new_content
