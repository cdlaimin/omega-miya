"""
@Author         : Ailitonia
@Date           : 2022/08/20 18:47
@FileName       : yandex.py
@Project        : nonebot2_miya 
@Description    : yandex 识图引擎
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm 
"""

from typing import TYPE_CHECKING

from lxml import etree
from nonebot.log import logger

from src.compat import parse_obj_as
from ..model import BaseImageSearcherAPI, ImageSearchingResult

if TYPE_CHECKING:
    from nonebot.internal.driver import CookieTypes, HeaderTypes


class Yandex(BaseImageSearcherAPI):
    """yandex 识图引擎

    [Deactivated]页面改版, 图片搜索内容不可靠, 放弃维护
    """

    @classmethod
    def _get_root_url(cls, *args, **kwargs) -> str:
        return 'https://yandex.com'

    @classmethod
    async def _async_get_root_url(cls, *args, **kwargs) -> str:
        return cls._get_root_url(*args, **kwargs)

    @classmethod
    def _get_default_headers(cls) -> "HeaderTypes":
        headers = cls._get_omega_requests_default_headers()
        headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                      'image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Host': 'yandex.com',
            'Origin': 'https://yandex.com/images',
            'Referer': 'https://yandex.com/images/'
        })
        return headers

    @classmethod
    def _get_default_cookies(cls) -> "CookieTypes":
        return None

    @property
    def api_url(self) -> str:
        return f'{self._get_root_url()}/images/search'

    @staticmethod
    def _parser(content: str) -> list[dict]:
        """解析结果页面"""
        html = etree.HTML(content)
        # 定位到相似图片区域
        container = html.xpath(
            '/html/body//section[@class="CbirSection CbirSection_decorated CbirSites CbirSites_infinite"]'
        ).pop(0)

        container_title = container.xpath('h2[@class="CbirSection-Title"]').pop(0).text
        if container_title != 'Sites containing information about the image':
            return []

        results_container = container.xpath('ul[@class="CbirSites-Items"]/li[@class="CbirSites-Item"]')
        if not results_container:
            return []

        result = []
        # Yandex 搜索仅前四个结果有缩略图
        for row in results_container[:4]:
            try:
                title_info = row.xpath('div[@class="CbirSites-ItemInfo"]').pop(0)
                title_href = title_info.xpath(
                    'div[@class="CbirSites-ItemTitle"]/a[@class="Link Link_view_default"]'
                ).pop(0)
                source_text = title_href.text if len(title_href.text) <= 20 else f'{title_href.text[:20]}...'
                source_url = title_href.attrib.get('href')

                thumbnail_info = row.xpath('div[@class="CbirSites-ItemThumb"]').pop(0)
                thumbnail_href = thumbnail_info.xpath(
                    'a[@class="Link Thumb Thumb_hover_fade Thumb_shade Thumb_rounded Thumb_type_inline"]/'
                    'img[@class="MMImage Thumb-Image"]'
                ).pop(0)
                thumbnail_url = thumbnail_href.attrib.get('src')
                thumbnail_url = f'https:{thumbnail_url}' if thumbnail_url.startswith('//') else thumbnail_url

                result.append({'similarity': None,
                               'thumbnail': thumbnail_url,
                               'source': f'Yandex-{source_text}',
                               'source_urls': [source_url, thumbnail_url]})
            except (IndexError, AttributeError) as e:
                logger.debug(f'Yandex | parse failed in row, {e}')
                continue
        return result

    async def search(self) -> list[ImageSearchingResult]:
        params = {'rpt': 'imageview', 'url': self.image_url}
        yandex_search_content = await self._get_resource_as_text(url=self.api_url, params=params)
        return parse_obj_as(list[ImageSearchingResult], self._parser(content=yandex_search_content))


__all__ = [
    'Yandex',
]