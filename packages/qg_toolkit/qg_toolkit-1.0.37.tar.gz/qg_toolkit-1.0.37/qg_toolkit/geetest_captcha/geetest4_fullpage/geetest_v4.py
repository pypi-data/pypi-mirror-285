import json
import os
import time
# import requests
import urllib.parse
import uuid

import execjs
from curl_cffi import requests


class GeetestV4:
    def __init__(self, captcha_id):
        self.daily_str = {"9KEN":"VGyt"}
        self.captcha_id = captcha_id

    def solve_captcha(self):
        challenge = str(uuid.uuid4())
        url = "https://gcaptcha4.geetest.com/load?captcha_id=" + self.captcha_id + "&challenge=" + challenge \
              + "&client_type=web&lang=zh-cn&callback=geetest_" + str(round(time.time() * 1000))
        # & risk_type = ai
        res = requests.get(url, impersonate="chrome101").text
        res = json.loads(res[res.index("(") + 1:res.rindex(")")])
        lot_number = res['data']['lot_number']
        detail_time = res['data']["pow_detail"]["datetime"]
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'jiyan.js')
        with open(file_path, 'r', encoding='utf-8') as f:
            js = execjs.compile(f.read())
        if not self.daily_str:
            self.get_daily_str()
        w = js.call('get_w', self.captcha_id, lot_number, detail_time, self.daily_str)
        url = "https://gcaptcha4.geetest.com/verify"
        params = {
            "callback": "geetest_" + str(round(time.time() * 1000)),
            "captcha_id": self.captcha_id,
            "client_type": "web",
            "lot_number": lot_number,
            # "risk_type": "ai",
            "payload": res['data']['payload'],
            "process_token": res['data']['process_token'],
            "payload_protocol": "1",
            "pt": "1",
            "w": w
        }
        res = requests.get(url, params=params).text
        res = json.loads(res[res.index("(") + 1:res.rindex(")")])
        print('Geetest V4打码成功:', res)
        return res["data"]["seccode"]

    def load_js_handle(self):
        challenge = str(uuid.uuid4())
        headers = {
            'authority': 'static.geetest.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://galxe.com',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        params = {
            'captcha_id': f'{self.captcha_id}',
            'challenge': f'{challenge}',
            'client_type': 'web',
            'lang': 'zh-cn',
            'callback': f'geetest_{int(time.time() * 1000)}',
        }
        file_url = f"https://gcaptcha4.geetest.com/load"
        try:
            response = requests.get(file_url, params=params, headers=headers, impersonate="chrome101")
            response_text = response.text
            first_open_parenthesis = response_text.find('(')
            last_close_parenthesis = response_text.rfind(')')
            result = response_text[first_open_parenthesis + 1:last_close_parenthesis]
            json_data = json.loads(result)['data']
            js_url = 'https://static.geetest.com' + json_data['static_path'] + json_data['js']
            print('js url:', js_url)
            js_data = requests.get(js_url).text
            start_index = js_data.index("decodeURI(") + 11
            end_index = js_data.rfind("');")
            return js_data[start_index:end_index + 1]
        except Exception as error:
            print('发生错误：', error)

    def handle_daily_str_fun(self):
        encoded_key = 'eDchk2'
        data_to_decode = self.load_js_handle()
        data_to_decode = str(data_to_decode).replace('\'', '')
        # print(len(data_to_decode))
        decoded_data = urllib.parse.unquote(data_to_decode)
        key_length = len(encoded_key)
        decoded_result = ''

        for i in range(len(decoded_data)):
            key_char = ord(encoded_key[i % key_length])
            decoded_result += chr(ord(decoded_data[i]) ^ key_char)
        decoded_data = decoded_result.split('^')
        # print(len(decoded_data))
        return {
            'decode': lambda index: decoded_data[index]
        }

    def get_daily_str(self):
        try:
            result = self.handle_daily_str_fun()
            decoded_value = result['decode'](744)  # 传递要获取的索引
            # print('解码后的值:', decoded_value)
            self.daily_str = json.loads(decoded_value)
            # return decoded_value
        except Exception as error:
            print('发生错误：', error)
            return None


if __name__ == '__main__':
    captchaId = "d7e47396afd397dd7c8cf7f280adc212"
    gt = GeetestV4(captchaId)
    sol = gt.solve_captcha()
    print(sol)
    # gt.get_daily_str(captchaId)

    # data = "1|0|md5|2023-08-23T10:01:59.201063+08:00|244bcb8b9846215df5af4c624a750db4|023ca18a84b441ffbd52f10d85909738||d5e239e3dfc6714c"
    # md5_hash = hashlib.md5()
    # md5_hash.update(data.encode('utf-8'))
    # print(md5_hash.hexdigest())
    # a = '{"ZLQg":"QiLi"}'
    # b = json.loads(a)
