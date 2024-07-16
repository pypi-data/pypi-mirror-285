# -*- encoding=utf8 -*-

__author__ = "uwa"

import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import unittest
from airtestProject.airtest.core.api import *

auto_setup(__file__)

# 导入UWA模块
from airtestProject.commons.UWA import *
from airtestProject.poco.drivers.android.uiautomation import AndroidUiautomationPoco
from airtestProject.commons.utils.page import Page
# 获取 UWA Pipeline 中的信息必须导入run_airtest_config模块
# import run_airtest_config
import logging
from airtestProject.commons.utils.logger import log as logger_log
# deviceID = device().uuid

class TestGot():

    @logger_log.wrap("正在启动游戏")
    def got_init(self, apk_name):
        try:
            stop_app("com.netease.open.pocoservice")
            sleep(2)
            start_app("com.netease.open.pocoservice")
        except:
            logger_log.step("启动失败")
        sleep(5)

        a_poco = AndroidUiautomationPoco()            # 初始化 原生 poco 对象

        try:
            home()
            stop_app(apk_name)
        except:
            logger_log.step("APP is not running")

        start_app(apk_name)     # 运行App
        sleep(10)
        permission_buttons = [
            "同意",
            "允许",
            "始终允许",
            "总是允许",
            "立即开始",
            "确定",
            "稍后"
        ]

        logger_log.test("进行权限验证")
        for i in range(5):
            for button in permission_buttons:         # 权限校验
                if a_poco(text=button).exists():
                    a_poco(text=button).click()
                sleep(0.1)
        logger_log.test("权限验证结束")
        sleep(10)

    def got_connect(self, poco):
        GOT_Test.Connect(poco)
        sleep(3)
        logger_log.step("连接got")

    def got_start(self, poco, mode):
        GOT_Test.Start(poco, mode)
        logger_log.step("开始执行测试用例")

    def got_stop(self, poco):
        GOT_Test.Stop(poco)                   # 关闭 GOT 模式()
        logger_log.step("开始上传")
        sleep(10)

    def got_upload(self, poco):
        GOT_Test.Upload(poco, 3000)  # 运行结束后自动上传至UWA官网()
        logger_log.step("上传结束")
        sleep(2)

    def stop_app(self,apk_name):
        stop_app(apk_name)  # 退出 App

    @staticmethod
    def sb():
        from poco.drivers.unity3d import UnityPoco
        # global poco

        poco = UnityPoco()
        return poco


    # def get_pipeline_info(self):
    #     """仅支持在UWA Pipeline中的Pipeline(流水线)中使用"""
    #     log("获取 设备信息")
    #     device_info = run_airtest_config.device_info
    #     log(f"设备信息为:{device_info}")
    #
    #     log("获取 package name")
    #     package_name = run_airtest_config.package_name
    #     log(f"包名的值为:{package_name}")
    #
    #     # UWA Pipeline 参数化构建与自动化测试脚本结合使用
    #     log("获取 参数化构建中设置的默认值")
    #     param_dict = {}
    #     custom_param = run_airtest_config.custom_param
    #     for custom_param_dict in custom_param:
    #         param_dict[custom_param_dict['name']] = custom_param_dict['value']
    #
    #     Name = param_dict['Name']
    #     # Out: UWA
    #     log(f"参数化构建中Name参数的值为:{Name}")
    #
    #     BoolValue = param_dict['BoolValue']
    #     # Out: False
    #     log(f"参数化构建中BoolValue参数的值为:{BoolValue}")       # 获取UWA Pipeline中信息的接口
if __name__ == '__main__':
    TestGot().got_init("com.sanqi.odin2022.weekly")