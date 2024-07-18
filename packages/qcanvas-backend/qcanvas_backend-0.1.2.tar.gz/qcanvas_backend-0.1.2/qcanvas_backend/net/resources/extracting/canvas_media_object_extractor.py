from bs4 import Tag
from qcanvas_api_clients.canvas import CanvasClient

from qcanvas_backend.database import types as db
from qcanvas_backend.net.resources.extracting.link_extractor import LinkExtractor


class CanvasMediaObjectExtractor(LinkExtractor):
    def __init__(self, canvas_client: CanvasClient):
        super().__init__(extractor_id="canvas_media_object", tag_whitelist=["iframe"])
        self._canvas_client = canvas_client

    def _is_tag_valid(self, tag: Tag) -> bool:
        return "data-media-type" in tag.attrs and tag["data-media-type"] == "video"

    def _tag_id(self, tag: Tag) -> str:
        return tag["data-media-id"]

    async def _extract_resource(self, tag: Tag) -> db.Resource:
        media_id = tag["data-media-id"]
        media_info = await self._canvas_client.get_media_object(media_id)
        hq_stream = media_info.media_sources[0]  # Highest quality stream is the first

        return db.Resource(
            file_name=media_info.title,
            url=hq_stream.url,
            file_size=int(hq_stream.size) * 1024,  # Given in KiB, not bytes
        )
