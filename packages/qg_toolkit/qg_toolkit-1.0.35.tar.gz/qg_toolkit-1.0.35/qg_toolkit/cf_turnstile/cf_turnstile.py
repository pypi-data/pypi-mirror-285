import asyncio
import random
from functools import lru_cache

from playwright.async_api import async_playwright


class CFTurnstileSolver:
    def __init__(self, site_key: str, target_url: str, headless: bool = True, proxy: str = None):
        self.site_key = site_key
        self.target_url = target_url
        self.headless = headless
        self.proxy = proxy
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.current_x = 0
        self.current_y = 0

    def __del__(self):
        self.close_browser()

    async def init_and_start_browser(self):
        self.playwright = await async_playwright().start()
        browser_args = {"headless": self.headless}
        if self.proxy:
            server, auth = self.proxy.split("@")
            username, password = auth.split(":")
            browser_args["proxy"] = {"server": f"http://{server}", "username": username, "password": password}
        self.browser = await self.playwright.firefox.launch(**browser_args)


    async def close_browser(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.current_x = 0
        self.current_y = 0

    def build_page_data(self):
        # this builds a custom page with the sitekey so we do not have to load the actual page, taking less bandwidth
        with open("utils/page.html") as f:
            self.page_data = f.read()
        stub = f"<div class=\"cf-turnstile\" data-sitekey=\"{self.sitekey}\"></div>"
        self.page_data = self.page_data.replace("<!-- cf turnstile -->", stub)

    @lru_cache(maxsize=None)
    def build_page_data_v2(self):
        self.html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>body's solver</title>
            <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback" async defer></script>
        </head>
        <body>
            <span>solver available at https://github.com/Body-Alhoha/turnaround</span>
            <div class="cf-turnstile" data-sitekey="{self.site_key}"></div>
        </body>
        </html>
        """

    def get_mouse_path(self, x1, y1, x2, y2):
        # 计算路径 x2 and y2 from x1 and y1
        path = []
        x = x1
        y = y1
        while abs(x - x2) > 3 or abs(y - y2) > 3:
            diff = abs(x - x2) + abs(y - y2)
            speed = random.randint(1, 2)
            if diff < 20:
                speed = random.randint(1, 3)
            else:
                speed *= diff / 45

            if abs(x - x2) > 3:
                if x < x2:
                    x += speed
                elif x > x2:
                    x -= speed
            if abs(y - y2) > 3:
                if y < y2:
                    y += speed
                elif y > y2:
                    y -= speed
            path.append((x, y))

        return path

    async def move_to(self, x, y):
        for path in self.get_mouse_path(self.current_x, self.current_y, x, y):
            await self.page.mouse.move(path[0], path[1])
            if random.randint(0, 100) > 15:
                ts = random.randint(1, 5) / random.randint(400, 600)
                await asyncio.sleep(ts)

    # def solve_invisible(self):
    #     iterations = 0
    #
    #     while iterations < 10:
    #         self.random_x = random.randint(0, self.window_width)
    #         self.random_y = random.randint(0, self.window_height)
    #         iterations += 1
    #
    #         self.move_to(self.random_x, self.random_y)
    #         self.current_x = self.random_x
    #         self.current_y = self.random_y
    #         elem = self.page.query_selector("[name=cf-turnstile-response]")
    #         if elem:
    #             if elem.get_attribute("value"):
    #                 return elem.get_attribute("value")
    #         time.sleep(random.randint(2, 5) / random.randint(400, 600))
    #     return "failed"

    async def solve_visible(self):
        iframe = await self.page.query_selector("div[class='cf-turnstile-wrapper']")
        while not iframe:
            iframe = await self.page.query_selector("div[class='cf-turnstile-wrapper']")
            await asyncio.sleep(0.1)
        while not await iframe.bounding_box():
            await asyncio.sleep(0.1)
        bounding_box = await iframe.bounding_box()
        x = bounding_box["x"] + random.randint(5, 12)
        y = bounding_box["y"] + random.randint(5, 12)
        await self.move_to(x, y)
        self.current_x = x
        self.current_y = y
        await asyncio.sleep(3)
        width = 24
        x = 22 + width / 5 + random.randint(int(width / 5), int(width - width / 5))
        y = 60

        await self.move_to(x, y)

        self.current_x = x
        self.current_y = y
        ts = random.randint(1, 5) / random.randint(400, 600)
        await asyncio.sleep(ts)
        await self.page.mouse.click(x, y)

        iterations = 0

        while iterations < 10:
            self.random_x = random.randint(0, self.window_width)
            self.random_y = random.randint(0, self.window_height)
            iterations += 1
            await self.move_to(self.random_x, self.random_y)
            self.current_x = self.random_x
            self.current_y = self.random_y
            elem = await self.page.query_selector("[name=cf-turnstile-response]")
            if elem:
                val = await elem.get_attribute("value")
                if val:
                    return val
            ts = random.randint(2, 5) / random.randint(400, 600)
            await asyncio.sleep(ts)
        return "failed"

    async def solve(self, auto_close=True):
        await self.init_and_start_browser()
        self.target_url = self.target_url + "/" if not self.target_url.endswith("/") else self.target_url
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.build_page_data_v2()
        await self.page.route(self.target_url, lambda route: route.fulfill(body=self.html, status=200))
        await self.page.goto(self.target_url)
        self.window_width = await self.page.evaluate("window.innerWidth")
        self.window_height = await self.page.evaluate("window.innerHeight")
        # if self.invisible:
        #     output = self.solve_invisible()
        # else:
        output = await self.solve_visible()
        if auto_close:
            await self.close_browser()
        return output


if __name__ == '__main__':
    site_key = '0x4AAAAAAAc6HG1RMG_8EHSC'
    target_url = 'https://faucet.sonic.game/'
    headless = False
    cf_solve = CFTurnstileSolver(site_key, target_url, headless=headless)
    for i in range(10):
        cf_token = asyncio.run(cf_solve.solve())
        print(f'CF_TOKEN破解【1】: {cf_token}')
    asyncio.run(cf_solve.close_browser())
