import html
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator

from bs4 import Tag
from httpx import URL
from qcanvas_api_clients.canvas import CanvasClient
from qcanvas_api_clients.panopto import PanoptoClient

from qcanvas_backend.database import types as db
from qcanvas_backend.net.panopto import IFramePanoptoVideoExtractor, video_downloader
from qcanvas_backend.net.resources.download.download_progress import DownloadProgress
from qcanvas_backend.net.resources.extracting.link_extractor import LinkExtractor


# fixme this class is such a fucking mess. please clean it. thanks panopto.


class EmbeddedPanoptoExtractor(LinkExtractor):
    def __init__(self, canvas_client: CanvasClient, panopto_client: PanoptoClient):
        super().__init__("panopto_embedded", ["iframe"])
        self._embedded_video_info_extractor = IFramePanoptoVideoExtractor(canvas_client)
        self._panopto_client = panopto_client

    async def download(
        self, resource: db.Resource, destination: Path
    ) -> AsyncIterator[DownloadProgress]:
        if not isinstance(resource, db.PanoptoResource):
            raise TypeError()

        async for progress in video_downloader.download_video(
            video_id=resource.delivery_id,
            client=self._panopto_client,
            destination=destination,
        ):
            yield progress

    def _is_tag_valid(self, tag: Tag) -> bool:
        if "src" not in tag.attrs:
            return False

        src_raw = tag.attrs["src"]
        src = URL(src_raw)

        if self._is_iframe_embedded_panopto_video(
            src_raw
        ) or self._is_resource_link_lookup_lti_iframe(src_raw):
            return True
        elif self._is_custom_context_lti_iframe(src_raw):
            lti_url = URL(src.params["url"])
            return self._is_custom_context_lti_url(lti_url)
        else:
            return False

    def _tag_id(self, tag: Tag) -> str:
        src_raw = tag.attrs["src"]
        src = URL(src_raw)

        # This might result in resource duplication if somehow there are 2 instances of the same video embedded with
        # both methods, but I REALLY don't care anymore and I want something that at least works.
        # I call it PAINopto for a reason.
        if self._is_iframe_embedded_panopto_video(src_raw):
            return src.params["id"]
        elif self._is_custom_context_lti_iframe(src_raw):
            lti_url = URL(src.params["url"])
            return lti_url.params["custom_context_delivery"]
        elif self._is_resource_link_lookup_lti_iframe(src_raw):
            return src.params["resource_link_lookup_uuid"]
        else:
            raise ValueError(f"Can't tell what type of video it is from the URL: {src}")

    async def _extract_resource(self, tag: Tag) -> db.Resource:
        src_raw = tag.attrs["src"]
        src = URL(src_raw)

        if self._is_iframe_embedded_panopto_video(src_raw):
            delivery_id = src.params["id"]
            video_url = str(src)
        else:
            info = (
                await self._embedded_video_info_extractor.retrieve_embedded_video_info(
                    src
                )
            )
            delivery_id = info.delivery_id
            video_url = info.video_url

        delivery_info = await self._panopto_client.get_session_info(delivery_id)

        return db.PanoptoResource(
            url=video_url,
            delivery_id=delivery_id,
            file_name=delivery_info.name
            + ".mp4",  # All panopto videos are downloaded as mp4s, but doesn't include the extension in the name
            duration_seconds=delivery_info.duration,
            recording_date=datetime.fromisoformat(delivery_info.start_time),
        )

    @staticmethod
    def _is_iframe_embedded_panopto_video(raw_src: str):
        src = URL(raw_src)
        # Check for urls that look like this: https://instance.panopto.com/Panopto/Pages/Embed.aspx?id=123456-1234-124556...
        return src.path.endswith("Embed.aspx") and "id" in src.params

    @staticmethod
    def _is_custom_context_lti_iframe(raw_src: str):
        # The URL is html encoded because it is from an iframe
        src = URL(html.unescape(raw_src))

        def _remove_empty(string: str) -> bool:
            return len(string) > 1

        path = list(filter(_remove_empty, src.path.split("/", 4)))

        # Check the URL path https://canvas_instance/courses/12345/external_tools?url=whatever.panopto.com/?custom_context_delivery=... (encoded)
        #                                                          ^^^^^^^^^^^^^^
        # Also check that "url" parameter is supplied
        return len(path) >= 3 and path[2] == "external_tools" and "url" in src.params

    @staticmethod
    def _is_resource_link_lookup_lti_iframe(raw_src: str):
        # The URL is html encoded because it is from an iframe
        src = URL(html.unescape(raw_src))

        def _remove_empty(string: str) -> bool:
            return len(string) > 1

        path = list(filter(_remove_empty, src.path.split("/", 4)))

        # Check the URL path https://canvas_instance/courses/12345/external_tools/retrieve?resource_link_lookup_uuid=...
        #                                                          ^^^^^^^^^^^^^^
        # Also check that "url" parameter is supplied
        return (
            len(path) >= 3
            and path[2] == "external_tools"
            and "resource_link_lookup_uuid" in src.params
        )

    @staticmethod
    def _is_custom_context_lti_url(lti_url: URL) -> bool:
        # Check for urls that look like this:
        # https://instance.panopto.com/Panopto/LTI/LTI.aspx?custom_context_delivery=12345-1234567-13454...
        return (
            "panopto.com" in lti_url.host
            and "custom_context_delivery" in lti_url.params
        )
