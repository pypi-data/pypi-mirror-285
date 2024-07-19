from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import qcanvas_backend.database.types as db
from qcanvas_backend.net.resources.scanning.page_resources import PageResources
from qcanvas_backend.net.sync._internal.canvas_sync_observer import CanvasSyncObservable


class ResourceLinker(CanvasSyncObservable):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self._session = session

    async def link_resources(self, page_resources_pairs: list[PageResources]):
        if len(page_resources_pairs) == 0:
            return

        page_ids = [pair.page_id for pair in page_resources_pairs]

        await self._mark_links_as_dead_for_pages(page_ids)
        await self._link_new_resources_and_restore_active_links(page_resources_pairs)

    async def _mark_links_as_dead_for_pages(self, page_ids: list[str]):
        await self._session.execute(
            update(db.ResourceLink)
            .where(db.ResourceLink.content_item_id.in_(page_ids))
            .values(link_state=db.ResourceLinkState.RESIDUAL)
        )

    async def _link_new_resources_and_restore_active_links(
        self, page_resources_pairs: list[PageResources]
    ):
        for pair in page_resources_pairs:
            page_id = pair.page_id
            existing_resource_links = await self._existing_page_resource_links(page_id)
            newly_linked_resources: list[str] = []

            await self._create_links_for_resources(
                existing_resource_links=existing_resource_links,
                page_resource_pair=pair,
                newly_linked_resources=newly_linked_resources,
            )

            await self._create_links_for_invisible_resources(
                existing_resource_links=existing_resource_links,
                page_resource_pair=pair,
                newly_linked_resources=newly_linked_resources,
            )

    async def _create_links_for_resources(
        self,
        existing_resource_links: Sequence[str],
        page_resource_pair: PageResources,
        newly_linked_resources: list[str],
    ):
        page_id = page_resource_pair.page_id

        for resource in page_resource_pair.resources:
            if resource.id in existing_resource_links:
                # If a resource is still linked on this page, reactivate the link
                await self._reactivate_existing_resource_link(
                    page_id=page_id, resource=resource
                )
                continue
            elif resource.id in newly_linked_resources:
                # Prevent adding duplicate links (duplicate links have been observed on some pages)
                continue

            self._create_resource_link(page_id=page_id, resource=resource)
            newly_linked_resources.append(resource.id)

            await self._add_resource_to_db_if_new(resource)

    async def _create_links_for_invisible_resources(
        self,
        existing_resource_links: Sequence[str],
        page_resource_pair: PageResources,
        newly_linked_resources: list[str],
    ):
        page_id = page_resource_pair.page_id

        for resource in page_resource_pair.invisible_resources:
            if (
                resource.id in existing_resource_links
                or resource.id in newly_linked_resources
            ):
                # If the resource was already on the page, or it has just been added, don't add it again
                continue

            self._create_dead_resource_link(page_id=page_id, resource=resource)
            newly_linked_resources.append(resource.id)
            await self._add_resource_to_db_if_new(resource)

    def _create_resource_link(self, page_id: str, resource: db.Resource):
        self._session.add(
            db.ResourceLink(content_item_id=page_id, resource_id=resource.id)
        )

    def _create_dead_resource_link(self, page_id: str, resource: db.Resource):
        link = db.ResourceLink(
            content_item_id=page_id,
            resource_id=resource.id,
            link_state=db.ResourceLinkState.RESIDUAL,
        )
        link.link_state = db.ResourceLinkState.RESIDUAL
        self._session.add(link)

    async def _existing_page_resource_links(self, page_id: str) -> Sequence[str]:
        return (
            await self._session.scalars(
                select(db.ResourceLink.resource_id).where(
                    db.ResourceLink.content_item_id == page_id
                )
            )
        ).all()

    async def _reactivate_existing_resource_link(
        self, page_id: str, resource: db.Resource
    ):
        existing = await self._session.get_one(db.ResourceLink, (page_id, resource.id))
        existing.link_state = db.ResourceLinkState.ACTIVE

    async def _add_resource_to_db_if_new(self, resource: db.Resource):
        does_not_exist = (await self._session.get(db.Resource, resource.id)) is None

        if does_not_exist:
            self._session.add(resource)
            self.notify_observers_for_updated_item(resource)
