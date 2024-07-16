"""
基于poco对象、二次封装的操作方法
"""
from airtestProject.commons.utils.logger import log
from airtestProject.commons.utils.exception import NoSuchNodeException
from airtestProject.poco.exceptions import PocoNoSuchNodeException, PocoTargetRemovedException
from airtestProject.abstractBase.OperateBase import OperateABC

from airtestProject.poco.drivers.unity3d import UnityPoco
import re
import time

identifier: str = '-'
index_compile = re.compile(r'(?<=\[)\d+?(?=\])')


class myPoco(OperateABC):

    def __init__(self, poco_instance):

        self.poco = poco_instance or UnityPoco()

    def get_poco(self, pos):
        return self.parser_pos(pos)

    def tap_anywhere(self):
        log.step("tap anywhere on the screen to continue .")
        return self.poco.click([0.2, 0.82])

    def click(self, pos, focus=None, ocrPlus=False, sleep_interval: float = None):
        try:
            return self.parser_pos(pos).click(focus, sleep_interval)
        except PocoNoSuchNodeException:
            try:
                log.debug(f"try locating the node： {pos} again")
                return self.parser_pos(pos).click(focus, sleep_interval)
            except PocoNoSuchNodeException:
                raise NoSuchNodeException(f'cannot find visible node by query UIObjectProxy of "{pos}"')

    def exists(self, pos, **kwargs):
        try:
            kwargs.pop('ocrPlus', None)
            return self.parser_pos(pos).exists()
        except (PocoTargetRemovedException, PocoNoSuchNodeException):
            return False

    def long_click(self, pos: str, duration: float = 2.0):
        return self.parser_pos(pos).long_click(duration)

    # def double_click(self, pos: str, focus=None, sleep_interval: float = None):
    #     return self.parser_pos(pos).double_click(focus, sleep_interval)
    #
    # def rclick(self, pos: str, focus=None, sleep_interval: float = None):
    #     return self.parser_pos(pos).rclick(focus, sleep_interval)

    def swipe(self, value, v2=None, vector_direction=None, focus=None, duration: float = 0.5, **kwargs):
        if vector_direction is None:
            vector_direction = [0, -3.0]
        kwargs.pop('steps', None)
        kwargs.pop('fingers', None)
        return self.parser_pos(value).swipe(direction=vector_direction, focus=focus, duration=duration)

    def scroll(self, pos: str, direction='vertical', percent: float = 0.6, duration: float = 2.0):
        return self.parser_pos(pos).scroll(direction, percent, duration)

    def pinch(self, in_or_out='in', percent: float = 0.5, duration: float = 2.0, dead_zone: float = 0.1):
        return self.poco.pinch(in_or_out, percent, duration, dead_zone)

    def set_text(self, pos=None, text=None, **kwargs):
        return self.parser_pos(pos).set_text(text)

    def get_text(self, pos):
        return self.parser_pos(pos).get_text()

    def get_name(self, pos: str):
        return self.parser_pos(pos).get_name()

    def drag_to(self, pos: str, target: str, duration=0.5):
        return self.parser_pos(pos).drag_to(self.parser_pos(target), duration)

    def wait(self, pos, timeout=30, interval=None, wait_type="appearance"):

        if wait_type == 'appearance':
            return self.parser_pos(pos).wait_for_appearance(timeout)

        if wait_type == 'disappearance':
            return self.parser_pos(pos).wait_for_appearance(timeout)

    def wait_disappear_element(self, pos, *args, **kwargs):
        start_loading_time = time.time()
        while self.parser_pos(pos).exists() is not False:
            if time.time() - start_loading_time > 180:
                log.info(f"{pos}寻找超时，请注意查看")
                return False
        log.info(f"{pos}消失")
        return True

    def wait_element_appear(self, pos, *args, **kwargs):
        start_loading_time = time.time()
        while self.parser_pos(pos).exists() is False:
            if time.time() - start_loading_time > 180:
                log.info(f"{pos}寻找超时，请注意查看")
                return False
        log.info(f"{pos}出现")
        return True

    def persistent_element_exists(self, pos):
        pass

    def wait_for_any(self, pos_list: list, timeout=30):
        return self.poco.wait_for_any(self.parser_pos_list(pos_list), timeout)

    def wait_for_all(self, pos_list: list, timeout=30):
        return self.poco.wait_for_all(self.parser_pos_list(pos_list), timeout)

    def wait_for_appearance(self, pos, timeout=30):
        return self.parser_pos(pos).wait_for_appearance(timeout)

    def wait_for_disappearance(self, pos, timeout=30):
        return self.parser_pos(pos).wait_for_disappearance(timeout)

    def sleep(self, secs: float = 1.0):
        log.step(f"sleep {secs} seconds .")
        time.sleep(secs)

    def wait_next_element(self, last_click_pos, next_pos):
        start_time = time.time()
        while self.exists(next_pos) is False:
            self.click(last_click_pos)
            if time.time() - start_time > 180:
                log.info(f"{next_pos}无法进入")

    def regex_pos_index(self, pos: str):
        """
        正则匹配定位的下标
        :param pos:
        :return:
        """
        s = index_compile.search(pos)
        if s:
            index = s.group()
            rep_pos = pos.replace(f"[{index}]", "")
            return rep_pos, int(index)
        return pos, 0

    def parser_pos(self, pos: str):
        """
        解析pos定位，基于poco定位方式，支持更简便的一行式书写定位方法，支持五种定位方法；
        传入的pos为中文时，使用text文本定位，不以中文开头不会匹配text文本；
        属性定位与正则定位属于同一种书写方式，均采用关键字方式书写，例如：text=确定、textMatches=确定；
        传入的pos为元素时，使用普通方式定位，并且当存在多级定位时，使用 - 符号连结，程序自动拆解，并自动解析index；
        相对定位与顺序定位可结合使用，采用先切割后取值的方式解析定位，例如：Bg_Front[1]-Close；
        :param pos: 定位
        :return:
        example：
            基本定位："Btn_Enter"
            顺序定位："Bg_Front[1]"
            相对定位: "Bg_Front[1]-Close"
            属性定位："text=确定"
            正则定位："textMatches=确定"
        """

        if '=' in pos:
            attr, pos = pos.split('=')
            return self.poco(**{attr: pos})

        if identifier not in pos:
            if index_compile.search(pos):
                rep_pos, index = self.regex_pos_index(pos)
                return self.poco(rep_pos)[index]

            return self.poco(pos)

        value_list = pos.split(identifier)
        pos_list = [self.regex_pos_index(value) for value in value_list]

        p0, n0 = pos_list[0]
        p1, n1 = pos_list[1]

        return self.poco(p0)[n0].child(p1)[n1]

    def parser_pos_list(self, pos_list: list):
        poco_list = []

        for pos in pos_list:
            poco_list.append(self.poco(pos))

        return poco_list
