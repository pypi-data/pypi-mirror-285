from datetime import datetime
from pathlib import Path

from stones import LmdbStore, stone


class SyncMeta:
    def __init__(self, stone_path: Path):
        self._db = stone(str(stone_path.absolute()), LmdbStore)

    @property
    def last_sync_time(self) -> datetime:
        return self._db.get("last", datetime.min)

    def update_last_sync_time(self):
        self._db["last"] = datetime.now()
