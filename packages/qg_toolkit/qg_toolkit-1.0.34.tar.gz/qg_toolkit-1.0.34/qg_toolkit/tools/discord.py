import copy
import random
import time
from threading import Lock

import capsolver
import requests
from loguru import logger

from qg_toolkit.tools.qg_file import QGFile
from qg_toolkit.tools.yescaptcha import YesCaptcha


class QDiscord:
    lock = Lock()

    headers = {
        'authority': 'discord.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'if-modified-since': 'Wed, 27 Sep 2023 23:07:34 GMT',
        'if-none-match': 'W/"044ab8b890eacce518ef1038efff3477"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }
    cookies = {
        # '__dcfduid': '35a9c4e0e01b11ec91b6497f3c4b8b8a',
        # '__sdcfduid': '35a9c4e1e01b11ec91b6497f3c4b8b8ac107c0425cecd7ee64c9562fe4a920a5193b1e6a99a89e7baa17279d02a07495',
        # '_gcl_au': '1.1.2003521288.1692090429',
        # '_ga': 'GA1.1.222680285.1692090430',
        # 'OptanonConsent': 'isIABGlobal=false&datestamp=Tue+Aug+15+2023+17%3A07%3A09+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=6.33.0&hosts=&landingPath=https%3A%2F%2Fdiscord.com%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1',
        # '_ga_Q149DFWHT7': 'GS1.1.1692090429.1.0.1692090494.0.0.0',
        # '__cfruid': '4e7190d946c987e078154be2cad511456c75e1a3-1695873781',
        # 'locale': 'zh-CN',
        # 'cf_clearance': 'jUR09l089wZ_SyRkVP1f9EXY7.1OYsR8QjVFYHuTet8-1695874154-0-1-3161ecba.d97def35.6660b35a-0.2.1695874154',
    }

    client_key = "c14f6a8da73559b4fbfd2de46eb7a4237c25cd15521"

    def __init__(self, index=None, token=None, invite_code=None):
        self.index = index
        self.token = token
        self.invite_code = invite_code
        headers = copy.deepcopy(self.headers)
        headers.update({'authorization': self.token})
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.session.cookies.update(self.cookies)
        self.yes_captcha: YesCaptcha = None
        self.userAgent = self.headers.get("user-agent")
        self.args = {
            "userAgent": self.userAgent,
            # rqdata值是通过请求获取的，这里先留空
            "rqdata": "",
        }

    def get_me(self):
        """
        修改个人信息
        """
        response = self.session.get('https://discord.com/api/v9/users/@me')
        logger.info(f'【{self.index}】:{response.text}')
        if "username" in response.text:
            data = response.json()
            log = f'【{self.index}】----{self.token}----{data["username"] + "#" + data["discriminator"]}----{data["email"]}----{data["id"]}'
            print(log)
            QDiscord.lock.acquire()
            QGFile.save_to_file("dis正常token账号0829-1.txt", log)
            QDiscord.lock.release()
        else:
            with open(f"dis过期token账号0820-1.txt", 'a', encoding='utf-8') as f1:
                f1.write(f'【{self.index}】----{self.token}\n')

    def into(self):
        json_data = {
            'session_id': None,
        }
        response = self.session.post('https://discord.com/api/v9/invites/vcKaXQ6G', json=json_data)
        print(response.text)

    def into_channel(self):
        # 完整测试流程
        if self.load():
            self.submit()

    def load(self):
        # 访问邀请页
        self.website_url = f"https://discord.com/invite/{self.invite_code}"
        r = self.session.get(self.website_url)
        logger.info(f"load invite page: {r.status_code}")
        self.session.headers.update({"Referer": self.website_url})
        # 点击进群按钮，获取验证码参数
        url = f"https://discord.com/api/v9/invites/{self.invite_code}"
        json_data = {
            'session_id': None,
        }
        r = self.session.post(url, json=json_data)
        logger.info(f"post invite page: {r.status_code}")
        self.session.headers.update({"Referer": url})
        if "401: Unauthorized" in r.text:
            logger.info(f"请先登陆，获取登陆token -> {r.text}")
            return False
        # 判断是不是已经在群里了
        if "xxxxxxxxx" in r.text:
            logger.info(f"已经在群里了 -> {r.text}")
            return False
        self.website_key = r.json().get("captcha_sitekey")
        captcha_rqdata = r.json().get("captcha_rqdata")
        self.captcha_rqtoken = r.json().get("captcha_rqtoken")
        print(self.website_key, captcha_rqdata, self.captcha_rqtoken)
        assert captcha_rqdata and self.captcha_rqtoken and self.website_key, f"Args is None: {r.text}"
        # print(self.website_key, self.website_url)
        self.args['rqdata'] = captcha_rqdata
        # task_type = "HCaptchaTaskProxyless"
        # task_type = "HCaptchaTaskProxylessE1"
        # task_type = "HCaptchaTaskProxylessM1"
        # self.yes_captcha = YesCaptcha(self.client_key, self.website_key, self.website_url, task_type=task_type)
        return True

    def submit(self):
        capsolver.api_key = "CAP-CB4FA7B61BD7848EFC8CFB81C091525B"
        params = {
            "type": "HCaptchaTurboTask",
            "websiteURL": f"{self.website_url}",
            "websiteKey": f"{self.website_key}",
            # "proxyType": "http",
            # "proxyAddress": "8.213.128.90",
            # "proxyPort": 8080,
            "proxy": "socks5:140.246.224.35:1080:tEr10TEq:Dk3y1bu1V",
            "enterprisePayload": {
                "rqdata": f"{self.args['rqdata']}"
            },
            "userAgent": self.userAgent
        }
        solution = capsolver.solve(params)
        assert solution, "获取token失败"
        captcha_key = solution.get('gRecaptchaResponse')
        userAgent = solution.get('userAgent', None)
        if self.userAgent != userAgent and userAgent:
            logger.info(f"User-Agent不一致，使用接口返回的User-Agent: {userAgent}")
            self.session.headers.update({
                'user-Agent': userAgent,
            })
        url = f"https://discord.com/api/v9/invites/{self.invite_code}"
        data = {
            'session_id': None,
        }
        data = {"captcha_key": captcha_key, "captcha_rqtoken": self.captcha_rqtoken}
        # data = {
        #     'session_id': None,
        # }
        response = self.session.post(url, json=data)
        if self.invite_code in response.text:
            logger.info(f"验证成功! -> {response.text}")
            return True
        else:
            logger.info(f"验证失败! -> {response.text}")

    def accept_rule(self):
        json_data = {
            'version': '2022-12-04T04:15:09.149000+00:00',
            'form_fields': [
                {
                    'field_type': 'TERMS',
                    'label': 'Read and agree to the server rules',
                    'description': None,
                    'automations': None,
                    'required': True,
                    'values': [
                        'Treat everyone with respect. Absolutely no harassment, witch hunting, sexism, racism, or hate speech will be tolerated.',
                        'No spam or self-promotion (server invites, advertisements, etc) without permission from a moderator. This includes DMing fellow members.',
                        'No NSFW or obscene content. This includes text, images, or links featuring nudity, sex, hard violence, or other graphically disturbing content.',
                        'The use of bots or multi-accounts is strictly forbidden.',
                        'If you see something against the rules, let a moderator know.',
                    ],
                    'response': True,
                },
            ],
        }
        response = self.session.put('https://discord.com/api/v9/guilds/887783279053406238/requests/@me', json=json_data)
        print(response.text)

    def auto_chat(self):
        msgs = [
            "升级！升级！", "最近超级热闹", "冲刺了冲刺了", "升级好慢", "主网什么时候上线", "太疯狂了", "gogogo",
            "这拼的耐力啊", "兄弟们冲冲", "肯定啊", "各位 不要卷了", "搞角色", "麻煩呢", "别搞我", "聊天有奖励吗",
            "好卷", "撸毛来了", "努力啊", "牛人啊", "都是牛", "加油肝!兄弟们", "omni大格局", "搞笑吗",
            "这项目牛逼", "又是个卷", "希望不会白卷", "各位冲起来", "吐了,吐了", "真吐了", "是卡了吗", "得分回复",
            "骚操作", "升级还是有难度的", "升级还是有难度的", "得分回复", "得分回复", "得分回复", "得分回复",
            "得分回复", "得分回复", "得分回复",
        ]
        while True:
            random_number = random.randint(10 ** (19 - 1), 10 ** 19 - 1)
            json_data = {
                'content': f'{random.choice(msgs)}',
                'nonce': f'{random_number}',
                'tts': False,
                'flags': 0,
            }
            response = self.session.post('https://discord.com/api/v9/channels/928014684571992205/messages',
                                         json=json_data)
            if response.status_code == 200:
                logger.info(f'【{self.index}】随机发言成功！:{response.text}')
            else:
                logger.info(f'【{self.index}】随机发言失败！:{response.text}')
            time.sleep(random.randint(123, 135))

    def authorize(self, params):
        """
        授权discord
        """
        # response = self.session.get('https://discord.com/api/v9/oauth2/authorize', params=params)
        # print(response.text)
        json_data = {
            'permissions': '0',
            'authorize': True,
        }
        response = self.session.post('https://discord.com/api/v9/oauth2/authorize', params=params, json=json_data)
        # print(response.text)
        if response.status_code == 200:
            # print(f'dis授权成功！！')
            location = response.json().get('location', None)
            # parsed_url = urlparse(location)
            # query_params = parse_qs(parsed_url.query)
            # code = query_params.get('code')[0]
            # state = query_params.get('state')[0]
            return location
        else:
            print(f'授权失败！！')
            return None

    def genarate_tokon(self):
        token = 'x.GNmVEE.j0uMowUQYCopc7_EIH5BDiP1sEgC2XXuQOySMQ'
        js = '(function() {window.t = "' + token + '";window.localStorage = document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage;window.setInterval(() => window.localStorage.token = `"${window.t}"`); window.location.reload();})();'
        print(js)
#
#
# def qg_task(index, token):
#     token = "MTA3ODEyMDYwOTExMzk2ODY1MA.GNmVEE.j0uMowUQYCopc7_EIH5BDiP1sEgC2XXuQOySMQ"
#     # https://discord.gg/rQAtZqdG
#     # "https://discord.gg/WNUXNQKN"
#     discord = QDiscord(index, token, "WNUXNQKN")
#     # discord.into()
#     # discord.get_me()
#     discord.into_channel()
#     # discord.invites_dis()
#     # discord.chat()
#
#
# if __name__ == '__main__':
#     requests.packages.urllib3.disable_warnings()
#     dl = 'http://124.71.157.181:15280'
#     proxy = {'http': f'{dl}', 'https': f'{dl}'}
#     setup_logger("logs/dis_log.log", "qg_discord")
#     # https://discord.gg/quai
#     # QGFile.save_to_file("dis正常token账号0723.txt", "xxxxxxxx")
#     # lock = Lock()
#     file_data = QGFile.txt_to_array('dis正常token账号0814-1.txt')
#     # file_data = QGFile.txt_to_array('dis正常token账号0814-1.txt')
#     executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
#     for i, row in enumerate(file_data, start=1):
#         token1 = row[1]
#         if 1 <= i <= 1:
#             executor.submit(qg_task, i, token1)
