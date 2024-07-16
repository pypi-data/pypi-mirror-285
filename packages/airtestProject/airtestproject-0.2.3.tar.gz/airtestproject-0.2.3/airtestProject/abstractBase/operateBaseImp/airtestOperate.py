"""
airtest核心api的二次封装，操作具体实现类
"""
import os

from airtestProject.airtest.core import api as air
from airtestProject.airtest.core.error import TargetNotFoundError

from airtestProject.commons.utils.logger import log
from airtestProject.abstractBase.OperateBase import OperateABC
import time

from airtestProject.commons.utils.myTemplate import myTemplate
from airtestProject.commons.utils.ocrTemplate import OcrTemplate
from airtestProject.commons.utils.tools import get_folder_path_up


class myAirTest(OperateABC):

    def __init__(self, language):
        super(myAirTest, self).__init__()
        self.this_dict = None
        self.language = language

    def set_dict(self, script_root: str, project: str):
        """
        各种兼容还有路径转换。ps images文件夹只能在脚本的上级或者同级否则无法正常工作
        :param script_root: 脚本当前目录
        :param project: 定位到的具体图片文件夹
        :return:
        """
        if self.this_dict is None:
            files_dict = {}
            images_abs_path = get_folder_path_up(script_root, 'images')  # 获取图片文件夹的绝对路径
            # script_root_dir = os.path.dirname(script_root)  # 获取脚本文件夹的绝对路径
            # images_relative_path = os.path.relpath(images_abs_path, script_root_dir)  # 构造为图片文件夹的相对路径
            images_project_relative_path = os.path.join(images_abs_path, project)  # 构造为图片文件夹和project的相对路径
            # 遍历指定目录下的所有文件
            for filename in os.listdir(images_project_relative_path):
                file_path = os.path.join(images_project_relative_path, filename)
                if os.path.isfile(file_path):
                    file_name_without_ext, _ = os.path.splitext(filename)
                    files_dict[file_name_without_ext] = myTemplate(file_path)
            print(files_dict)
            self.this_dict = files_dict

    def init_device(self, platform=None, uuid=None, **kwargs):
        try:
            air.init_device(platform=platform, uuid=uuid, **kwargs)
            log.info(f"init device success, platform: {platform}, uuid:  {uuid}")
        except Exception as e:
            log.error(f"failed to init device, platform: {platform}, uuid:  {uuid}")
            raise e

    def connect_device(self, uri):
        log.info('🍇 🍉 ready to connect device host ...')
        try:
            air.connect_device(uri)
            log.info(f'🍊 🍋 connect device succeeded... host: {uri}')
        except ConnectionError as e:
            log.error(f'connect device failed... host: {uri}')
            raise ConnectionError from e

    def device(self):
        current_active_device = air.device()
        log.info(f'get current active device: {current_active_device}')
        return current_active_device

    def set_current(self, idx):
        try:
            log.info(f"set current active device idx: {idx}")
            air.set_current(idx)
        except Exception as e:
            log.error(f"failed to set current active device idx: {idx}")
            raise e

    def auto_setup(self, basedir=None, devices=None, logdir=None, project_root=None, compress=None):
        air.auto_setup(basedir=basedir, devices=devices, logdir=logdir, project_root=project_root, compress=compress)

    def shell(self, cmd):
        try:
            log.info(f"execute adb shell command: {cmd}")
            return air.shell(cmd)
        except Exception as e:
            log.error(f"failed to execute adb shell command: {cmd}")
            raise e

    def start_app(self, package, activity=None):
        try:
            air.start_app(package, activity)
            log.info(f"start app: {package}, activity: {activity}")
        except Exception as e:
            log.error(f"failed start app {package}, activity: {activity}")
            raise e

    def stop_app(self, package):
        try:
            air.stop_app(package)
            log.info(f"stop the application on device, package: {package}")
        except Exception as e:
            log.error(f"failed to stop the application on device, package: {package}")
            raise e

    def clear_app(self, package):
        try:
            air.clear_app(package)
            log.info(f"clear data of the application on device, package: {package}")
        except Exception as e:
            log.error(f"failed to clear data of the application on device, package: {package}")
            raise e

    def install(self, filepath, **kwargs):
        try:
            log.info(f"install application: {filepath}")
            return air.install(filepath, **kwargs)
        except Exception as e:
            log.error(f"failed to install application: {filepath}")
            raise e

    def uninstall(self, package):
        try:
            log.info(f"uninstall application: {package}")
            return air.uninstall(package)
        except Exception as e:
            log.error(f"failed to uninstall application: {package}")
            raise e

    def snapshot(self, filename=None, msg="", quality=None, max_size=None):
        try:
            log.info(f"take the screenshot of the device and save it to the filepath:{filename}.")
            return air.snapshot(filename, msg, quality, max_size)
        except Exception as e:
            log.error(f"failed to wake up and unlock the device")
            raise e

    def wake(self):
        try:
            log.info(f"wake up and unlock the device")
            return air.wake
        except Exception as e:
            log.error(f"failed to wake up and unlock the device")
            raise e

    def home(self, package):
        raise NotImplementedError

    def click(self, value, times=1, ocrPlus=False, **kwargs):
        try:
            log.info(f"perform the touch action on the device screen, pos: {value}")
            if 'focus' in kwargs.keys():
                del kwargs['focus']
            value = self.check_value(value, ocrPlus)
            return air.touch(value, times, **kwargs)
        except Exception as e:
            log.error(f"failed to perform the touch action on the device screen, pos: {value}")
            raise e

    def double_click(self, v1, v2=None, vector=None, **kwargs):
        log.info(f"perform double click")
        return air.double_click(v1, v2, vector, **kwargs)

    def swipe(self, value, v2=None, vector_direction=None, **kwargs):
        if vector_direction is None:
            vector_direction = [0, -3.0]
        log.info("Perform the swipe action on the device screen.")
        value = self.check_value(value)
        if v2 is not None:
            v2 = self.check_value(v2)
        return air.swipe(value, v2, vector=vector_direction, **kwargs)

    def pinch(self, in_or_out='in', percent=0.5, center=None):
        log.info(f"perform the pinch action on the device screen")
        return air.pinch(in_or_out, center, percent)

    def keyevent(self, keyname, **kwargs):
        log.info(f"perform key event keyname: {keyname} on the device.")
        return air.keyevent(keyname, **kwargs)

    def set_text(self, pos=None, text=None, enter=True, **kwargs):
        try:
            self.click(pos)
            log.info(f"input {text} on the target device")
            for i in range(20):
                air.keyevent("KEYCODE_DEL")
                log.info(f"我在删除")
            return air.text(text, enter, **kwargs)
        except Exception as e:
            log.error(f"failed to input {text} on the target device")
            raise e

    def sleep(self, secs=1.0):
        time.sleep(secs)
        log.info(f'time sleep {secs} seconds')

    def wait(self, pos, timeout=None, interval=0.5, intervalfunc=None):
        try:
            log.info(f"input {pos} on the target device")
            pos = self.check_value(pos)
            return air.wait(pos, timeout, interval, intervalfunc)
        except Exception as e:
            log.error(f"failed to input {pos} on the target device")
            raise e

    def wait_disappear_element(self, pos, *args, **kwargs):
        start_loading_time = time.time()
        while self.exists(pos) is not False:
            if time.time() - start_loading_time > 180:
                log.info(f"{pos}存在超时，请注意查看")
                return False
        log.info(f"{pos}消失")
        return True

    def wait_element_appear(self, pos, *args, **kwargs):
        start_loading_time = time.time()
        while self.exists(pos) is False:
            if time.time() - start_loading_time > 180:
                log.info(f"{pos}寻找超时，请注意查看")
                return False
        log.info(f"{pos}出现")
        return True

    def exists(self, pos, ocrPlus=None, **kwargs):
        try:
            log.info(f"the node: {pos} exists.")
            if ocrPlus is None:
                ocrPlus = False
            pos = self.check_value(pos, ocrPlus)
            return air.exists(pos)
        except Exception as e:
            log.error(f"the node: {pos} not exists.")
            raise e

    def persistent_element_exists(self, pos):
        pass

    def wait_for_any(self, pos_list: list, timeout=30):
        """

        :param pos_list: 需要等待的列表元素
        :param timeout: 超出时长
        :return:
        """
        start = time.time()
        while True:
            for pos in pos_list:
                if self.exists(pos):
                    return pos
            if time.time() - start > timeout:
                raise TargetNotFoundError(f'any to appear{pos_list}')

    def wait_for_all(self, pos_list: list, timeout=30):
        start = time.time()
        while True:
            all_exist = True
            for pos in pos_list:
                if not self.exists(pos):
                    all_exist = False
                    break
            if all_exist:
                return
            if time.time() - start > timeout:
                raise TargetNotFoundError(f'all to appear{pos_list}')

    def wait_next_element(self, last_click_pos, next_pos):
        """
        等待下一个元素出现
        :param last_click_pos: 需要点击的元素
        :param next_pos: 将会出现的元素
        :return:
        """
        start_time = time.time()
        while self.exists(next_pos) is False:
            log.info(f"{next_pos}没有出现正在尝试点击")
            self.click(last_click_pos)
            air.sleep(0.5)
            if time.time() - start_time > 180:
                log.info(f"{next_pos}没有出现")
                return False
        return True

    def get_text(self, pos):

        pass

    def check_value(self, val, ocrPlus=False):
        """
        用于判定是否是可以直接使用字典取值。如果不可以判断是否为文件夹路径是的话采用图片识别
        :param ocrPlus: 主要用于传递是否开启增强识别(不一定增强)
        :param val: 需要检查的参数
        :return:
        """
        if isinstance(val, str):
            dict_value = None
            if self.this_dict:
                dict_value = self.this_dict.get(val)
            if dict_value is not None:
                return dict_value
            log.info(f"字典中不存在{val}对应的路径")
            return myTemplate(val) if os.path.isfile(val) else OcrTemplate(val, language=self.language, ocrPlus=ocrPlus)
        return val


if __name__ == '__main__':
    air.sleep()
