import time
import requests
from loguru import logger

class YesCaptcha:
    requests.packages.urllib3.disable_warnings()
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    }

    def __init__(self, client_key, website_key, website_url, task_type="NoCaptchaTaskProxyless"):
        self.client_key = client_key
        self.website_key = website_key
        self.website_url = website_url
        self.task_type = task_type

    def create_task(self, args=None) -> str:
        """
        第一步，创建验证码任务
        :param
        :return taskId : string 创建成功的任务ID
        """
        url = "https://api.yescaptcha.com/createTask"
        data = {
            "clientKey": self.client_key,
            "task": {
                "websiteURL": self.website_url,
                "websiteKey": self.website_key,
                "type": self.task_type
            }
        }
        if args:
            data["task"].update(args)
        # logger.info(f'传参：{data}')
        try:
            # 发送JSON格式的数据
            result = requests.post(url, json=data, verify=False, headers=self.headers).json()
            taskId = result.get('taskId')
            if taskId is not None:
                return taskId
            logger.info(result)

        except Exception as e:
            logger.info(e)

    def get_response(self, taskID: str):
        """
        第二步：使用taskId获取response
        :param taskID: string
        :return response: string 识别结果
        """

        # 循环请求识别结果，3秒请求一次
        times = 0
        while times < 120:
            try:
                url = f"https://api.yescaptcha.com/getTaskResult"
                data = {
                    "clientKey": self.client_key,
                    "taskId": taskID
                }
                result = requests.post(url, json=data, verify=False, headers=self.headers).json()
                solution = result.get('solution', {})
                if solution:
                    response = solution.get('gRecaptchaResponse')
                    if response:
                        logger.info(result)
                        return response
            except Exception as e:
                logger.info(e)
            times += 3
            time.sleep(3)

    def get_response2(self, taskID: str):
        """
        第二步：使用taskId获取response
        :param taskID: string
        :return response: string 识别结果
        """
        # 循环请求识别结果，3秒请求一次
        times = 0
        while times < 120:
            try:
                url = f"https://api.yescaptcha.com/getTaskResult"
                data = {
                    "clientKey": self.client_key,
                    "taskId": taskID
                }
                result = requests.post(url, json=data, verify=False, headers=self.headers).json()
                solution = result.get('solution', {})
                if solution:
                    logger.info(result)
                    return solution
                    # response = solution.get('gRecaptchaResponse')
                    # if response:
                    #     logger.info(result)
                    #     return response
            except Exception as e:
                logger.info(e)
            times += 3
            time.sleep(3)

    def get_recaptcha(self, args=None):
        taskId = self.create_task(args)
        logger.info('创建任务:', taskId)
        if taskId is not None:
            response = self.get_response(taskId)
            logger.info('识别结果:', response)
            return response

    def get_solution(self, args=None):
        taskId = self.create_task(args)
        logger.info('创建任务:', taskId)
        if taskId is not None:
            solution = self.get_response2(taskId)
            logger.info('识别结果:', solution)
            return solution
