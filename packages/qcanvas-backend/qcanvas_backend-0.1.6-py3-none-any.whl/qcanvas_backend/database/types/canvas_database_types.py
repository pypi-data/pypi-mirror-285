from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

from qcanvas_backend.database.types.course_page_grouping_policy import (
    CourseFileGroupingPolicy,
)
from qcanvas_backend.database.types.module_page_type import ModulePageType
from qcanvas_backend.database.types.resource_download_state import ResourceDownloadState
from qcanvas_backend.database.types.resource_life_state import ResourceLinkState


class ModificationDate:
    last_modification_date: Mapped[datetime]


class Base(DeclarativeBase, MappedAsDataclass, init=False):
    pass


class ResourceLink(Base, init=True):
    __tablename__ = "resource_links"

    # Do not reorder these (it will mess up the key tuple)!! content_item_id, then resource_id
    content_item_id: Mapped[str] = mapped_column(
        ForeignKey("course_content.id"), primary_key=True
    )
    resource_id: Mapped[str] = mapped_column(
        ForeignKey("resources.id"), primary_key=True
    )
    link_state: Mapped[ResourceLinkState] = mapped_column(
        default=ResourceLinkState.ACTIVE
    )


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[str] = mapped_column(primary_key=True)

    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"))
    course: Mapped["Course"] = relationship(back_populates="resources")

    url: Mapped[str]
    file_name: Mapped[str]
    file_size: Mapped[Optional[int]] = mapped_column(default=None)
    discovery_date: Mapped[datetime]
    download_state: Mapped[ResourceDownloadState] = mapped_column(
        default=ResourceDownloadState.NOT_DOWNLOADED
    )
    download_error_message: Mapped[Optional[str]] = mapped_column(default=None)

    polymorphic_type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_on": "polymorphic_type",
        "polymorphic_identity": "resource",
    }


class CourseContentItem(Base):
    __tablename__ = "course_content"

    id: Mapped[str] = mapped_column(primary_key=True)

    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"))
    course: Mapped["Course"] = relationship(back_populates="content_items")

    name: Mapped[str]
    body: Mapped[Optional[str]]
    creation_date: Mapped[datetime]
    polymorphic_type: Mapped[str]

    resources: Mapped[List["Resource"]] = relationship(
        secondary=ResourceLink.__table__,
        primaryjoin=f"and_(ResourceLink.content_item_id == CourseContentItem.id, ResourceLink.link_state=='{ResourceLinkState.ACTIVE.name}')",
        overlaps="dead_resources, course_content",
        order_by=Resource.discovery_date,
    )
    dead_resources: Mapped[List["Resource"]] = relationship(
        secondary=ResourceLink.__table__,
        primaryjoin=f"and_(ResourceLink.content_item_id == CourseContentItem.id, ResourceLink.link_state=='{ResourceLinkState.RESIDUAL.name}')",
        overlaps="resources, course_content",
        order_by=Resource.discovery_date,
    )

    __mapper_args__ = {
        "polymorphic_on": "polymorphic_type",
        "polymorphic_identity": "generic_content",
    }


class CourseConfiguration(Base):
    __tablename__ = "course_configuration"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"))
    course: Mapped["Course"] = relationship(
        back_populates="configuration", single_parent=True
    )

    nickname: Mapped[Optional[str]] = mapped_column(default=None)
    file_grouping_policy: Mapped[CourseFileGroupingPolicy] = mapped_column(
        default=CourseFileGroupingPolicy.GROUP_BY_PAGES
    )


class PanoptoResource(Resource):
    __tablename__ = "panopto_resources"

    id: Mapped[str] = mapped_column(ForeignKey("resources.id"), primary_key=True)

    duration_seconds: Mapped[int]
    recording_date: Mapped[datetime]

    # Panopto/Canvas have this stupid "custom_context_delivery" which is a pain in the ass because it has nothing to do
    # with the actual ID of the video. In this case, this object's id may not be useful in any way (thanks painopto),
    # but delivery_id will always be the true ID of the video.
    # !!!! It has been observed that different "custom_context_delivery"s CAN link to the same video !!!!
    delivery_id: Mapped[str]

    __mapper_args__ = {"polymorphic_identity": "panopto_resource"}


