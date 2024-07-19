import time

import requests
from loguru import logger

from qg_toolkit.tools.date_util import DateTool


class CuiQiuClient:
    """脆球客户端"""

    def __init__(self, token=None, domain_id=None, mail_id=None):
        self.token = token
        self.domain_id = domain_id
        self.mail_id = mail_id
        self.init()

    def init(self):
        if not self.token:
            # 获取当前文件所在目录的绝对路径
            # current_dir = os.path.dirname(os.path.abspath(__file__))
            # # 构建配置文件的路径
            # config_path = os.path.join(current_dir, "../config/env.yaml")
            # config = ConfigManager(config_path)
            # cq = config.get_value('qg.cq')
            # self.domain_id = cq['domain_id']
            # self.mail_id = cq['mail_id']
            # self.token = cq['token']
            self.domain_id = "16202"
            self.mail_id = "631957"
            self.token = "e265b3c708a1486bad1c48849fb61579"

    def mail_list(self, mail=""):
        """获取邮箱列表"""
        url = "https://domain-open-api.cuiqiu.com/v1/mail/list"
        payload = {
            'token': self.token,
            'domain_id': self.domain_id,
            'page': '1',
            'limit': '20',
            'mail': mail
        }
        response = requests.request("POST", url, data=payload)
        logger.info(response.text)
        return response.json()['data']

    def aliases_mail(self, mail=""):
        """根据邮箱名获取邮箱id"""
        url = "https://domain-api.cuiqiu.com/v1/aliases/mail"
        data = {
            'page': '1',
            'limit': '20',
            'mail': mail,
            'mark': '',
            'domainId': self.domain_id,
            'sort_value': 'id',
            'sort_type': 'desc',
            'domain_id': self.domain_id,
            'token': self.token,
        }
        response = requests.post(url, data=data)
        logger.info(response.text)

    def box_list(self, to_mail="", title=None):
        """获取邮件列表"""
        url = "https://domain-open-api.cuiqiu.com/v1/box/list"
        try:
            payload = {
                'token': self.token,
                'mail_id': self.mail_id,
                'start_time': DateTool.offset('%Y-%m-%d', 'H', 0),
                'end_time': DateTool.offset('%Y-%m-%d', 'H', 1),
                'folder': 'Inbox',
                'subject': title,
                'to': to_mail,
                'page': '1',
                'limit': '20'
            }
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload)
            return response.json()["data"]["list"]
        except Exception as e:
            logger.info(e)
            return None

    def box_detail(self, box_id):
        """获取邮件详情"""
        url = "https://domain-open-api.cuiqiu.com/v1/box/detail"
        payload = {
            'token': self.token,
            'mail_id': self.mail_id,
            'box_id': box_id,
        }
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()["data"]

    def domain_list(self):
        """获取域名列表"""
        url = "https://domain-open-api.cuiqiu.com/v1/domain/list"
        payload = {
            'token': self.token,
            'page': '1',
            'limit': '10'
        }
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info(response.text)

    def search_cq_email(self, my_mail, title, cs=20):
        """job 管理"""
        for x in range(cs):
            logger.info(f"【{my_mail}】：开始第{x + 1}次尝试查找邮箱")
            box_list = self.box_list(my_mail, title)
            if box_list:
                logger.info(str(box_list))
                box_list = list(filter(lambda x: title in x['subject'], box_list))
                logger.info(f"【{my_mail}】找到收件啦啦！")
                box_info = self.box_detail(box_list[0]["id"])
                return box_info["content"]["body"]
                # soup = BeautifulSoup(box_info["content"]["body"], features="lxml")
                # code = soup.find('h1').text
                # logger.info(f"【{my_mail}】验证地址：{code}")
            time.sleep(5)
        return None

    def search_cq_email_v2(self, my_mail, title, cs=20):
        """job 管理"""
        if "gmailiil.com" not in my_mail:
            return None
        for x in range(cs):
            time.sleep(5)
            logger.info(f"开始第{x + 1}次尝试查找邮箱")
            box_list = self.box_list(my_mail)
            logger.info(str(box_list))
            if box_list:
                box_list = list(filter(lambda x: title in x['subject'], box_list))
                logger.info(f"{my_mail}找到收件啦啦！")
                box_info = self.box_detail(box_list[0]["id"])
                return box_info["content"]["body"]
                # soup = BeautifulSoup(box_info["content"]["body"], features="lxml")
                # code = soup.find('h1').text
                # logger.info(f"【{my_mail}】验证地址：{code}")
        return None
