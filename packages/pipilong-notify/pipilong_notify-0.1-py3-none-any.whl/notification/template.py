from typing import Dict, List, Type
from notification.abstractNotifyTemplate import AbstractNotifyTemplate


class Text(AbstractNotifyTemplate):
    """
    文本格式的消息类型

    Attributes
    ----------
    content : str
        要发送的消息内容
    at : str
        @用户类型

    Methods
    -------
    set_content():
        设置消息内容
    to_array():
        格式转换
    """
    content: str
    at: Dict = {
        "isAtAll": False
    }

    def __init__(
            self,
            content: str = None,
            at: Dict = None
    ):
        self.content = content
        self.at = at

    def set_content(self, content: str):
        self.content = content
        return self

    def to_array(self):
        return {
            "at": self.at,
            "text": {
                "content": self.content
            },
            "msgtype": "text"
        }


class Link(AbstractNotifyTemplate):
    """
    链接类型
    Attributes
    ----------
    title:str
        消息标题
    content :str
        消息内容。如果太长只会部分展示
    pic_url: str
        图片URL
    message_url: str
        点击消息跳转的URL
    """
    at: Dict = {
        "isAtAll": False
    }
    content: str
    title: str
    message_url: str = None
    pic_url: str = None

    def __init__(
            self,
            title: str = None,
            content: str = None,
            message_url: str = None,
            pic_url: str = None,
            at: Dict = None
    ):
        self.content = content
        self.at = at
        self.title = title
        self.pic_url = pic_url
        self.message_url = message_url

    def set_content(self, content: str):
        self.content = content
        return self

    def to_array(self):
        return {
            "msgtype": "link",
            "link": {
                "text": self.content,
                "title": self.title,
                "picUrl": self.pic_url,
                "messageUrl": self.message_url
            }
        }


class Markdown(AbstractNotifyTemplate):
    """
    富文本类型
     Attributes
    ----------
    title:str
        首屏会话透出的展示内容
    text: str
        markdown格式的消息
    """
    at: Dict = {
        "isAtAll": False
    }
    title: str
    text: str

    def __init__(self, title: str = None, text: str = None):
        if title is not None:
            self.title = title
        if text is not None:
            self.text = text

    def to_array(self):
        return {
            "msgtype": "markdown",
            "markdown": {
                "title": self.title,
                "text": self.text
            },
            "at": self.at
        }


class ActionCard(AbstractNotifyTemplate):
    """
    整体跳转 ActionCard 类型
    Attributes
    ----------
    title:str
        首屏会话透出的展示内容
    text: str
        markdown格式的消息
    single_title:str
        单个按钮的标题
    single_url:str
        点击消息跳转的URL
    btn_orientation:str
        按钮排列方式
    """
    at: Dict = {
        "isAtAll": False
    }
    title: str
    text: str
    btn_orientation: str
    single_title: str
    single_url: str

    def __init__(
            self,
            title: str,
            text: str,
            btn_orientation: str,
            single_title: str,
            single_url: str
    ):
        self.title = title
        self.text = text
        self.btn_orientation = btn_orientation
        self.single_title = single_title
        self.single_url = single_url

    def to_array(self):
        return {
            "actionCard": {
                "title": self.title,
                "text": self.text,
                "btnOrientation": self.btn_orientation,
                "singleTitle": self.single_title,
                "singleURL": self.single_url
            },
            "msgtype": "actionCard"
        }


class FeedCard(AbstractNotifyTemplate):
    """
    FeedCard 类型
    Attributes
    ----------
    links:List[Dict[str, str]]
            参数示例{
                "title": "时代的火车向前开1",
                "messageURL": "https://www.dingtalk.com/",
                "picURL": "https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png"
            },
    """
    links: List[Dict[str, str]]

    def __init__(self, link:List[Dict[str, str]]):
        self.links = link

    def to_array(self):
        return {
            "msgtype": "feedCard",
            "feedCard": {
                "links": self.links
            }
        }
