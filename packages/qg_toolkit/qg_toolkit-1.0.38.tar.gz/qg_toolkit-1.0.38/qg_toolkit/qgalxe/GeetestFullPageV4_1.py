import asyncio
import json
import requests
from loguru import logger
from playwright.async_api import async_playwright


class GeetestFullPageV4:
    def __init__(self):
        self.valid_url = None
        self.w = None
        self.captcha_id = "244bcb8b9846215df5af4c624a750db4"
        self.browser = None
        self.context = None
        self.page = None

    async def initialize_page(self):
        self.p = await async_playwright().start()
        self.browser = await self.p.chromium.launch(headless=True, args=[
            '--lang=en-US,en',
            '--disable-blink-features=AutomationControlled',
        ])
        self.context = await self.browser.new_context()
        await self.context.add_init_script('() => {}')
        self.page = await self.context.new_page()
        await self.page.goto('https://app.galxe.com/quest', wait_until='domcontentloaded', timeout=250000)
        logger.info(f"Page title: {await self.page.title()}")
        await self.page.wait_for_load_state('networkidle')

    async def _init_geetest_and_get_url(self):
        try:
            self.valid_url = None
            await self.page.evaluate(f'''
                                   window.initGeetest4({{captchaId: "{self.captcha_id}", product: "bind"}})
                               ''')
            response_info = await self.page.wait_for_event('response', lambda response: response.status == 200 and 'verify' in response.url, timeout=2500000)
            self.valid_url = response_info.url
            if self.valid_url:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f'GeetestV4打码失败: {str(e)}')
            return False

    async def generate_captcha(self):
        retry_attempts = 3
        for attempt in range(1, retry_attempts + 1):
            try:
                if await self._init_geetest_and_get_url():
                    logger.success(f'Attempt {attempt}: GeetestV4获取新码！{self.valid_url}')
                    res = requests.get(self.valid_url).text
                    res = json.loads(res[res.index("(") + 1:res.rindex(")")])
                    # logger.success(f'Attempt {attempt}: GeetestV4打码结果：{res}')
                    if "seccode" in res["data"]:
                        logger.success(f'Geetest V4打码结果: {res["data"]["seccode"]}')
                        return res["data"]["seccode"]
                    else:
                        logger.error(f'Geetest V4打码失败: {res["data"]}')
                        return None
                else:
                    logger.error(f'Attempt {attempt}: GeetestV4打码失败或未获取有效 URL。')
            except Exception as e:
                logger.error(f'Attempt {attempt}: GeetestV4打码失败: {str(e)}')
        logger.error(f'所有尝试均失败，无法完成GeetestV4打码。')

    async def close(self):
        await self.page.close()
        await self.browser.close()
        await self.p.stop()


class GeetestFullPageV4SyncWrapper:
    def __init__(self):
        self.geetest = GeetestFullPageV4()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.geetest.initialize_page())

    def generate_captcha(self):
        return self.loop.run_until_complete(self.geetest.generate_captcha())

    def close(self):
        self.loop.run_until_complete(self.geetest.close())
        self.loop.close()


def main():
    gt_sync = GeetestFullPageV4SyncWrapper()
    for _ in range(10):
        captcha = gt_sync.generate_captcha()
    gt_sync.close()


if __name__ == '__main__':
    main()
