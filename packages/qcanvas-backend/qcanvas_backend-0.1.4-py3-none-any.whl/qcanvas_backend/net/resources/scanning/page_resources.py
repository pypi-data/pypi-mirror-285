from dataclasses import dataclass

import qcanvas_backend.database.types as db


@dataclass
class PageResources:
    page_id: str
    resources: list[db.Resource]
    invisible_resources: list[db.Resource]
