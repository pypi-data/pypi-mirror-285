import re
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup, Comment
from html2text import HTML2Text

from ....common.logger import logger

# from ....common.storage import BaseStorage
from ....common.types import CrawlerBackTask, CrawlerContent, DatapoolContentType
from ...utils import canonicalize_url
from ..base_plugin import BasePlugin, BaseTag
from ...worker import WorkerTask

DOMAIN = "www.theguardian.com"


class TheGuardianPlugin(BasePlugin):

    base_url = f"https://{DOMAIN}/"

    def __init__(self, ctx, demo_tag=None):
        super().__init__(ctx)
        self.demo_tag = BaseTag(demo_tag)

    @staticmethod
    def is_supported(url):
        u = BasePlugin.parse_url(url)
        # logger.info( f'dataphoenix.info {u=}')
        return u.netloc[-16:] == ".theguardian.com"

    def is_article(self, url):
        path = urlparse(url).path
        pattern = r"^/[\w/-]+/\d+/\w+/\d+/[\w/-]+$"
        return bool(re.match(pattern, path))

    def normalize(self, url):
        parts = list(urlparse(url))
        parts[5] = ""  # remove fragment
        clean_url = urlunparse(parts)
        return clean_url

    def extract(self, soup):
        content = soup.find("article")
        if not content:
            logger.debug("No <article>. Skipped.")
            return None

        filter_list = [
            dict(string=lambda s: isinstance(s, Comment)),
            dict(name="img"),
            dict(name="svg"),
            dict(name="button"),
            dict(name="video"),
            dict(name="picture"),
            dict(name="source"),
            dict(name="small"),
            dict(name="footer"),
            dict(name="gu-island"),
        ]
        for tag_params in filter_list:
            for element in content.find_all(**tag_params):
                element.extract()

        unwrap_tags = ["figure", "figcaption", "form", "span", "a"]
        for tag in unwrap_tags:
            for element in content.find_all(tag):
                element.unwrap()

        for element in content.descendants:
            if element.name:
                element.attrs = {}

        text_maker = HTML2Text(bodywidth=80)
        text_maker.ignore_links = True
        markdown = text_maker.handle(str(content))
        markdown = re.sub("\n[ \t]+", "\n", markdown)
        markdown = re.sub("\n{2,}", "\n\n", markdown)

        i = markdown.find("Explore more on these topics")
        if i > 0:
            markdown = markdown[:i].strip()

        snippet = re.sub("\n+", " ", markdown)[:160].strip()
        logger.info(f"Extracted content: {snippet}...")
        return markdown

    async def process(self, task: WorkerTask):
        url = str(task.url)
        logger.info(f"{url} - Processing...")

        response = requests.get(url)
        if response.url != url:
            logger.info(f"{url} - Redirect to {response.url}")
            url = response.url

        soup = BeautifulSoup(response.content, "html.parser")

        if not self.demo_tag.is_valid():
            platform_tag = await self.get_platform_tag(DOMAIN, soup, 3600)
        else:
            platform_tag = self.demo_tag

        logger.debug("Adding new links...")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_local_url = BasePlugin.get_local_url(href, url)
            if full_local_url:
                full_local_url = canonicalize_url(full_local_url)
                logger.info(full_local_url)
                yield CrawlerBackTask(url=full_local_url)

        if self.is_article(url):
            content = self.extract(soup)
            if content:
                # storage_id = self.ctx.storage.gen_id(url)
                # logger.info(f"putting article into {storage_id=}")

                # await self.ctx.storage.put(
                #     storage_id,
                #     BasePlugin.make_text_storage_value(content),
                # )
                yield CrawlerContent(
                    platform_tag_id=str(platform_tag) if platform_tag is not None else None,
                    platform_tag_keepout=platform_tag.is_keepout() if platform_tag is not None else False,
                    type=DatapoolContentType.Text,
                    # storage_id=storage_id,
                    url=url,
                    content=BasePlugin.make_text_storage_value(content),
                )
