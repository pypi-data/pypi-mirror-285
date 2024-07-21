import base64
import hashlib
import hmac
import logging
import os
import time
import requests
import urllib.parse

from dotenv import load_dotenv
from rich.logging import RichHandler
from notification.abstractNotifyTemplate import AbstractNotifyTemplate


class DingTalk:

    def __init__(
            self,
            access_token: str = None,
            secret: str = None,
            base_url: str = None,
    ) -> None:
        FORMAT = "%(message)s"
        logging.basicConfig(
            level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
        )
        self.logger = logging.getLogger("rich")

        if base_url is None:
            self.base_url = "https://oapi.dingtalk.com/robot/send"

        self.get_config()

        if access_token is None:
            access_token = os.environ.get("DING_ACCESS_TOKEN")
        if access_token is None:
            raise Exception(
                "access_token未指定"
            )
        self.access_token = access_token
        if secret is None:
            secret = os.environ.get("DING_SECRET")
        if secret is None:
            raise Exception(
                "secret未指定"
            )
        self.secret = secret

    def __sign(self):
        """
        拼接timestamp和sign参数
        返回示例： https://oapi.dingtalk.com/robot/send?access_token=XXXXXX&timestamp=XXX&sign=XXX
        """
        timestamp = str(round(time.time() * 1000))
        secret = self.secret
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        return (self.base_url + '?'
                + 'access_token=' +
                self.access_token +
                "&timestamp=" + timestamp +
                '&sign=' + urllib.parse.quote_plus(base64.b64encode(hmac_code))
                )

    def notify(self, option: AbstractNotifyTemplate):
        """
        发送通知
        Parameters
        ----------
        option : AbstractNotifyTemplate
            实现AbstractNotifyTemplate类的模版实例
        """
        try:
            url = self.__sign()
            header = {"Content-Type": "application/json"}
            response = requests.post(url=url, json=option.to_array(), headers=header)
            result = response.json()
            if result['errcode'] != 0:
                raise Exception(result['errmsg'])
            self.logger.info('消息发送成功')
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    def get_config(self):
        load_dotenv()
        # if os.getenv('DING_ACCESS_TOKEN') is None:
        #     raise Exception('未配置ACCESS_TOKEN')
        #
        # if os.getenv('DING_SECRET') is None:
        #     raise Exception('未配置密钥')
