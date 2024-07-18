import concurrent.futures
import copy
import re

import requests
from bs4 import BeautifulSoup

from qg_toolkit.tools.qg_file import QGFile
from loguru import logger

class QTwitter:
    headers1 = {
        'authority': 'twitter.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }
    headers2 = {
        'authority': 'api.twitter.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        'content-type': 'application/json',
        'origin': 'https://twitter.com',
        'referer': 'https://twitter.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        # 'x-client-transaction-id': '0oy4xP77+LceRPB7PRSreX2KJEqXg2MPCsytADivTob69YYEgFPU1NXTHzXOyAuQyl9eawA2GCCy2z7yPbfYhMpZDu2I',
        # 'x-csrf-token': '13ad50d8a10af85b95673c524f587777',
        # 'x-guest-token': f'{gt}',
        'x-twitter-active-user': 'yes',
        'x-twitter-client-language': 'zh-cn',
    }

    def __init__(self, index=None, email=None, username=None, password=None, phone=None, token_info=None):
        self.tw_ok = False
        self.index = index
        self.email = email
        self.username = username
        self.password = password
        self.phone = phone
        self.token_info = token_info
        self.session = requests.Session()
        self.tw_map = {
        }
        if self.token_info:
            self.init_by_token()


    def init_by_token(self):
        is_success = self.refresh_session()
        if not is_success:
            return False
        cookies = {
            'auth_token': f'{self.token_info["auth_token"]}',
            'ct0': f'{self.token_info["ct0"]}',
        }
        headers = copy.deepcopy(self.headers1)
        headers.update({
            'accept': '*/*',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'content-type': 'application/json',
            # 'x-client-transaction-id': '/UdDp2yuhtYWjshJoTL8RyqEBv0ZoHw7lf7KTjFdhaJDeU/HMPMhj5N9Iaz+XoaNqzMPbABp+9vbWkaXjP1Rhg1OJDHx',
            # 'x-client-uuid': 'f1fe6974-4a34-49b3-9dac-5454f5b38d98',
            'x-csrf-token': f'{self.token_info["ct0"]}',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'zh-cn',
        })
        self.session.headers.update(headers)
        self.session.cookies.update(cookies)

    def login_by_email(self):
        """登录，仅用于取参数，平时不用"""
        flow_token = self.start_login_flow()
        if not flow_token:
            return

        params = {
            'c_name': 'ui_metrics',
        }
        response = self.session.get('https://twitter.com/i/js_inst', params=params)
        # logger.info(response.text)
        #  输入账户
        response = self.login_flow_input_username_or_email(flow_token, self.email)
        flow_token = response.json()["flow_token"]
        if "你的账号存在异常登录活动。" in response.text:
            response = self.login_flow_check_username(flow_token)
            flow_token = response.json()["flow_token"]
        response = self.login_flow_input_password(flow_token)
        flow_token = response.json()["flow_token"]
        response = self.login_flow_duplication_check(flow_token)
        self.login_flow_get_ct0()

    def login_by_username(self):
        """登录，仅用于取参数（不要频繁调用，会被冻结！）"""
        # 开始登录流程
        flow_token = self.start_login_flow()
        if not flow_token:
            return
        # params = {
        #     'c_name': 'ui_metrics',
        # }
        # response = self.session.get('https://twitter.com/i/js_inst', params=params)
        response = self.login_flow_input_username_or_email(flow_token, self.username)
        flow_token = response.json()["flow_token"]
        if "你的账号存在异常登录活动。" in response.text:
            response = self.login_flow_check_username(flow_token)
            flow_token = response.json()["flow_token"]
        response = self.login_flow_input_password(flow_token)
        flow_token = response.json()["flow_token"]
        response = self.login_flow_duplication_check(flow_token)
        if "输入与 X 账号关联的手机号码来" in response.text or "输入与 X 账号关联的邮件地址" in response.text:
            flow_token = response.json()["flow_token"]
            self.login_flow_phone_check(flow_token)
            # flow_token = response.json()["flow_token"]
        if "使用代码生成器应用生成" in response.text:
            flow_token = response.json()["flow_token"]
            self.input_google_code(flow_token)
        if "我们已发送了一个确认码至" in response.text:
            logger.info(f"【{self.username}】【{self.index}】此号完犊子完犊子咯~~~~~~~~~：{response.text}")
            return False
        self.refresh_by_session()
        # self.login_flow_get_ct0()
        # self.refresh_session()
        return True

    def start_login_flow(self):
        response = self.session.get('https://twitter.com/i/flow/login', headers=self.headers1)
        # 获取gt 大作用！！
        match = re.search(r'gt=(\d+);', response.text)
        gt = match.group(1) if match and match.group(1) else None
        if gt:
            logger.info(f"【{self.username}】【{self.index}】1.获取gt:{gt}")
        else:
            logger.info(f"【{self.username}】【{self.index}】1.未找到gt变量")
            return None
        # 2
        headers = copy.deepcopy(self.headers2)
        headers.update({
            'x-guest-token': f'{gt}'
        })
        self.session.headers.update(headers)
        params = {
            'flow_name': 'login',
        }
        json_data = {
            'input_flow_data': {
                'flow_context': {
                    'debug_overrides': {},
                    'start_location': {
                        'location': 'splash_screen',
                    },
                },
            },
            'subtask_versions': {
                'action_list': 2,
                'alert_dialog': 1,
                'app_download_cta': 1,
                'check_logged_in_account': 1,
                'choice_selection': 3,
                'contacts_live_sync_permission_prompt': 0,
                'cta': 7,
                'email_verification': 2,
                'end_flow': 1,
                'enter_date': 1,
                'enter_email': 2,
                'enter_password': 5,
                'enter_phone': 2,
                'enter_recaptcha': 1,
                'enter_text': 5,
                'enter_username': 2,
                'generic_urt': 3,
                'in_app_notification': 1,
                'interest_picker': 3,
                'js_instrumentation': 1,
                'menu_dialog': 1,
                'notifications_permission_prompt': 2,
                'open_account': 2,
                'open_home_timeline': 1,
                'open_link': 1,
                'phone_verification': 4,
                'privacy_options': 1,
                'security_key': 3,
                'select_avatar': 4,
                'select_banner': 2,
                'settings_list': 7,
                'show_code': 1,
                'sign_up': 2,
                'sign_up_review': 4,
                'tweet_selection_urt': 1,
                'update_users': 1,
                'upload_media': 1,
                'user_recommendations_list': 4,
                'user_recommendations_urt': 1,
                'wait_spinner': 3,
                'web_modal': 1,
            },
        }
        response = self.session.post('https://api.twitter.com/1.1/onboarding/task.json', params=params, json=json_data)
        logger.info(f"【{self.username}】【{self.index}】2.初始化登录流程：{response.text}")
        flow_token = response.json()["flow_token"]
        # 3.验证js
        json_data = {
            'flow_token': f'{flow_token}',
            'subtask_inputs': [
                {
                    'subtask_id': 'LoginJsInstrumentationSubtask',
                    'js_instrumentation': {
                        'response': '{"rf":{"a93fc5dc9ac246e9693c684ed79f29af46b3c64b81cd8ddd06372ee7a1751e1f":-140,"a9249513374b27e807794b9a44f32ad40494fbb4a36a32552970cdb67b892842":227,"ad9257164e44687140e434566d67e9fbe37f48aef43044e47c6ec4aec71a1022":15,"e420bb0dcbb032939891d227470ddcf0a437c99175b5e2b348d4e65a92420261":-1},"s":"ELKPLcGDfEOjJGHw63rXBEBNQuqBffo5w3a2D6hMpBa59t_pLlnShErv0VqgWkpYQZQlw0kdeLRw4sTrABFS0wM_t1ku94n7EzsX2mxIRkYqpVpjXH4anI3YHr9E-cxghN10I1Cz8xM1NsduN5Fb6Gfvs4frvU_6BRjdwyMnvotWRXlByqrL0L7Pf8MTxdO3ZmZZSnbpnyG4z_XMBfLziRzUCUG2WsY88jqDTV2_Ery6H6ybchxEj9vRKc5RgjJ9Ayl8mKJvxdHYo6Ses8w4GBRMVNmCHXHAayxEyQ9XKo8gOOqyHQswKVhfSYGpX6Kf-HH4j4JmnYVBrl9Z1U-TSgAAAYl-msQU"}',
                        'link': 'next_link',
                    },
                },
            ],
        }
        response = self.session.post('https://api.twitter.com/1.1/onboarding/task.json', json=json_data)
        logger.info(f"【{self.username}】【{self.index}】3.验证js：{response.text}")
        flow_token = response.json()["flow_token"]
        return flow_token

    def login_flow_input_username_or_email(self, flow_token, username_or_email):
        # 3 输入账户 username
        json_data = {
            'flow_token': f'{flow_token}',
            'subtask_inputs': [
                {
                    'subtask_id': 'LoginEnterUserIdentifierSSO',
                    'settings_list': {
                        'setting_responses': [
                            {
                                'key': 'user_identifier',
                                'response_data': {
                                    'text_data': {
                                        'result': f'{username_or_email}',
                                    },
                                },
                            },
                        ],
                        'link': 'next_link',
                    },
                },
            ],
        }
        response = self.session.post('https://api.twitter.com/1.1/onboarding/task.json', json=json_data)
        logger.info(f"【{self.username}】【{self.index}】登录流程->输入账号或者邮箱：{response.text}")
        return response

    def login_flow_check_username(self, flow_token):
        json_data = {
            'flow_token': f'{flow_token}',
            'subtask_inputs': [
                {
                    'subtask_id': 'LoginEnterAlternateIdentifierSubtask',
                    'enter_text': {
                        'text': f'{self.username}',
                        'link': 'next_link',
                    },
                },
            ],
        }
        response = self.session.post('https://api.twitter.com/1.1/onboarding/task.json', json=json_data)
        logger.info(f"【{self.username}】【{self.index}】登录流程->验证账号名：{response.text}")
        return response

    def login_flow_input_password(self, flow_token):
        json_data = {
            'flow_token': f'{flow_token}',
            'subtask_inputs': [
                {
                    'subtask_id': 'LoginEnterPassword',
                    'enter_password': {
                        'password': f'{self.password}',
                        'link': 'next_link',
                    },
                },
            ],
        }
        response = self.session.post('https://api.twitter.com/1.1/onboarding/task.json', json=json_data)
        logger.info(f"【{self.username}】【{self.index}】6.输入密码：{response.text}")
        return response

    def login_flow_duplication_check(self, flow_token):
        json_data = {
            'flow_token': f'{flow_token}',
            'subtask_inputs': [
                {
                    'subtask_id': 'AccountDuplicationCheck',
                    'check_logged_in_account': {
                        'link': 'AccountDuplicationCheck_false',
                    },
                },
            ],
        }
        response = self.session.post('https://api.twitter.com/1.1/onboarding/task.json', json=json_data)
        logger.info(f"【{self.username}】【{self.index}】7.校验登录：{response.text}")
        return response

    def login_flow_phone_check(self, flow_token):
        json_data = {
            'flow_token': f'{flow_token}',
            'subtask_inputs': [
                {
                    'subtask_id': 'LoginAcid',
                    'enter_text': {
                        'text': f'{self.phone}',
                        'link': 'next_link',
                    },
                },
            ],
        }
        response = self.session.post('https://api.twitter.com/1.1/onboarding/task.json', json=json_data)
        logger.info(f"【{self.username}】【{self.index}】8.输入手机号验证：{response.text}")

    def login_flow_email_check(self, flow_token):
        json_data = {
            'flow_token': f'{flow_token}',
            'subtask_inputs': [
                {
                    'subtask_id': 'LoginAcid',
                    'enter_text': {
                        'text': f'{self.phone}',
                        'link': 'next_link',
                    },
                },
            ],
        }
        response = self.session.post('https://api.twitter.com/1.1/onboarding/task.json', json=json_data)
        logger.info(f"【{self.username}】【{self.index}】8.输入手机号验证：{response.text}")

    def google_author(self):
        import pyotp
        import time
        # 替换为您的谷歌身份验证器密钥
        secret_key = f"{self.phone}"
        # 创建一个TOTP对象
        totp = pyotp.TOTP(secret_key)
        # 获取当前时间戳
        current_time = int(time.time())
        # 获取谷歌验证码
        otp = totp.at(current_time)
        # 获取谷歌验证码的有效期剩余秒数
        remaining_seconds = totp.interval - (current_time % totp.interval)
        logger.info(f"谷歌验证码:{otp}", f"有效期剩余秒数:{remaining_seconds}")
        return otp

    def input_google_code(self, flow_token):
        json_data = {
            'flow_token': f'{flow_token}',
            'subtask_inputs': [
                {
                    'subtask_id': 'LoginTwoFactorAuthChallenge',
                    'enter_text': {
                        'text': f'{self.google_author()}',
                        'link': 'next_link',
                    },
                },
            ],
        }
        response = self.session.post('https://api.twitter.com/1.1/onboarding/task.json', json=json_data)
        logger.info(f"【{self.username}】【{self.index}】8.输入谷歌验证码验证：{response.text}")

    def login_flow_get_ct0(self):
        params = {
            'variables': '{"withCommunitiesMemberships":true,"withSubscribedTab":true,"withCommunitiesCreation":true}',
            'features': '{"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}',
            'fieldToggles': '{"withAuxiliaryUserLabels":false}',
        }
        cookies = {
            'ct0': f'{self.session.cookies.get("ct0")}',
            'auth_token': f'{self.session.cookies.get("auth_token")}',
        }
        self.session.headers.update({
            'x-client-transaction-id': 'nNYQLmiIS3tKttLghYxxnI1ASZgPAaTRHRysnLxU4+3chvx1usuHXhLbVl/wgr5mxRVu4ZzYArIn33PBu5IWWM2QwyBJnQ',
            'x-csrf-token': f'{self.session.cookies.get("ct0")}',
            # 'x-guest-token': f'{gt}',
            'x-twitter-active-user': 'yes',
            'x-twitter-client-language': 'zh-cn',
        })
        response = self.session.get('https://twitter.com/i/api/graphql/5wNTkTJmk8GZlJmd2rL7eQ/Viewer', params=params, cookies=cookies)
        self.token_info = self.session.cookies.get_dict()
        logger.info(f"【{self.username}】【{self.index}】9.获取关键参数ct0：{response.text}")

    def save_user_token_info(self, filename):
        cookies_dict = self.session.cookies.get_dict()
        result = f"{self.index}----{self.email}----{self.username}----{self.password}----{self.phone}----{cookies_dict}"
        with open(f"{filename}", 'a', encoding='utf-8') as f1:
            logger.info(f"{result}")
            f1.write(f'{result}\n')

    def refresh_session(self):
        # if self.token_info.get("ct0"):
        #     return True
        cookies = {
            'auth_token': f'{self.token_info["auth_token"]}',
        }
        headers = {
            'authority': 'api.twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://twitter.com',
            'pragma': 'no-cache',
            'referer': 'https://twitter.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-client-transaction-id': 'UpoQRDM+dE86fxISR0y+WaEicC0h04TkX55by5NdpppZQeeuS3pJOqH1S2NZ4/bvCcZ6EVMCOp3EfyD/gyNFd8SjK/BdUw',
            'x-client-uuid': 'f1fe6974-4a34-49b3-9dac-5454f5b38d98',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'zh-cn',
        }
        data = {
            'category': 'perftown',
            'log': '[{"description":"rweb:urt:notifications:fetch_Top:success","product":"rweb","duration_ms":667},{"description":"rweb:urt:notifications:fetch_Top:format:success","product":"rweb","duration_ms":667}]',
        }
        s = requests.Session()
        s.headers.update(headers)
        s.cookies.update(cookies)
        response = s.post('https://api.twitter.com/1.1/jot/client_event.json', data=data)
        # logger.info(f'【{self.index}】【{self.token_info["username"]}】：{response.status_code}')
        if response.status_code != 200:
            logger.info(f'【{self.index}】【{self.token_info["username"]}】已过期或者被冻结: {response.status_code}')
            if "ct0" in self.token_info:
                self.token_info.pop("ct0")
            return False
        else:
            self.token_info["ct0"] = s.cookies.get("ct0")
            self.tw_ok = True
            # logger.info(f'【{self.index}】【{self.token_info["username"]}】刷新session成功！')
            return True
            # account["twitter"] = twitter_info1

    def verify_tw(self, auth_token, ct0=None):
        cookies = {
            'auth_token': f'{auth_token}',
        }
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://twitter.com',
            'referer': 'https://twitter.com/qgx_dev',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'x-client-transaction-id': 'ocX80LIgkIJgVQK2DZ5oYeUIRZny7OYvEfCJGCDSpkbkC22XIE93lnqQGPFBsHKQ9SBNKqBVXu/A4MzXRD0fV9xbho84oA',
            'x-client-uuid': '656a8dbd-1ac6-4946-b6a0-731cfec05f93',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'zh-cn',
        }
        if ct0:
            cookies.update({
                "ct0": f"{ct0}"
            })
            headers.update({
                "x-csrf-token": f"{ct0}"
            })
        data = {
            'debug': 'true',
            'log': '[{"_category_":"client_event","format_version":2,"triggered_on":1708871665825,"profile_id":"1366019760710955009","position":0,"items":[{"item_type":3,"id":"1366019760710955009","is_viewer_follows_user":false,"is_user_follows_viewer":false,"is_viewer_super_following_user":false,"is_viewer_super_followed_by_user":false,"is_user_super_followable":false}],"event_namespace":{"page":"me","section":"sidebar","component":"unified_events","action":"impression","client":"m5"},"client_event_sequence_start_timestamp":1708870835759,"client_event_sequence_number":156,"client_app_id":"3033300"}]',
        }
        response = requests.post('https://twitter.com/i/api/1.1/jot/client_event.json', cookies=cookies, headers=headers, data=data)
        if response.status_code != 200:
            logger.info(f'【{self.username}】已过期或者被冻结: {response.status_code}')
            return -1
        else:
            if "This request requires a matching csrf cookie and header." in response.text:
                logger.info(f'【{self.username}】推特疑似正常，继续验证: {response.status_code}')
                ct0 = response.cookies.get("ct0")
                return self.verify_tw(auth_token, ct0)
            elif "temporarily locked" in response.text:
                logger.info(f'【{self.username}】推特被临时冻结: {response.status_code}，报文:{response.text}')
                return -2
            elif "is not permitted to access this feature" in response.text:
                logger.info(f'【{self.username}】推特被完全冻结: {response.status_code}，报文:{response.text}')
                return -3
            else:
                logger.info(f'【{self.username}】推特真的正常:{response.status_code}，报文:{response.text}')
                return 1

    def refresh_by_session(self):
        # if self.token_info.get("ct0"):
        #     return True
        cookies = {
            'auth_token': f'{self.session.cookies.get("auth_token")}',
        }
        headers = {
            'authority': 'api.twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://twitter.com',
            'pragma': 'no-cache',
            'referer': 'https://twitter.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-client-transaction-id': 'UpoQRDM+dE86fxISR0y+WaEicC0h04TkX55by5NdpppZQeeuS3pJOqH1S2NZ4/bvCcZ6EVMCOp3EfyD/gyNFd8SjK/BdUw',
            'x-client-uuid': 'f1fe6974-4a34-49b3-9dac-5454f5b38d98',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'zh-cn',
        }
        data = {
            'category': 'perftown',
            'log': '[{"description":"rweb:urt:notifications:fetch_Top:success","product":"rweb","duration_ms":667},{"description":"rweb:urt:notifications:fetch_Top:format:success","product":"rweb","duration_ms":667}]',
        }
        self.session.headers.update(headers)
        self.session.cookies.update(cookies)
        response = self.session.post('https://api.twitter.com/1.1/jot/client_event.json', data=data)
        # logger.info(f'【{self.index}】【{self.token_info["username"]}】：{response.status_code}')
        if response.status_code != 200:
            logger.info(f'【{self.index}】【{self.token_info["username"]}】已过期或者被冻结: {response.status_code}')
            self.token_info.pop("ct0")
            return False
        else:
            # self.token_info["ct0"] = s.cookies.get("ct0")
            self.token_info = self.session.cookies.get_dict()
            # logger.info(f'【{self.index}】【{self.token_info["username"]}】刷新session成功！')
            return True
            # account["twitter"] = twitter_info1

    def inbox_initial_state(self):
        cookies = {
            'kdt': f'{self.token_info.get("kdt")}',
            'auth_token': f'{self.token_info.get("auth_token")}',
            'ct0': f'{self.token_info.get("ct0")}',
        }
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'referer': 'https://twitter.com/home',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-client-transaction-id': 'zwgIl3vdrj6JsoOlhg4m0+7WoNGtVlgRvBUIxeLtAED61pM3fgVqf6DR4MA4vZ7NtGTSsc+mUy/U64hMG6oosuCoG/Tczg',
            'x-csrf-token': f'{self.token_info["ct0"]}',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'zh-cn',
        }
        params = {
            'nsfw_filtering_enabled': 'false',
            'include_profile_interstitial_type': '1',
            'include_blocking': '1',
            'include_blocked_by': '1',
            'include_followed_by': '1',
            'include_want_retweets': '1',
            'include_mute_edge': '1',
            'include_can_dm': '1',
            'include_can_media_tag': '1',
            'include_ext_has_nft_avatar': '1',
            'include_ext_is_blue_verified': '1',
            'include_ext_verified_type': '1',
            'include_ext_profile_image_shape': '1',
            'skip_status': '1',
            'dm_secret_conversations_enabled': 'false',
            'krs_registration_enabled': 'true',
            'cards_platform': 'Web-12',
            'include_cards': '1',
            'include_ext_alt_text': 'true',
            'include_ext_limited_action_results': 'true',
            'include_quote_count': 'true',
            'include_reply_count': '1',
            'tweet_mode': 'extended',
            'include_ext_views': 'true',
            'dm_users': 'true',
            'include_groups': 'true',
            'include_inbox_timelines': 'true',
            'include_ext_media_color': 'true',
            'supports_reactions': 'true',
            'include_ext_edit_control': 'true',
            'ext': 'mediaColor,altText,mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,birdwatchPivot,superFollowMetadata,unmentionInfo,editControl',
        }

        response = self.session.get('https://twitter.com/i/api/1.1/dm/inbox_initial_state.json', params=params, cookies=cookies, headers=headers)
        if "You are not currently active" in response.text:
            logger.info(f'【{self.username}】被完全冻结，GG啦！')
            return False
        elif 'this account is temporarily locked' in response.text:
            logger.info(f'【{self.username}】被临时冻结，需要手动解冻！')
            return False
        else:
            return True

    def get_tweet_detail_by_id(self, tweet_id):
        tw_info = self.tw_map.get(f'{tweet_id}', None)
        if tw_info:
            return tw_info
        params = {
            'variables': '{"focalTweetId":"' + tweet_id + '","with_rux_injections":false,"includePromotedContent":true,"withCommunity":true,"withQuickPromoteEligibilityTweetFields":true,"withBirdwatchNotes":true,"withVoice":true,"withV2Timeline":true}',
            'features': '{"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"c9s_tweet_anatomy_moderator_badge_enabled":true,"tweetypie_unmention_optimization_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"rweb_video_timestamps_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_enhance_cards_enabled":false}',
            'fieldToggles': '{"withArticleRichContentState":true}',
        }
        response = self.session.get('https://twitter.com/i/api/graphql/1ra1rFDRUquziGxksi5ifg/TweetDetail', params=params)
        if "threaded_conversation_with_injections_v2" in response.text:
            tw_info_result = response.json()["data"]["threaded_conversation_with_injections_v2"]["instructions"][0]["entries"][0]["content"]["itemContent"]["tweet_results"]["result"]
            if "legacy" in tw_info_result:
                tw_info = tw_info_result["legacy"]
                self.tw_map.update({
                    f'{tweet_id}': tw_info
                })
                return tw_info
            else:
                return None
        else:
            return None

    def get_user_by_screen_name(self, username):
        params = {
            'variables': '{"screen_name":"' + username + '","withSafetyModeUserFields":true}',
            'features': '{"hidden_profile_likes_enabled":false,"hidden_profile_subscriptions_enabled":false,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}',
            'fieldToggles': '{"withAuxiliaryUserLabels":false}',
        }
        response = self.session.get('https://twitter.com/i/api/graphql/xc8f1g7BYqr6VTzTbvNlGw/UserByScreenName', params=params)
        if "UserUnavailable" not in response.text:
            user_info = response.json()["data"]["user"]["result"]["legacy"]
            friends_count = user_info["friends_count"]
            followers_count = user_info["followers_count"]
            logger.info(f'【{self.username}】【{self.index}】查询用户【{username}】,粉丝数：{friends_count},关注数：{followers_count}')
            return response.json()
        else:
            logger.info(f'【{self.username}】【{self.index}】查询用户【{username}】,报文:{response.text}')
            return None

    def follow_by_name(self, username):
        """根据用户名关注"""
        if not username or username == self.username:
            return
        userinfo = self.get_user_by_screen_name(username)
        if not userinfo:
            return False
        if "following" in str(userinfo):
            logger.info(f'【{self.username}】【{self.index}】已经关注过【{username}】')
            return True
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://twitter.com',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'x-csrf-token': f'{self.token_info["ct0"]}',
        }

        data = {
            'include_profile_interstitial_type': '1',
            'include_blocking': '1',
            'include_blocked_by': '1',
            'include_followed_by': '1',
            'include_want_retweets': '1',
            'include_mute_edge': '1',
            'include_can_dm': '1',
            'include_can_media_tag': '1',
            'include_ext_has_nft_avatar': '1',
            'include_ext_is_blue_verified': '1',
            'include_ext_verified_type': '1',
            'include_ext_profile_image_shape': '1',
            'skip_status': '1',
            'user_id': f'{userinfo["data"]["user"]["result"]["rest_id"]}',
        }
        response = self.session.post('https://twitter.com/i/api/1.1/friendships/create.json', data=data, headers=headers)
        if "UserUnavailable" not in response.text:
            logger.info(f'【{self.username}】【{self.index}】关注【{username}】成功,报文:{response.text}')
            return True
        else:
            logger.info(f'【{self.username}】【{self.index}】关注【{username}】失败,报文:{response.text}')
            return False

    def unfollow_by_name(self, username):
        """根据用户名取消关注"""
        userinfo = self.get_user_by_screen_name(username)
        if not userinfo:
            return
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://twitter.com',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'x-csrf-token': f'{self.token_info["ct0"]}',
        }
        data = {
            'include_profile_interstitial_type': '1',
            'include_blocking': '1',
            'include_blocked_by': '1',
            'include_followed_by': '1',
            'include_want_retweets': '1',
            'include_mute_edge': '1',
            'include_can_dm': '1',
            'include_can_media_tag': '1',
            'include_ext_has_nft_avatar': '1',
            'include_ext_is_blue_verified': '1',
            'include_ext_verified_type': '1',
            'include_ext_profile_image_shape': '1',
            'skip_status': '1',
            'user_id': f'{userinfo["data"]["user"]["result"]["rest_id"]}',
        }
        response = self.session.post('https://twitter.com/i/api/1.1/friendships/destroy.json', headers=headers,
                                     data=data)
        if response.status_code == 200:
            logger.info(f'【{self.username}】【{self.index}】取关成功,报文:{response.text}')
        else:
            logger.info(f'【{self.username}】【{self.index}】取关失败,报文:{response.text}')

    # 发推
    def tweet(self, content):
        json_data = {
            'variables': {
                'tweet_text': f'{content} \n ',
                'dark_request': False,
                'media': {
                    'media_entities': [],
                    'possibly_sensitive': False,
                },
                'semantic_annotation_ids': [],
            },
            'features': {
                'tweetypie_unmention_optimization_enabled': True,
                'responsive_web_edit_tweet_api_enabled': True,
                'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
                'view_counts_everywhere_api_enabled': True,
                'longform_notetweets_consumption_enabled': True,
                'responsive_web_twitter_article_tweet_consumption_enabled': False,
                'tweet_awards_web_tipping_enabled': False,
                'longform_notetweets_rich_text_read_enabled': True,
                'longform_notetweets_inline_media_enabled': True,
                'responsive_web_graphql_exclude_directive_enabled': True,
                'verified_phone_label_enabled': False,
                'freedom_of_speech_not_reach_fetch_enabled': True,
                'standardized_nudges_misinfo': True,
                'tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled': True,
                'responsive_web_media_download_video_enabled': False,
                'responsive_web_graphql_skip_user_profile_image_extensions_enabled': False,
                'responsive_web_graphql_timeline_navigation_enabled': True,
                'responsive_web_enhance_cards_enabled': False,
            },
            'fieldToggles': {
                'withArticleRichContentState': False,
                'withAuxiliaryUserLabels': False,
            },
            'queryId': 'SoVnbfCycZ7fERGCwpZkYA',
        }
        response = self.session.post(
            'https://twitter.com/i/api/graphql/SoVnbfCycZ7fERGCwpZkYA/CreateTweet',
            json=json_data,
        )
        if "errors" not in response.text and response.status_code != 404:
            result = response.json()['data']['create_tweet']['tweet_results']['result']
            tweet_url = f'https://twitter.com/{result["core"]["user_results"]["result"]["legacy"]["screen_name"]}/status/{result["rest_id"]}'
            logger.info(f'【{self.username}】【{self.index}】发推成功,推文链接：{tweet_url},报文:{response.text}')
            return tweet_url
        else:
            logger.info(f'【{self.username}】【{self.index}】发推失败,报文:{response.text}')
            return None

    def reply_tweet(self, tweet_id, content):
        """回复留言指定推特"""
        json_data = {
            'variables': {
                'tweet_text': f'{content}',
                'reply': {
                    'in_reply_to_tweet_id': f'{tweet_id}',
                    'exclude_reply_user_ids': [],
                },
                'batch_compose': 'BatchSubsequent',
                'dark_request': False,
                'media': {
                    'media_entities': [],
                    'possibly_sensitive': False,
                },
                'semantic_annotation_ids': [],
            },
            'features': {
                'tweetypie_unmention_optimization_enabled': True,
                'responsive_web_edit_tweet_api_enabled': True,
                'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
                'view_counts_everywhere_api_enabled': True,
                'longform_notetweets_consumption_enabled': True,
                'responsive_web_twitter_article_tweet_consumption_enabled': False,
                'tweet_awards_web_tipping_enabled': False,
                'longform_notetweets_rich_text_read_enabled': True,
                'longform_notetweets_inline_media_enabled': True,
                'responsive_web_graphql_exclude_directive_enabled': True,
                'verified_phone_label_enabled': False,
                'freedom_of_speech_not_reach_fetch_enabled': True,
                'standardized_nudges_misinfo': True,
                'tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled': True,
                'responsive_web_media_download_video_enabled': False,
                'responsive_web_graphql_skip_user_profile_image_extensions_enabled': False,
                'responsive_web_graphql_timeline_navigation_enabled': True,
                'responsive_web_enhance_cards_enabled': False,
            },
            'fieldToggles': {
                'withArticleRichContentState': False,
                'withAuxiliaryUserLabels': False,
            },
            'queryId': 'SoVnbfCycZ7fERGCwpZkYA',
        }

        response = self.session.post(
            'https://twitter.com/i/api/graphql/SoVnbfCycZ7fERGCwpZkYA/CreateTweet',
            json=json_data,
        )
        if response.status_code == 200:
            logger.info(f'【{self.username}】【{self.index}】回复推特成功,报文:{response.text}')
            return f'https://twitter.com/{self.username}/status/{response.json()["data"]["create_tweet"]["tweet_results"]["result"]["rest_id"]}'
        else:
            logger.info(f'【{self.username}】【{self.index}】回复推特失败,报文:{response.text}')
            return None

    def retweet(self, tweet_id, tw_info=None):
        """转推指定推特"""
        if not tw_info:
            tw_info = self.get_tweet_detail_by_id(tweet_id)
        if not tw_info:
            # logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},不存在！跳过！')
            json_data = {
                'variables': {
                    'tweet_id': f'{tweet_id}',
                    'dark_request': False,
                },
                'queryId': 'ojPdsZsimiJrUGLR1sjUtA',
            }
            response = self.session.post(
                'https://twitter.com/i/api/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet',
                json=json_data,
            )
            if response.status_code == 200:
                if "have already retweeted this Tweet" in response.text:
                    logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},已经转推过！')
                else:
                    logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},转推成功,报文:{response.text}')
            else:
                logger.info(f'【{self.username}】【{self.index}】转推失败,报文:{response.text}')
            return
        if tw_info["retweeted"]:
            logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},已经转推过！跳过！')
            return
        json_data = {
            'variables': {
                'tweet_id': f'{tweet_id}',
                'dark_request': False,
            },
            'queryId': 'ojPdsZsimiJrUGLR1sjUtA',
        }
        response = self.session.post(
            'https://twitter.com/i/api/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet',
            json=json_data,
        )
        if response.status_code == 200:
            if "have already retweeted this Tweet" in response.text:
                logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},已经转推过！')
            else:
                logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},转推成功,报文:{response.text}')
        else:
            logger.info(f'【{self.username}】【{self.index}】转推失败,报文:{response.text}')

    def like(self, tweet_id, tw_info=None):
        if not tw_info:
            tw_info = self.get_tweet_detail_by_id(tweet_id)
        if not tw_info:
            # logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},不存在！跳过！')
            json_data = {
                'variables': {
                    'tweet_id': f'{tweet_id}',
                },
                'queryId': 'lI07N6Otwv1PhnEgXILM7A',
            }
            response = self.session.post(
                'https://twitter.com/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet',
                json=json_data,
            )
            if response.status_code == 200:
                if "already favorited tweet" in response.text:
                    logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},已经like过！')
                else:
                    logger.info(f'【{self.username}】【{self.index}】喜欢推特成功,报文:{response.text}')
            else:
                logger.info(f'【{self.username}】【{self.index}】喜欢推特失败,报文:{response.text}')
            return
        if tw_info["favorited"]:
            logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},已经like过！跳过！')
            return
        json_data = {
            'variables': {
                'tweet_id': f'{tweet_id}',
            },
            'queryId': 'lI07N6Otwv1PhnEgXILM7A',
        }
        response = self.session.post(
            'https://twitter.com/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet',
            json=json_data,
        )
        if response.status_code == 200:
            if "already favorited tweet" in response.text:
                logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},已经like过！')
            else:
                logger.info(f'【{self.username}】【{self.index}】喜欢推特成功,报文:{response.text}')
        else:
            logger.info(f'【{self.username}】【{self.index}】喜欢推特失败,报文:{response.text}')

    def retweet_and_like(self, tweet_id):
        """转推并且喜欢指定推特"""
        tw_info = self.get_tweet_detail_by_id(tweet_id)
        if not tw_info:
            logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},不存在！跳过！')
            return
        if tw_info["retweeted"]:
            logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},已经转推过！跳过！')
        else:
            # logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},未转推,开始转推！')
            self.retweet(tweet_id, tw_info)
        if tw_info["favorited"]:
            logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},已经like过！跳过！')
        else:
            # logger.info(f'【{self.username}】【{self.index}】推特:{tweet_id},未like,开始like！')
            self.like(tweet_id, tw_info)

    def change_password(self, new_password):
        """修改密码"""
        cookies = {
            'kdt': f'{self.token_info.get("kdt")}',
            'auth_token': f'{self.token_info.get("auth_token")}',
            'ct0': f'{self.token_info.get("ct0")}',
        }
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://twitter.com',
            'pragma': 'no-cache',
            'referer': 'https://twitter.com/settings/password',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'x-client-transaction-id': '/UdDp2yuhtYWjshJoTL8RyqEBv0ZoHw7lf7KTjFdhaJDeU/HMPMhj5N9Iaz+XoaNqzMPbABp+9vbWkaXjP1Rhg1OJDHx',
            'x-client-uuid': 'f1fe6974-4a34-49b3-9dac-5454f5b38d98',
            'x-csrf-token': f'{self.token_info.get("ct0")}',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'zh-cn',
        }

        data = {
            'current_password': f'{self.password}',
            'password': f'{new_password}',
            'password_confirmation': f'{new_password}',
        }
        response = self.session.post('https://twitter.com/i/api/i/account/change_password.json', headers=headers,
                                     cookies=cookies, data=data)
        if response.status_code == 200:
            self.password = new_password
            logger.info(f'【{self.username}】修改密码成功,报文:{response.text}')
        else:
            logger.info(f'【{self.username}】修改密码失败,报文:{response.text}')

    def set_no_pro(self):
        cookies = {
            'kdt': f'{self.token_info.get("kdt")}',
            'auth_token': f'{self.token_info.get("auth_token")}',
            'ct0': f'{self.token_info.get("ct0")}',
        }
        data = {
            'include_mention_filter': 'true',
            'include_nsfw_user_flag': 'true',
            'include_nsfw_admin_flag': 'true',
            'include_ranked_timeline': 'true',
            'include_alt_text_compose': 'true',
            'protected': 'false',
        }

        headers = {
            'authority': 'api.twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://twitter.com',
            'pragma': 'no-cache',
            'referer': 'https://twitter.com/',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-client-transaction-id': 'K5H0v5B14TEZy93MsibUSKpVVAaZLvl8S37g86I+YYf+wgbmTqxBE7MXebZp/+vsPWMquStT0+xeXx/QbW1WayKtG1OFKg',
            'x-client-uuid': '7d44bf6b-e29a-4019-b03c-87118a0cf570',
            'x-csrf-token': f'{self.token_info.get("ct0")}',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'zh-cn',
        }
        response = self.session.post('https://api.twitter.com/1.1/account/settings.json', cookies=cookies, headers=headers, data=data)
        if response.status_code == 200:
            logger.info(f'【{self.username}】设置帖子公开成功,报文:{response.text}')
        else:
            logger.info(f'【{self.username}】设置帖子公开失败,报文:{response.text}')

    def authorize(self, params):
        """
        授权推特
        """
        cookies = {
            'kdt': f'{self.token_info.get("kdt")}',
            'auth_token': f'{self.token_info.get("auth_token")}',
            'ct0': f'{self.token_info.get("ct0")}',
        }
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'x-client-transaction-id': 'tTLaZPJGhndMIE7MAPffR+tQFmeJC9XAwNnVEC0MWJVfzL6JAB4vtK9qN/uCLZA9i0z5wrXbszyivxg5H19LKSKyCU55tA',
            'x-csrf-token': f'{self.token_info.get("ct0")}',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'zh-cn',
        }
        response = self.session.get('https://twitter.com/i/api/2/oauth2/authorize', params=params, cookies=cookies, headers=headers)
        # logger.info(response.text)
        auth_code = response.json()['auth_code']
        data = {
            'approval': 'true',
            'code': f'{auth_code}',
        }
        response = self.session.post('https://twitter.com/i/api/2/oauth2/authorize', headers=headers, cookies=cookies, data=data)
        if response.status_code == 200:
            logger.info(f'推特授权成功！！')
            return auth_code
        else:
            logger.info(f'推特授权失败！！')
            return None

    def authorize_v1(self, params):
        """推特的第一个版本的授权"""
        cookies = {
            # 'kdt': f'{self.token_info.get("kdt")}',
            'auth_token': f'{self.token_info.get("auth_token")}',
            'ct0': f'{self.token_info.get("ct0")}',
        }
        # cookies = {
        #     'kdt': f'Z0pMJ5kZr8L3cUjRST0l9zWadaltbL2zgn3d8O6h',
        #     'auth_token': f'96bc2170ba8c7b8c109bb58f5d5484d4d74ec9ff',
        #     'ct0': f'6959cb5cb3e403579cbda5da0c6e7f321196ef0e4df87544c9bdc4411d653f13f069c746ea5ba39af25333ae73b0e5ea0d46c0397eec8d910c70ed8d65c06dec078ebc54a9bbeffb1f415d13df72fa3a; twid=u%3D1366019760710955009',
        # }

        headers = {
            'authority': 'api.twitter.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://api.twitter.com',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }

        oauth_token = params["oauth_token"]
        # params = {
        #     'oauth_token': 'yMidkAAAAAABpprAAAABishKkuE',
        # }
        new_sw1 = requests.Session()
        response = new_sw1.get('https://api.twitter.com/oauth/authorize', params=params, cookies=cookies, headers=headers)
        cookies.update({"_twitter_sess": response.cookies.get("_twitter_sess")})
        soup = BeautifulSoup(response.text, 'html.parser')
        authenticity_token = soup.find("input", {"name": "authenticity_token"}).get("value")
        data = {
            'authenticity_token': authenticity_token,
            'redirect_after_login': f'https://api.twitter.com/oauth/authorize?oauth_token={oauth_token}',
            'oauth_token': oauth_token,
        }
        response = new_sw1.post('https://api.twitter.com/oauth/authorize', cookies=cookies, headers=headers, data=data)
        # logger.info(response.status_code, 2)
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tag = soup.find('a', class_='maintain-context')
        oauth_verifier = ""
        if a_tag:
            href = a_tag['href']
            logger.info(f'【{self.index}】【{self.username}】提取回调链接:{href}')
            # requests.Session().get(href)
            paramxs = QGFile.url_params_to_object(href)
            oauth_verifier = paramxs["oauth_verifier"]
        else:
            logger.info("未找到指定的<a>标签")
        return oauth_verifier

    def authorize_v1_1(self, params):
        """推特的第一个版本的授权"""
        cookies = {
            # 'kdt': f'{self.token_info.get("kdt")}',
            'auth_token': f'{self.token_info.get("auth_token")}',
            'ct0': f'{self.token_info.get("ct0")}',
        }
        # cookies = {
        #     'kdt': f'Z0pMJ5kZr8L3cUjRST0l9zWadaltbL2zgn3d8O6h',
        #     'auth_token': f'96bc2170ba8c7b8c109bb58f5d5484d4d74ec9ff',
        #     'ct0': f'6959cb5cb3e403579cbda5da0c6e7f321196ef0e4df87544c9bdc4411d653f13f069c746ea5ba39af25333ae73b0e5ea0d46c0397eec8d910c70ed8d65c06dec078ebc54a9bbeffb1f415d13df72fa3a; twid=u%3D1366019760710955009',
        # }

        headers = {
            'authority': 'api.twitter.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://api.twitter.com',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }

        oauth_token = params["oauth_token"]
        # params = {
        #     'oauth_token': 'yMidkAAAAAABpprAAAABishKkuE',
        # }
        new_sw1 = requests.Session()
        response = new_sw1.get('https://api.twitter.com/oauth/authorize', params=params, cookies=cookies, headers=headers)
        cookies.update({"_twitter_sess": response.cookies.get("_twitter_sess")})
        soup = BeautifulSoup(response.text, 'html.parser')
        authenticity_token = soup.find("input", {"name": "authenticity_token"}).get("value")
        data = {
            'authenticity_token': authenticity_token,
            'redirect_after_login': f'https://api.twitter.com/oauth/authorize?oauth_token={oauth_token}',
            'oauth_token': oauth_token,
        }
        response = new_sw1.post('https://api.twitter.com/oauth/authorize', cookies=cookies, headers=headers, data=data)
        # logger.info(response.status_code, 2)
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tag = soup.find('a', class_='maintain-context')
        oauth_verifier = ""
        if a_tag:
            href = a_tag['href']
            # logger.info(f'【{self.index}】【{self.username}】提取回调链接:{href}')
            requests.Session().get(href)
            params = QGFile.url_params_to_object(href)
            oauth_verifier = params["oauth_verifier"]
            return oauth_verifier, href
        else:
            logger.info("未找到指定的<a>标签")

    def authorize_v1_2(self, params):
        """推特的第一个版本的授权"""
        cookies = {
            # 'kdt': f'{self.token_info.get("kdt")}',
            'auth_token': f'{self.token_info.get("auth_token")}',
            'ct0': f'{self.token_info.get("ct0")}',
        }
        headers = {
            'authority': 'api.twitter.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://well3.com/',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        }
        oauth_token = params["oauth_token"]
        params = {
            'oauth_token': f'{oauth_token}',
            'context_uri': 'https://well3.com',
        }
        new_sw1 = requests.Session()
        response = new_sw1.get('https://api.twitter.com/oauth/authenticate', params=params, cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tag = soup.find('a', class_='maintain-context')
        if a_tag:
            href = a_tag['href']
            # logger.info(f'【{self.index}】【{self.username}】提取回调链接:{href}')
            requests.Session().get(href)
            params = QGFile.url_params_to_object(href)
            oauth_verifier = params["oauth_verifier"]
            return oauth_verifier, href
        else:
            logger.info("未找到指定的<a>标签")

    def authorize_v1_3(self, params):
        """推特的第一个版本的授权"""
        cookies = {
            # 'kdt': f'{self.token_info.get("kdt")}',
            'auth_token': f'{self.token_info.get("auth_token")}',
            'ct0': f'{self.token_info.get("ct0")}',
        }
        # cookies = {
        #     'kdt': f'Z0pMJ5kZr8L3cUjRST0l9zWadaltbL2zgn3d8O6h',
        #     'auth_token': f'96bc2170ba8c7b8c109bb58f5d5484d4d74ec9ff',
        #     'ct0': f'6959cb5cb3e403579cbda5da0c6e7f321196ef0e4df87544c9bdc4411d653f13f069c746ea5ba39af25333ae73b0e5ea0d46c0397eec8d910c70ed8d65c06dec078ebc54a9bbeffb1f415d13df72fa3a; twid=u%3D1366019760710955009',
        # }

        headers = {
            'authority': 'api.twitter.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://api.twitter.com',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }

        oauth_token = params["oauth_token"]

        new_sw1 = requests.Session()
        response = new_sw1.get('https://api.twitter.com/oauth/authorize', params=params, cookies=cookies, headers=headers)
        cookies.update({"_twitter_sess": response.cookies.get("_twitter_sess")})
        soup = BeautifulSoup(response.text, 'html.parser')
        authenticity_token = soup.find("input", {"name": "authenticity_token"}).get("value")
        data = {
            'authenticity_token': authenticity_token,
            'redirect_after_login': f'https://api.twitter.com/oauth/authorize?oauth_token={oauth_token}',
            'oauth_token': oauth_token,
        }
        response = new_sw1.post('https://api.twitter.com/oauth/authorize', cookies=cookies, headers=headers, data=data)
        # logger.info(response.status_code, 2)
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tag = soup.find('a', class_='maintain-context')
        if a_tag:
            href = a_tag['href']
            logger.info(f'【{self.index}】【{self.username}】提取回调链接:{href}')
            # requests.Session().get(href)
            paramxs = QGFile.url_params_to_object(href)
            oauth_verifier = paramxs["oauth_verifier"]
            return oauth_verifier, href
        else:
            logger.info("未找到指定的<a>标签")
        return None

    def authorize_v2(self, params):
        """推特的第二个版本的授权"""
        cookies = {
            'kdt': f'{self.token_info.get("kdt")}',
            'auth_token': f'{self.token_info.get("auth_token")}',
            'ct0': f'{self.token_info.get("ct0")}',
        }
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'x-client-transaction-id': 'tTLaZPJGhndMIE7MAPffR+tQFmeJC9XAwNnVEC0MWJVfzL6JAB4vtK9qN/uCLZA9i0z5wrXbszyivxg5H19LKSKyCU55tA',
            'x-csrf-token': f'{self.token_info.get("ct0")}',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'zh-cn',
        }
        response = self.session.get('https://twitter.com/i/api/2/oauth2/authorize', params=params, cookies=cookies, headers=headers)
        logger.info(f'【{self.index}】【{self.username}】授权推特步骤2:{response.text}')
        auth_code = response.json()['auth_code']
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://twitter.com',
            'pragma': 'no-cache',
            'referer': 'https://twitter.com/i/oauth2/authorize?response_type=code&client_id=bUNCS1dTd0REVU9HUnRud1ZNQkc6MTpjaQ&redirect_uri=https://journey.mantle.xyz/twitter-login&scope=like.read%20tweet.read%20users.read%20offline.access%20follows.read&state=provenance&code_challenge=challenge&code_challenge_method=plain',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'x-client-transaction-id': 'S/OGMH+SFfMAqDM9UbsJB9tmJwjpZhSLV5OqatoKNnDvIw5CUcB4xoL5NlTON0ESYQKm60tq2dJVYg/y6iUvqD6Ae4tjSg',
            'x-client-uuid': '4e099dfe-ab2f-40be-a65f-fa019aa47b39',
            'x-csrf-token': f'{self.token_info.get("ct0")}',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'zh-cn',
        }
        data = {
            'approval': 'true',
            'code': f'{auth_code}',
        }
        response = self.session.post('https://twitter.com/i/api/2/oauth2/authorize', headers=headers, data=data)
        logger.info(f'【{self.index}】【{self.username}】授权推特步骤3:{response.text}')
        return auth_code

    def access(self):
        """解冻"""
        headers = {
            'authority': 'twitter.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'referer': 'https://twitter.com/account/access',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }
        cookies = {
            'auth_token': f'{self.token_info.get("auth_token")}',
            'ct0': f'{self.token_info.get("ct0")}',
        }
        response = self.session.get('https://twitter.com/account/access', cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        authenticity_token = soup.find('input', name='authenticity_token')['value']
        assignment_token = soup.find('input', name='assignment_token')['value']
        headers = {
            'authority': 'twitter.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://twitter.com',
            'pragma': 'no-cache',
            'referer': 'https://twitter.com/account/access',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }
        data = {
            'authenticity_token': f'{authenticity_token}',
            'assignment_token': f'{assignment_token}',
            'lang': 'en',
            'flow': '',
        }
        response = requests.post('https://twitter.com/account/access', cookies=cookies, headers=headers, data=data, allow_redirects=False)
        if response.status_code == 302:
            logger.info("解冻成功！")
        else:
            logger.info("解冻失败！")


def qg_task(index, em, un, pw, ph, token_info):
    qt = QTwitter(index=index, email=em, password=pw, username=un, phone=ph, token_info=token_info)
    # # 邮箱登录的方式
    # qt.login_by_email()
    # # 用户名登录的方式
    qt.login_by_username()
    if qt.inbox_initial_state():
        # qt.save_user_token_info("../wallets/twitter/tw_google_79_部分_提取结果.txt")
        qt.save_user_token_info("../wallets/twitter/100推-提取结果2.txt")
    # qt.access()
    # # 加载已登录token信息
    # qt.init_by_token()
    # qt.set_no_pro()
    # # 授权推特
    # params = {
    #     'code_challenge': '2wfuO6fwJP',
    #     'code_challenge_method': 'plain',
    #     'client_id': 'dUJhbkUzT0tSYjRjV0pfczhVTU46MTpjaQ',
    #     'redirect_uri': 'https://api.intract.io/api/qv1/auth/oauth/twitter/callback',
    #     'response_type': 'code',
    #     'scope': 'tweet.read users.read follows.read like.read offline.access space.read',
    #     'state': 'JTdCJTIydCUyMiUzQXRydWUlMkMlMjJ2JTIyJTNBJTIyMndmdU82ZndKUCUyMiUyQyUyMnAlMjIlM0ElMjJhYjVjNDVhMC1kZWU3LTRkNjYtYmJiOS0wZjIyZDAwZjA5YTAlMjIlMkMlMjJkJTIyJTNBJTIyaHR0cHMlM0ElMkYlMkZxdWVzdC5pbnRyYWN0LmlvJTJGJTIyJTJDJTIydGMlMjIlM0ElMjJkVUpoYmtVelQwdFNZalJqVjBwZmN6aFZUVTQ2TVRwamFRJTIyJTdE',
    # }
    # qt.authorize(params)

    # follow_user = "taikoxyz"
    # # # 关注指定用户
    # qt.follow_by_name(follow_user)
    # # 取关指定用户
    # qt.unfollow_by_name(follow_user)

    # follow_users = ["0xDripVerse"]
    # for u in follow_users:
    #     qt.follow_by_name(u)

    # # 批量关注
    # follow_users = ["Tabi_NFT", "READEMxyz", "TreasurelandNFT"]
    # for user in follow_users:
    #     qt.follow_by_name(user)

    # # 批量转推，喜欢
    # tweet_id1 = ["1673318394328940544"]
    # for tid in tweet_id1:
    #     qt.like(tid)
    #     # qt.retweet(tid)

    # # 回复某条推特
    # # content = "回复内容xxxxxxxxxxxxx"
    # # qt.reply_tweet(tweet_id,content)

    # 修改密码
    # new_password = "Qq666666"
    # qt.change_password(new_password)
    # qt.save_user_token_info("../wallets/twitter/推特登录保存结果5.txt")


if __name__ == '__main__':

    # file_data = open('../wallets/twitter/推特登录保存结果1-2.txt', 'r').readlines()
    # file_data = open('tw.txt', 'r').readlines()
    # file_data = open('../wallets/twitter/tw400.txt', 'r').readlines()
    # ws = QGFile.txt_to_array("../wallets/twitter/tw_google_79_提取结果.txt")
    # adds = [x[0] for x in ws]
    # file_data = open('../wallets/twitter/tw_google_10.txt', 'r').readlines()
    file_data = open('../wallets/twitter/100推特.txt', 'r').readlines()
    # file_data = open('../wallets/twitter/tw400-1.txt', 'r').readlines()
    # file_data = open('../wallets/twitter/tw_google_79_部分_提取结果.txt', 'r').readlines()
    indexs = [x[0] for x in QGFile.txt_to_array("../wallets/twitter/100推-提取结果.txt")]
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    for i, row in enumerate(file_data, start=1):
        info = row.split('----')
        em1 = info[1].strip()
        un1 = info[2].strip()
        pw1 = info[3].strip()
        ph1 = info[4].strip()
        # tk_info1 = ast.literal_eval(info[5].strip())
        tk_info1 = {}
        if 1 <= i <= 100:
            # if str(i) not in indexs and i <= 20:
            # qg_task(i, em1, un1, pw1, ph1, tk_info1)
            executor.submit(qg_task, i, em1, un1, pw1, ph1, tk_info1)
