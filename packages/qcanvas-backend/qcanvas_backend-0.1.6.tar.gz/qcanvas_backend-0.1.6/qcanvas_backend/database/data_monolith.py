from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectin_polymorphic, selectinload

import qcanvas_backend.database.types as db


class DataMonolith:
    def __init__(
        self,
        courses: Sequence[db.Course],
        resources: Sequence[db.Resource],
        terms: Sequence[db.Term],
    ):
        self.courses = sorted(courses, key=lambda x: x.name)
        self.resources = self._create_resource_map(resources)
        self.terms = terms

    @staticmethod
    def _create_resource_map(resources):
        return {resource.id: resource for resource in resources}

    @staticmethod
    async def create(session: AsyncSession) -> "DataMonolith":
        eager_load_resources = [
            joinedload(db.Resource.course),
            selectin_polymorphic(db.Resource, [db.PanoptoResource]),
        ]
        eager_load_terms = joinedload(db.Term.courses)
        eager_load_courses = [
            selectinload(db.Course.modules).options(
                joinedload(db.Module.course),
                selectinload(db.Module.pages).joinedload(db.ModulePage.module),
            ),
            selectinload(db.Course.resources).options(*eager_load_resources),
            selectinload(db.Course.content_items).options(
                selectin_polymorphic(
                    db.CourseContentItem,
                    [db.ModulePage, db.CourseMessage, db.Assignment],
                ),
                selectinload(db.CourseContentItem.resources),
                selectinload(db.CourseContentItem.dead_resources),
                joinedload(db.CourseContentItem.course),
            ),
            selectinload(db.Course.messages),
            selectinload(db.Course.assignments),
            selectinload(db.Course.configuration).joinedload(
                db.CourseConfiguration.course
            ),
            selectinload(db.Course.term).joinedload(db.Term.courses),
            selectinload(db.Course.assignment_groups).options(
                joinedload(db.AssignmentGroup.course),
                selectinload(db.AssignmentGroup.assignments).joinedload(
                    db.Assignment.group
                ),
            ),
        ]

        query = select(db.Course).options(*eager_load_courses)
        courses = (await session.scalars(query)).all()
        query = select(db.Resource).options(*eager_load_resources)
        resources = (await session.scalars(query)).all()
        query = select(db.Term).options(eager_load_terms)
        terms = (await session.scalars(query)).unique().all()

        return DataMonolith(courses=courses, resources=resources, terms=terms)
