from pathlib import Path
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectin_polymorphic

import qcanvas_backend.database.types as db
from qcanvas_backend.database.data_monolith import DataMonolith
from qcanvas_backend.database.types.canvas_database_types import Base


class QCanvasDatabase:
    def __init__(self, database_file: Path):
        self._engine = create_async_engine(f"sqlite+aiosqlite:///{database_file}")
        self._session_maker = async_sessionmaker(self._engine, expire_on_commit=False)

    @staticmethod
    async def create(database_file: Path) -> "QCanvasDatabase":
        new = QCanvasDatabase(database_file)
        await new.init()
        return new

    async def init(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def session(self):
        # Return type is missing intentionally.
        # Don't try and make this a context manager (which would normally be better) because pycharm still can't
        # determine the type correctly. Blech.
        return self._session_maker.begin()

    async def get_existing_course_ids(self) -> Sequence[str]:
        async with self._session_maker.begin() as session:
            return (await session.scalars(select(db.Course.id))).all()

    async def get_existing_resources(self) -> Sequence[db.Resource]:
        async with self._session_maker.begin() as session:
            stmt = select(db.Resource)
            return (await session.scalars(stmt)).all()

    async def get_resource(self, id: str) -> db.Resource:
        async with self._session_maker.begin() as session:
            stmt = (
                select(db.Resource)
                .where(db.Resource.id == id)
                .options(selectin_polymorphic(db.Resource, [db.PanoptoResource]))
            )
            return (await session.scalars(stmt)).one()

    async def record_resource_downloaded(self, resource: db.Resource):
        await self._update_resource_download_state(
            resource, db.ResourceDownloadState.DOWNLOADED
        )

    async def record_resource_download_failed(
        self, resource: db.Resource, message: str
    ):
        await self._update_resource_download_state(
            resource=resource, message=message, state=db.ResourceDownloadState.FAILED
        )

    async def _update_resource_download_state(
        self,
        resource: db.Resource,
        state: db.ResourceDownloadState,
        message: Optional[str] = None,
    ):
        async with self._session_maker.begin() as session:
            session.add(resource)
            resource.download_state = state
            resource.download_error_message = message

    async def get_data(self) -> DataMonolith:
        async with self.session() as session:
            return await DataMonolith.create(session)
