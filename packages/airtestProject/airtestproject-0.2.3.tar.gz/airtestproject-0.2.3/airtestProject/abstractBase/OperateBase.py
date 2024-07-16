#!-*- coding = utf-8 -*-
# @Time : 2024/4/7 2:44
# @Author : 苏嘉浩
# @File : OperateBase.py
# @Software : PyCharm
from abc import ABC, abstractmethod

"""
airtest核心api和poco的二次封装，操作具体基类
"""


class OperateABC(ABC):

    @abstractmethod
    def click(self, value, *args, **kwargs):
        """
        :param value:
        :param args:
        :param kwargs: ocrPlus=True,可以开启二值化
        :return:
        """
        pass

    @abstractmethod
    def exists(self, pos, **kwargs):
        """

        :param pos: 传入的元素
        :param kwargs: 如果是使用ocr可以传入ocrPlus=True,可以开启二值化
        :return:
        """
        pass

    @abstractmethod
    def sleep(self, secs):
        """

        :param secs: 延迟秒数
        :return:
        """
        pass

    @abstractmethod
    def swipe(self, value, v2=None, vector_direction=None, **kwargs):
        """

        :param value: 要滑动的元素
        :param v2: airtest可以选填滑动到的元素（poco其实底层也是有两个元素的，但是封装后现在没有，后续考虑airtest也去掉第二个元素）
        :param vector_direction: （按比例滑动）
        :param kwargs: 定义参数，熟悉poco的可以自己添加
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def pinch(self, in_or_out, percent=0.5, **kwargs):
        """

        :param in_or_out: 缩放方向in就是里面out就是往外
        :param percent: 屏幕捏动百分比
        :param kwargs: airtest和poco还有一些小参数可以自己定义
        :return:
        """
        pass

    @abstractmethod
    def set_text(self, pos, text, *args, **kwargs):
        pass

    @abstractmethod
    def wait(self, pos, timeout=None, *args, **kwargs):
        pass

    @abstractmethod
    def wait_disappear_element(self, pos, *args, **kwargs):
        """
        等待元素消失
        :param pos: 元素
        :param args:
        :param kwargs:
        :return:
        """
        pass

    @abstractmethod
    def wait_element_appear(self, pos, *args, **kwargs):
        """
        等待元素出现
        :param pos:
        :param args:
        :param kwargs:
        :return:
        """
        pass

    @abstractmethod
    def persistent_element_exists(self, pos):
        """
        暂时未实现，判断元素是否一直存在
        :param pos:
        :return:
        """
        pass

    def set_dict(self, script_root, project):
        """
        图片识别需要设定路径用文件名代替路径
        :param script_root: 脚本当前目录
        :param project: 定位到的具体图片文件夹
        :return:
        """
        pass

    @abstractmethod
    def wait_for_any(self, pos_list: list, timeout=30):
        """
        等待列表中的某一个元素
        :param pos_list: 元素列表
        :param timeout:
        :return:
        """
        pass

    @abstractmethod
    def wait_for_all(self, pos_list: list, timeout=30):
        """

        :param pos_list: 等待列表中的全部元素
        :param timeout:
        :return:
        """
        pass

    @abstractmethod
    def wait_next_element(self, last_click_pos, next_pos):
        """
        等待下一个元素，没有出现就点击上一个
        :param last_click_pos: 上一个需要点击的元素
        :param next_pos: 下一个元素
        :return:
        """
        pass

    @abstractmethod
    def get_text(self, pos):
        """
        获取元素的文本内容，airtest暂未实现
        :param pos: 元素
        :return:
        """
        pass

# class OperateClass:
#     def __init__(self, operate: OperateABC):
#         self.operate = operate
