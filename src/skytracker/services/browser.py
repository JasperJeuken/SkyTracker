"""Browser service"""
from typing import Optional, Literal
from urllib.parse import urlparse, parse_qs, unquote
from asyncio import Lock

from fastapi import HTTPException
from playwright.async_api import (async_playwright, Browser, Playwright, Page,
                                  TimeoutError as PlaywrightTimeoutError)

from skytracker.utils import logger


class WebBrowser:
    """Playwright browser for retrieving webpages"""

    def __init__(self, headless: bool = True, args: list[str] = None) -> None:
        """Create a new Playwright browser instance using Chromium

        Args:
            headless (bool, optional): whether to launch Chromium headless. Defaults to True.
            args (list[str], optional): Chromium launch arguments. Defaults to ['--no-sandbox'].
        """
        self._chromium_headless: bool = headless
        self._chromium_args: list[str] = args if args is not None else ['--no-sandbox']
        self._browser: Optional[Browser] = None
        self._playwright: Optional[Playwright] = None
        self._lock: Lock = Lock()
    
    async def start(self) -> None:
        """Open the browser"""
        if self._browser is not None or self._playwright is not None:
            return
        logger.info('Starting Playwright and Chromium browser...')
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self._chromium_headless,
                                                               args=self._chromium_args)
    
    async def stop(self) -> None:
        """Close the browser"""
        if self._browser is not None:
            try:
                logger.info('Closing Chromium browser...')
                await self._browser.close()
            except Exception as exc:
                logger.warning(f'Error when closing browser: {exc}')
            finally:
                self._browser = None
        if self._playwright is not None:
            try:
                logger.info('Closing Playwright...')
                await self._playwright.stop()
            except Exception as exc:
                logger.warning(f'Error when closing Playwright: {exc}')
            finally:
                self._playwright = None
    
    async def get_page(self, url: str, timeout: int = 10000, wait_for: Optional[str] = None) \
        -> Page:
        """Get a website page

        Args:
            url (str): URL to retrieve
            timeout (int, optional): timeout in milliseconds. Defaults to 10000 ms.
            wait_for (str, optional): element selector to wait for. Defaults to None.

        Returns:
            Page: loaded web page
        """
        # Ensure browser is open
        if self._browser is None:
            await self.start()
        logger.info(f'Fetching URL "{url}"...')

        async with self._lock:
        
            # Create context and page
            context = await self._browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' + \
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                accept_downloads=False
            )
            page = await context.new_page()

            # Try to load the page
            try:
                await page.goto(url, timeout=timeout)
                if wait_for is not None:
                    await page.wait_for_selector(wait_for, timeout=timeout)
            except PlaywrightTimeoutError:
                await context.close()
                logger.error(f'Timeout while fetching URL "{url}" (wait_for="{wait_for}")')
                raise HTTPException(status_code=504, detail='Timeout while fetching page')
            except Exception as exc:
                await context.close()
                logger.error(f'Failed to fetch page: {exc}')
                raise HTTPException(status_code=502, detail=f'Failed to fetch page: {exc}')
            return page

    async def get_images_from_page(self, url: str, timeout: int = 10000, limit: int = 0) \
        -> list[dict[Literal['image', 'detail'], str]]:
        """Get image (and corresponding) detail URLs from a web page

        Args:
            url (str): URL to fetch images from
            timeout (int, optional): timeout in milliseconds. Defaults to 10000 ms.
            limit (int, optional): maximum number of results to return (0=all). Defaults to 0 (all).

        Returns:
            list[dict[Literal['image', 'detail'], str]]: image and detail URLs
        """
        # Load page
        page = await self.get_page(url, timeout)

        # Parse image information
        results = []
        divs = await page.query_selector_all('div.imgpt')
        for div in divs:

            # Get image and detail link information
            img_link = await div.query_selector('a:has(img)')
            info_link = await div.query_selector("a[target='_blank']")
            if img_link is None or info_link is None:
                continue
            img_href = await img_link.get_attribute('href')
            info_href = await info_link.get_attribute('href')
            if img_href is None or info_href is None:
                continue

            # Parse image URL
            img_parse = urlparse(img_href)
            img_urls = parse_qs(img_parse.query).get('mediaurl', [])
            if not len(img_urls):
                continue
            img_url = unquote(img_urls[0])

            # Add result
            results.append({
                'image': img_url,
                'detail': info_href
            })
            if limit > 0 and len(results) >= limit:
                break
        await page.close()
        await page.context.close()
        return results
