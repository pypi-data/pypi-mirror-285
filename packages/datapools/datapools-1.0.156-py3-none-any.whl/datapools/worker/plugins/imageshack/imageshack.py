import asyncio

# import traceback
from typing import Union

# import httpx
from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywriteTimeoutError
from playwright.async_api import async_playwright

from ....common.logger import logger

# from ....common.storage import BaseStorage
from ....common.types import CrawlerBackTask, CrawlerContent, CrawlerDemoUser, DatapoolContentType
from ...utils import canonicalize_url
from ..base_plugin import BasePlugin, BaseTag
from ...worker import WorkerTask

# from typing import List

DOMAIN = "imageshack.com"


class ImageshackPlugin(BasePlugin):
    def __init__(self, ctx, demo_tag=None):
        super().__init__(ctx)
        self.demo_tag = BaseTag(demo_tag)

    @staticmethod
    def is_supported(url):
        u = BasePlugin.parse_url(url)
        # logger.info( f'imageshack {u=}')
        return u.netloc == DOMAIN

    async def process(self, task: WorkerTask):
        if self.ctx.session is None:
            raise Exception("invalid usage")

        logger.info(f"imageshack::process({task.url})")

        async with async_playwright() as playwright:
            webkit = playwright.chromium
            browser = await webkit.launch()
            viewport_height = 1024
            context = await browser.new_context(viewport={"width": 1920, "height": viewport_height})

            page = await context.new_page()
            await page.goto(str(task.url))

            if not self.demo_tag.is_valid():
                platform_tag = await self.get_platform_tag(DOMAIN, page, 3600)
            else:
                platform_tag = self.demo_tag

            session_meta = await self.ctx.session.get_meta()

            n_images = 0
            n_hrefs = 0
            expect_changes = True
            while expect_changes:
                expect_changes = False

                # 1.search for photo LINKS and return them as new tasks
                hrefs = await page.locator("a.photo, a.hero-wrapper").all()
                new_n_hrefs = len(hrefs)
                if new_n_hrefs != n_hrefs:
                    expect_changes = True

                while n_hrefs < new_n_hrefs:
                    try:
                        href = await hrefs[n_hrefs].get_attribute("href", timeout=100)
                        n_hrefs += 1

                        full_local_url = BasePlugin.get_local_url(href, session_meta["url"])
                        if full_local_url:
                            # strict constraint on urls, else may get endless recursions etc
                            full_local_url = canonicalize_url(full_local_url)
                            logger.info(f"adding task: {full_local_url}")

                            yield CrawlerBackTask(url=full_local_url)
                        else:
                            logger.info(f'non local: {href=} {session_meta["url"]=}')

                    except PlaywriteTimeoutError:
                        # element may be not ready yet, no problems, will get it on the next iteration
                        # logger.info( 'get_attribute timeout' )
                        expect_changes = True
                        break

                # 2. search for single photo IMAGE
                images = await page.locator("img#lp-image").all()
                new_n_images = len(images)
                if new_n_images > n_images:
                    expect_changes = True

                while n_images < new_n_images:
                    try:
                        src = await images[n_images].get_attribute("src", timeout=100)
                        n_images += 1

                        logger.info(f"{src=}")
                        if src is None:
                            logger.info("--------------------------------------")
                            outerHTML = await images[n_images - 1].evaluate("el => el.outerHTML")
                            logger.info(f"{outerHTML=}")
                            continue

                        full_local_url = BasePlugin.get_local_url(src, session_meta["url"])
                        logger.info(full_local_url)

                        copyright_owner_tag = None

                        # check for user license on his public profile page
                        profile_link = await page.locator("a.profile-link").all()
                        if len(profile_link):
                            href = await profile_link[0].get_attribute("href")
                            if href is not None:
                                # strict constraint on urls, else may get endless recursions etc
                                full_profile_url = canonicalize_url(BasePlugin.get_local_url(href, session_meta["url"]))
                                logger.info(f"adding task: {full_profile_url}")

                                yield CrawlerBackTask(url=full_profile_url)

                                if not self.demo_tag.is_valid():
                                    copyright_owner_tag = await self.parse_user_profile(href)
                                else:
                                    # demo functionality for royalties spreadout demo
                                    user_name = href.split("/")[-1]
                                    short_tag_id = BasePlugin.gen_demo_tag(user_name)
                                    copyright_owner_tag = BaseTag(short_tag_id)
                                    yield CrawlerDemoUser(
                                        user_name=user_name, short_tag_id=short_tag_id, platform="imageshack.com"
                                    )

                        if copyright_owner_tag is not None:
                            logger.info(f"found {copyright_owner_tag=}")

                        # TODO: getting image from browser works somehow but
                        #   requires image type detection, quality check, crossOrigin understading etc
                        #   So for now let's do not in optimal way
                        # content = await self.download(full_local_url)
                        # getting content from browser page instead of downloading it again
                        # content = await BasePlugin.get_webpage_image_bytes(images[n_images-1])
                        # if content:
                        yield CrawlerContent(
                            copyright_tag_id=(str(copyright_owner_tag) if copyright_owner_tag is not None else None),
                            copyright_tag_keepout=(
                                copyright_owner_tag.is_keepout() if copyright_owner_tag is not None else False
                            ),
                            platform_tag_id=str(platform_tag) if platform_tag is not None else None,
                            platform_tag_keepout=(platform_tag.is_keepout() if platform_tag is not None else False),
                            type=DatapoolContentType.Image,
                            priority_timestamp=await BasePlugin.parse_time_tag(page, ".user-area time"),
                            url=full_local_url,
                        )

                    except PlaywriteTimeoutError:
                        # element may be not ready yet, no problems, will get it on the next iteration
                        # logger.info( 'get_attribute timeout' )
                        expect_changes = True
                        break

                scroll_height1 = await page.evaluate("document.body.scrollHeight")
                await page.mouse.wheel(0, viewport_height * 0.8)
                scroll_height2 = await page.evaluate("document.body.scrollHeight")
                logger.info(f"*********** {scroll_height1=} {scroll_height2=} ****************")
                if scroll_height1 != scroll_height2:
                    expect_changes = True

                await asyncio.sleep(1)

    async def parse_user_profile(self, href) -> Union[BaseTag, None]:
        username = href.split("/")[-1]
        if not BasePlugin.copyright_tags_cache.contains(username, 3600):
            url = f"https://{DOMAIN}/{href}"

            logger.info(f"parsing user profile {url=}")

            r = await self.download(url)
            # logger.info( f'text: {r}')
            logger.info(f"got url content length={len(r)}")

            soup = BeautifulSoup(r, "html.parser")
            about = soup.body.find("div", attrs={"class": "bio tall"})
            if about:
                BasePlugin.copyright_tags_cache.set(username, BasePlugin.parse_tag_in_str(about.contents[0]))
            else:
                BasePlugin.copyright_tags_cache.set(username, None)
        return BasePlugin.copyright_tags_cache.get(username)
