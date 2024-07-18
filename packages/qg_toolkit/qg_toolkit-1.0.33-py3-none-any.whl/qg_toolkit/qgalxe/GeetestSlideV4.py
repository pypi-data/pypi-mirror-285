import json
import time
from typing import Union

import requests
from faker import Faker
from loguru import logger


class GeetestSlideV4:
    def __init__(self):
        self.valid_url = None

    def get_captcha(self, url):
        self.valid_url = url
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
        session = requests.Session()
        session.headers.update(headers)
        res = session.get(self.valid_url).text
        res = json.loads(res[res.index("(") + 1:res.rindex(")")])
        if "seccode" in res["data"]:
            logger.success(f'GeetestSlide V4打码结果: {res["data"]["seccode"]}')
            return res["data"]["seccode"]
        else:
            return None

    def solve_captcha(self, url=None) -> Union[str, None]:
        if url is None:
            return None
        return self.get_captcha(url)

#
# if __name__ == '__main__':
#     gt = GeetestSlideV4()
#     for _ in range(10):
#         gt.solve_captcha(
#             url = 'https://gcaptcha4.geetest.com/verify?callback=geetest_1714388895377&captcha_id=a7ea5725ff59be6a27d8db0d05a1bf09&client_type=web&lot_number=935469a676134c8a89998513a6692c89&payload=_b-sD20eax9oEJvmoMxvFPDC8WTZafY4krFYMddesP3be1zPV3xye8FjcTq0_uP_rmIBBbVvrcjuotejPtAN1bDUKUR8uzpQw3ZRo4BYjxjlNS2Qy0TgXDfw2cmhZVtjl_euFv2XpFsThDN7hYo1mttSrox9uWhxWO6sc5g3s7c1XX-KgZocOJhYYBsxbgTo7Uc8FKlakNIs-VHF3bPXo7yvIAP02ipj5jUkVXNcVl-SzMY2O1dF8cE5QKH_oQlHue7thDQgmKUsGeeaH-_N7E7jzrYvWAwvLvNO2eo9KGu1bx7nsMWnzhzUw0nNBBDn4jZ2NqH7zELDxMCH2emvmWD978R8yuf3pY77Po2mhshpUkDVVe_3rLanDYCT8LpvAjzAYeMEmE8gimMcEgnIIug93zS1dAL6AnoOnFPpRWdcdly9BT1k2BXBSDsm_Dc4clPw5iNSlwvakxlYfDFNAL-Uudvf-aTnfG06uzmvqA23iY0k0i-RPZ3rGyn0wlBgtVq_vKuO5Kd4kn4MajhFRYTyIwAEZt7b4MY-aCGM6VovuIFtql2BtmKr9maoic0lUMh2ueiEEkQDv7yuxDyGm7G6FE_cBeoLFB1irBaKYmUczrP1qPTcPfRJnmTw_GTIiMnnyeJj4kzEUkQ-hEvoMsRq9V0leg6szU8PZfXTByndIVbLzjQ9Youa3CVIDSwAB75DZGvhPj4P3DbAZYhceyDIn5oB3x2AFaRwAVP9CuNr19ljOXiMDDyMYtbeVZtmyg0gPDoMPz81GL-LHc31oVjtzuXWcMy8sEkPmQFOrdAovrYtbvbuRaBPzBva-BGUUNhRU6pJ_RdWtfUQvWCBJRTPsQ52KfEMipmcACOvVeo%3D&process_token=4b88013bdf66814aa8bb33f197a7699e99299720a0a705c320acc6cc3f93d43d&payload_protocol=1&pt=1&w=77714321393fd537dbb657a2e944e5c73874fe11abd6602f631765b395dfc156feda7a3e803c1be9b97f8b208790fc23440ced449aad6b757195a8166e9ee01893017ab26370dd70e6a9a0d203811e52baf8757b67da9739061d79cd231f2de6a9d2306cd8fc7f5ec4367f36d5c85169cb93383394775211a9cbf28db2f8bac126884c2d70fbce1f187a13b9feea4a9dfa11e9654a3c50711313741cd4ff5daa8784c56e8b7ee800aeb0ec5239e0291892d31fea403ed7b51327d0d46cefcaa795dcfe803103b3c3af7dbe5315b44b8a47d38fd3ef949f31028b5801b41d550de97cf95ab6ea0c65fa7221d265870bb844873ff4948e2d2a8e84cd53946942e4036307fde947515029ba671db386e55221509efb296c35ba8dccf39de723cfc87c1ae9bdba3eccc08d5f2847b76fd052e44d1508c3cc307e90b049eaac7d5dee0fb1a35f364e7397d9b51d2d1bdb7beffd6acf7b6ff819f01762542ae3f37599b4ac9d9f06ef9bb376eeb36c90e27fca53b931b2ff50936e5f6b9b1290b1a65fe23065ef4011052c932db9df1859b1b606da565232021bd5aee4a863c2456618aea0b47050e299d764a886ec615b41fc6b5907c2220258e014ba836e38feb4f7ab78970aa5bf8e402a0d55d806ba2506cf346c4059d3e008c9fbcffa7c01bee7fb4c4aace94b92bc37edb60fb3a5433e1d967bf4a0bf92073da684a51341106f706b390a9eea51ae3c2c87390672434cfa14a5778c7e4242822fdeeb9ba501704a4ad9ced7a304921f858c2067d084fd2a5387f09dae2394bd6061c5aa2a468a')
#         time.sleep(2)
