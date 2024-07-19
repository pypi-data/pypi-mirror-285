import json
import time
import uuid

import requests
from faker import Faker
from loguru import logger
from playwright.sync_api import sync_playwright

from qg_toolkit.tools.qg_file import QGFile


class GeetestFullPageV4:
    def __init__(self):
        self.valid_url = None
        self.w = None
        self.captcha_id = "244bcb8b9846215df5af4c624a750db4"
        self.page = None

    def _generate_valid_url(self):
        if self.page:
            self.get_vaild_url()
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=[
                '--lang=en-US,en',
                '--disable-blink-features=AutomationControlled',
            ])
            context = browser.new_context()
            context.add_init_script('() => {}')
            valid_url = ''
            try:
                page = context.new_page()
                page.goto('https://app.galxe.com/quest', wait_until='domcontentloaded', timeout=25000)
                self.page = page
                self.get_vaild_url()
            except Exception as e:
                logger.error(f'GeetestV4打码失败: {str(e)}')
            context.close()
            browser.close()

    def get_vaild_url(self):
        self.page.evaluate(f'''
                        window.initGeetest4({{captchaId: "{self.captcha_id}", product: "bind"}})
                    ''')
        with self.page.expect_response(lambda resp: resp.status == 200 and 'verify' in resp.url, timeout=25000) as response_info:
            valid_url = response_info.value.url
            self.valid_url = valid_url
            if self.valid_url != '':
                logger.success(f'GeetestV4打码成功！{valid_url}')
                res = requests.get(self.valid_url).text
                res = json.loads(res[res.index("(") + 1:res.rindex(")")])
                logger.success(f'GeetestV4打码结果：{res}')

    def get_captcha(self):
        if not self.valid_url:
            return
        fake = Faker("zh_CN")
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': f'{fake.chrome()}',
        }
        res = requests.get(self.valid_url, headers=headers).text
        res = json.loads(res[res.index("(") + 1:res.rindex(")")])
        if "seccode" in res["data"]:
            logger.success(f'Geetest V4打码结果: {res["data"]["seccode"]}')
            return res["data"]["seccode"]
        else:
            logger.error(f'Geetest V4打码失败: {res["data"]}')
            return None

    def get_captcha_v2(self):
        if not self.valid_url:
            return
        self.w = QGFile.url_params_to_object(self.valid_url, "w")
        fake = Faker("zh_CN")
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': f'{fake.chrome()}',
        }
        challenge = str(uuid.uuid4())
        url = "https://gcaptcha4.geetest.com/load?captcha_id=" + self.captcha_id + "&challenge=" + challenge \
              + "&client_type=web&lang=zh-cn&callback=geetest_" + str(round(time.time() * 1000))
        # & risk_type = ai
        res = requests.get(url, headers=headers).text
        res = json.loads(res[res.index("(") + 1:res.rindex(")")])
        lot_number = res['data']['lot_number']
        detail_time = res['data']["pow_detail"]["datetime"]
        params = {
            'callback': "geetest_" + str(round(time.time() * 1000)),
            'captcha_id': '244bcb8b9846215df5af4c624a750db4',
            'client_type': 'web',
            'lot_number': lot_number,
            "payload": res['data']['payload'],
            "process_token": res['data']['process_token'],
            'payload_protocol': '1',
            'pt': '1',
            'w': f'{self.w}',
        }
        res = requests.get('https://gcaptcha4.geetest.com/verify', params=params, headers=headers).text
        res = json.loads(res[res.index("(") + 1:res.rindex(")")])
        if "seccode" in res["data"]:
            logger.success(f'Geetest V4打码结果: {res["data"]["seccode"]}')
            return res["data"]["seccode"]
        else:
            logger.error(f'Geetest V4打码失败: {res["data"]}')
            return None

    def solve_captcha(self) -> str:
        self._generate_valid_url()
        return self.get_captcha()

    def solve_captcha_v2(self) -> str:
        if self.valid_url is None or self.valid_url == '':
            self._generate_valid_url()
        return self.get_captcha_v2()


if __name__ == '__main__':
    gt = GeetestFullPageV4()
    for _ in range(10):
        gt.solve_captcha()
        time.sleep(2)
