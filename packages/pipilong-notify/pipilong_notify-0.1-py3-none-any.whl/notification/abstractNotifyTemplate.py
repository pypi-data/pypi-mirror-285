from abc import ABC, abstractmethod


class AbstractNotifyTemplate(ABC):
    def to_array(self):
        """
        转换为符合要求的请求体
        """
        pass