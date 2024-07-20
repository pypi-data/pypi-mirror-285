import asyncio
import re

# from bs4 import BeautifulSoup
# from playwright.async_api import Locator, Page
from playwright.async_api import TimeoutError as PlaywriteTimeoutError
from playwright.async_api import async_playwright, expect

from ....common.logger import logger

# from ....common.storage import BaseStorage
from ....common.types import CrawlerBackTask, CrawlerContent, CrawlerNop, DatapoolContentType
from ..base_plugin import BasePlugin
from ...worker import WorkerTask

# import traceback


class DataPhoenixInfoPlugin(BasePlugin):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.header_tag_id = None

    @staticmethod
    def is_supported(url):
        u = BasePlugin.parse_url(url)
        # logger.info( f'dataphoenix.info {u=}')
        return u.netloc == "dataphoenix.info"

    async def process(self, task: WorkerTask):
        logger.info(f"dataphoenix_info::process({task.url})")

        async with async_playwright() as playwright:
            self.webkit = playwright.chromium
            self.browser = await self.webkit.launch()
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

            # async with httpx.AsyncClient() as client:
            #     logger.info( f'loading url {url}')

            #     r = await client.get( url )
            #     #logger.info( f'got Response {r}')
            #     r = r.text
            logger.info(f"loading url {task.url}")
            await self.page.goto(str(task.url))  # "https://dataphoenix.info/news/"

            # check if <meta/> tag exists with our tag
            self.header_tag_id = await BasePlugin.parse_meta_tag(self.page, "robots")
            logger.info(f"{self.header_tag_id=}")

            if not self.header_tag_id:
                logger.info("No <meta> tag found")
                return

            if re.match(
                r"^http(s?)://dataphoenix.info/(news|papers|articles|videos)(?:$|/)",
                str(task.url),  # linter..
            ):
                logger.info("parsing feed")
                async for yielded in self._process_feed(task.url):
                    yield yielded
            else:
                logger.info("parsing single page")
                async for yielded in self._process_single_page(task.url):
                    yield yielded

    async def _process_single_page(self, url):
        await self._try_remove_banner()

        # article consists of header, excerpt and body
        # TODO: support video
        header = await self.page.locator("h1.gh-post-page__title").all()
        if len(header) == 0:
            logger.error("Not parsable page (header)")
            # await self.page.screenshot(
            #     path="/app/tmp/not_parsable_page_header.png"
            # )
            return
        header = await header[0].inner_text()

        # optional Excerpt
        excerpt = await self.page.locator("p.gh-post-page__excerpt").all()
        if len(excerpt) > 0:
            excerpt = await excerpt[0].inner_text()
        else:
            excerpt = ""

        body = ""
        ps = await self.page.locator("div.gh-post-page__content > p").all()
        for p in ps:
            body += await p.inner_text() + "\n"

        # storage_id = self.ctx.storage.gen_id(url)
        # logger.info(f"putting article into {storage_id=}")

        # await self.ctx.storage.put(storage_id, BasePlugin.make_text_storage_value(body, header=header, excerpt=excerpt))

        priority_timestamp = await BasePlugin.parse_time_tag(self.page, ".gh-post-info__date")
        logger.info(f"{priority_timestamp=}")

        yield CrawlerContent(
            tag_id=str(self.header_tag_id),
            tag_keepout=self.header_tag_id.is_keepout(),
            type=DatapoolContentType.Text,
            priority_timestamp=priority_timestamp,
            # storage_id=storage_id,
            url=url,
            content=BasePlugin.make_text_storage_value(body, header=header, excerpt=excerpt),
        )

    async def _process_feed(self, url):
        total_news = 0
        while True:
            # logger.info( 'scrolling  to bottom')
            # await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # logger.info( 'scrolled')

            urls = await self.page.locator("a.gh-archive-page-post-title-link").all()
            n = len(urls)
            logger.info(f"items on page {n=}, yielding from {total_news}")
            for i in range(total_news, n):
                href = await urls[i].get_attribute("href")
                logger.info(f"yielding {href=}")
                yield CrawlerBackTask(url="https://dataphoenix.info" + href)

            total_news = n

            # logger.info( 'creating button locator')
            button = self.page.locator("a.gh-load-more-button")

            # logger.info( 'getting disabled attr')
            visible = await button.is_visible()

            logger.info(f"button {visible=}")
            if not visible:
                break

            # ready = False
            # for i in range(0, 2):
            #     try:
            #         logger.info(f"waiting until button is ready for clicks ({i})")
            #         await button.click(trial=True, timeout=10000)
            #         logger.info("button is ready for clicks")
            #         ready = True
            #         break
            #     except PlaywriteTimeoutError:
            #         # logger.info( e )
            #         # logger.info( traceback.format_exc() )
            await self._try_remove_banner()

            # if not ready:
            #     logger.error("ready wait failed error")
            #     # await self.page.screenshot(path="/app/tmp/screenshot.png")
            #     break

            try:
                await button.click(no_wait_after=True, timeout=10000)
                # logger.info( "clicked More Posts")
            except PlaywriteTimeoutError:
                logger.error("click More Posts timeout")
                # await self.page.screenshot(path="/app/tmp/screenshot.png")
                break

            # for i in range(0, 10):
            #     html = await button.evaluate("el => el.outerHTML")
            #     logger.info(html)
            #     await asyncio.sleep(0.2)

            # button = self.page.locator("button.js-load-posts.c-btn--loading")
            # await button.wait_for()
            # logger.info("button changed to Loading")

            # button = self.page.locator("button.js-load-posts:not(.c-btn--loading)")
            # await button.wait_for()
            # logger.info("button changed back to More Posts")

            await asyncio.sleep(2)

        yield CrawlerNop()

    async def _try_remove_banner(self):
        close_button = await self.page.locator("span.sp-popup-close").all()
        if len(close_button) == 0:
            return False

        logger.info("Modal found, clicking modal close button")

        await close_button[0].click(no_wait_after=True)
        logger.info("waiting modal to dissapear")
        await expect(close_button[0]).to_have_count(0)
        logger.info("modal dissapeared")
        return True