class Assignment(CourseContentItem, ModificationDate):
    __tablename__ = "assignments"

    id: Mapped[str] = mapped_column(ForeignKey("course_content.id"), primary_key=True)

    due_date: Mapped[Optional[datetime]]
    mark: Mapped[Optional[float]]
    max_mark_possible: Mapped[Optional[float]]
    position: Mapped[int]

    group_id: Mapped[str] = mapped_column(ForeignKey("assignment_groups.id"))
    group: Mapped["AssignmentGroup"] = relationship(back_populates="assignments")

    __mapper_args__ = {"polymorphic_identity": "assignment"}


class AssignmentGroup(Base):
    __tablename__ = "assignment_groups"

    id: Mapped[str] = mapped_column(primary_key=True)

    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"))
    course: Mapped["Course"] = relationship(back_populates="assignment_groups")

    name: Mapped[str]
    assignments: Mapped[List["Assignment"]] = relationship(
        back_populates="group",
        order_by=Assignment.position,
        cascade="save-update, merge, delete",
    )
    group_weight: Mapped[int]
    position: Mapped[int]


class CourseMessage(CourseContentItem):
    """
    Used for announcements and course mail
    """

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(ForeignKey("course_content.id"), primary_key=True)

    sender_name: Mapped[str]
    has_been_read: Mapped[bool]

    __mapper_args__ = {"polymorphic_identity": "message"}


class ModulePage(CourseContentItem, ModificationDate):
    __tablename__ = "pages"

    id: Mapped[str] = mapped_column(ForeignKey("course_content.id"), primary_key=True)

    module_id: Mapped[str] = mapped_column(ForeignKey("modules.id"))
    module: Mapped["Module"] = relationship(back_populates="pages")
    position: Mapped[int]

    page_type: Mapped[ModulePageType]

    __mapper_args__ = {"polymorphic_identity": "page"}


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[str] = mapped_column(primary_key=True)

    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"))
    course: Mapped["Course"] = relationship(back_populates="modules")

    name: Mapped[str]
    pages: Mapped[List["ModulePage"]] = relationship(
        back_populates="module",
        order_by=ModulePage.position,
        cascade="save-update, merge, delete",
    )
    position: Mapped[int]


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(primary_key=True)

    name: Mapped[str]
    configuration: Mapped["CourseConfiguration"] = relationship(
        back_populates="course", cascade="save-update, merge, delete"
    )
    resources: Mapped[List["Resource"]] = relationship(
        back_populates="course",
        order_by=Resource.discovery_date,
        cascade="save-update, merge, delete",
    )
    modules: Mapped[List["Module"]] = relationship(
        back_populates="course",
        order_by=Module.position,
        cascade="save-update, merge, delete",
    )
    assignment_groups: Mapped[List["AssignmentGroup"]] = relationship(
        back_populates="course",
        order_by=AssignmentGroup.position,
        cascade="save-update, merge, delete",
    )
    content_items: Mapped[List["CourseContentItem"]] = relationship(
        back_populates="course",
        order_by=CourseContentItem.creation_date,
        cascade="save-update, merge, delete",
    )
    messages: Mapped[List["CourseMessage"]] = relationship(
        viewonly=True,
        primaryjoin=id == CourseMessage.course_id,
        order_by=CourseMessage.creation_date,
    )
    assignments: Mapped[List["Assignment"]] = relationship(
        viewonly=True,
        primaryjoin=id == Assignment.course_id,
        order_by=Assignment.due_date,
    )
    panopto_folder_id: Mapped[Optional[str]]
    term_id: Mapped[str] = mapped_column(ForeignKey("terms.id"))
    term: Mapped["Term"] = relationship(back_populates="courses")


class Term(Base):
    __tablename__ = "terms"

    id: Mapped[str] = mapped_column(primary_key=True)

    start_date: Mapped[Optional[datetime]]
    end_date: Mapped[Optional[datetime]]
    name: Mapped[str]
    courses: Mapped[List["Course"]] = relationship(
        back_populates="term",
        order_by=Course.name,
        cascade="save-update, merge, delete",
    )

    def __hash__(self):
        return (
            hash(self.id)
            ^ hash(self.start_date)
            ^ hash(self.end_date)
            ^ hash(self.name)
        )
