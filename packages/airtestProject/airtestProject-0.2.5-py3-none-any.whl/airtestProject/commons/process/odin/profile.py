import time

from airtestProject.commons.page.odin.login import LoginPage
from airtestProject.commons.utils.gotCommon import TestGot
from airtestProject.commons.UWA import *
from airtestProject.commons.utils.logger import log
# from poco.drivers.unity3d import UnityPoco


class OdinProfile:

    def __init__(self):
        self.odin_poco_apk = "com.sanqi.odin.poco"
        self.odin_weekly_apk = "com.sanqi.odin.weekly"
        self.odin_2022weekly_apk = "com.sanqi.odin2022.weekly"
        self.odin_uwa_apk = "com.sanqi.odinUWA"
        self.odin_2022uwa_apk = "com.sanqi.odin2022.uwa"
        self.got = TestGot()
        # self.mainPage = MainPage()

    @log.wrap("跑图并上传UWA")
    def test_running_uwa(self):
        self.got.got_init(self.odin_2022uwa_apk)
        # 登录
        # self.loginPage.
        # 点击跑图
        # self.mainPage.start_running_1()
        # 开启got

        # # poco = UnityPoco()
        # self.got.got_start(poco, "default")
        # # 开始跑图
        # # self.mainPage.start_running_2()
        # # 停止got
        # self.got.got_stop(poco)
        # GOT_Test.LocalUpload(poco, account='wangmo@37.com', password='37youxi123456', projectID=1775,
        #                      timeLimitS=300)
        # 上传报告
        # self.got.got_upload(poco)
        # 杀进程
        stop_app(self.odin_poco_apk)

    @log.wrap("跑checklist")
    def test_check_list(self):
        self.got.got_init(self.odin_2022uwa_apk)
        # 登录



if __name__ == '__main__':
    odin = OdinProfile()
    odin.test_running_uwa()
