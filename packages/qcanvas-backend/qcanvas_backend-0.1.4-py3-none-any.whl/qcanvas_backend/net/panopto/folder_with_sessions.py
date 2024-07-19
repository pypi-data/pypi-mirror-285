from dataclasses import dataclass

from qcanvas_api_clients.panopto import FolderInfo, Session


@dataclass
class FolderWithSessions:
    folder: FolderInfo
    sessions: list[Session]
