#!-*- coding = utf-8 -*-
# @Time : 2024/4/28 8:08
# @Author : 苏嘉浩
# @File : ocrTemplate.py
# @Software : PyCharm
import threading

import cv2
import easyocr
import numpy as np

import torch
from airtestProject.airtest import aircv
from airtestProject.airtest.core.cv import Template
from airtestProject.airtest.core.error import InvalidMatchingMethodError
from airtestProject.airtest.utils.transform import TargetPos
from airtestProject.airtest.core.helper import G, logwrap
from airtestProject.airtest.core.settings import Settings as ST  # noqa
from paddleocr import PaddleOCR
from airtestProject.commons.utils.setting import Setting as SS
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


class EasyOcr:
    def __init__(self, language=None):
        """
        :param language: 语言默认为中文和英文。可能会比较慢，后续可以建议为单引擎
        """
        if language is None:
            self.easy_language = ['en', 'ch_sim']
        else:
            self.easy_language = list(language)
            index = self.easy_language.index('ch')  # 找到 'ch' 的位置,easyocr的中文是分繁体简体
            self.easy_language[index] = 'ch_sim'
        self.reader = easyocr.Reader(self.easy_language, gpu=True)

    def ocr_match(self, img, input_text):
        # 读取图像

        result = self.reader.readtext(img)
        # 转为 {'result': (1606, 1116), 'rectangle': [(1271, 1046), (1271, 1187), (1941, 1187), (1941, 1046)],
        # 'confidence': 0.8403522074222565, 'time': 0.7186686992645264}
        result_list = []
        for res in result:
            result_dict = {}
            (bbox, text, prob) = res
            bbox = [(float(point[0]), float(point[1])) for point in bbox]
            (tl, tr, br, bl) = bbox
            center_x = (tl[0] + br[0]) / 2
            center_y = (tl[1] + br[1]) / 2
            result_dict['result'] = (center_x, center_y)
            result_dict['rectangle'] = bbox
            result_dict['confidence'] = prob
            result_dict['text'] = text
            result_list.append(result_dict)
        # for result_dict1 in result_list:
        #     if result_dict1['text'] == input_text:
        #         return result_dict1['result']
        # return False
        # 生成式等效于for循环
        print(result_list)
        coordinate = next((r_dict for r_dict in result_list if r_dict.get('text') == input_text), None)
        return coordinate


class PpOcr:
    """
    :param language: 默认为双引擎，会比较慢，可以针对项目启用单引擎（Odin中英文都有很难受）
    """

    def __init__(self, language=None):

        if language is None:
            self.ppOcr_languages = ['ch']
        else:
            self.ppOcr_languages = list(language)
        self.ocr_modules = [PaddleOCR(use_angle_cls=True, use_gpu=True, lang=lang) for lang in self.ppOcr_languages]

    def ocr_match(self, img, input_text):
        pp_results = {}
        for ocr_model in self.ocr_modules:
            result = ocr_model.ocr(img, cls=True)
            for re in result:
                for line in re:
                    text, coordinates, confidence = line[1][0], line[0], line[1][1]
                    coordinates_key = ''.join(map(str, coordinates))
                    # 如果文本,还需要比对坐标是否相同不然会已经在字典中，比较可信度
                    # print((text, tuple(coordinates)) in pp_results)
                    if (text, coordinates_key) in pp_results and confidence <= pp_results[(text, coordinates_key)][0]:
                        continue
                    # 如果文本不在字典中，或者新的可信度更高，更新字典
                    pp_results[text, coordinates_key] = (confidence, coordinates)
        result_list = []
        for key, value in pp_results.items():
            result_dict = {}
            (prob, bbox) = value
            bbox = [(float(point[0]), float(point[1])) for point in bbox]
            (tl, tr, br, bl) = bbox
            center_x = (tl[0] + br[0]) / 2
            center_y = (tl[1] + br[1]) / 2
            result_dict['result'] = (center_x, center_y)
            result_dict['rectangle'] = bbox
            result_dict['confidence'] = prob
            result_dict['text'] = key[0]
            result_list.append(result_dict)
        print(result_list)
        coordinate = next((r_dict for r_dict in result_list if r_dict.get('text').lower() == input_text.lower()), None)
        return coordinate


METHOD_LIST = ['easy', 'padd']


class OcrTemplate(Template):
    """
    ocr模版
        :param filename: 传入的文字
        :param ocrPlus: 是否启用二值化和高斯模糊
        :param
    """

    ocr_instances = {
        "default": {
            'easy': EasyOcr(),
            'padd': PpOcr()
        }
    }
    lock = threading.Lock()

    def __init__(self, filename, threshold=None, target_pos=TargetPos.MID, record_pos=None, resolution=(), rgb=False,
                 scale_max=800, scale_step=0.005, ocrPlus=False, language=None):

        super().__init__(filename, threshold, target_pos, record_pos, resolution, rgb, scale_max, scale_step)
        self.ocrPlus = ocrPlus
        if language is not None:
            self.language = tuple(language)
            with OcrTemplate.lock:
                if self.language not in OcrTemplate.ocr_instances:
                    OcrTemplate.ocr_instances[self.language] = {
                        'easy': EasyOcr(language=self.language),
                        'padd': PpOcr(language=self.language)
                    }
        else:
            self.language = language

    @property
    def filepath(self):
        return self.filename

    def match_in(self, screen):
        match_result = self._cv_match(screen)
        G.LOGGING.debug("match result: %s", match_result)
        if not match_result:
            return None
        focus_pos = TargetPos().getXY(match_result, self.target_pos)
        return focus_pos

    @logwrap
    def _cv_match(self, screen):

        img = screen

        # 灰度化
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 增加对比度和亮度
        # contrast_img = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        # 创建一个空的数组，数据类型为'float32'
        img_float = np.float32(gray)
        # 缩放像素值到0-1之间
        img_norm = img_float / 255.0
        # 调整对比度
        contrast_img = np.power(img_norm, 2.3)
        # 将像素值缩放回0-255之间并转换为'uint8'
        contrast_img = np.uint8(contrast_img * 255)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(contrast_img)
        # cv2.imshow("Image3", clahe_img)
        # cv2.waitKey(0)

        ret = None
        if self.ocrPlus is True:
            # osu
            _, binary_img = cv2.threshold(contrast_img, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            # 应用高斯滤波
            clahe_img = cv2.GaussianBlur(binary_img, (5, 5), 0)
            #
            # cv2.imshow("Image3", binary_img)
            # cv2.waitKey(0)

        for method in METHOD_LIST:
            # get function definition and execute:
            if self.language is not None:
                func = OcrTemplate.ocr_instances[self.language][method]
            else:
                func = OcrTemplate.ocr_instances["default"][method]
            if func is None:
                raise InvalidMatchingMethodError(
                    "Undefined method in OCR_METHOD: '%s'" % method)
            else:
                ret = self._try_match(func, language=self.language, img=clahe_img, input_text=self.filename)
            # 先用easyOCR方法失败则会用下一个
            if ret:
                break
        return ret

    @staticmethod
    def _try_match(func, *args, **kwargs):
        G.LOGGING.debug("try match with %s" % func)
        try:
            instance = func
            ret = instance.ocr_match(img=kwargs['img'], input_text=kwargs['input_text'])
        except aircv.NoModuleError as err:
            G.LOGGING.warning(
                "'Easy/ppd' initialization failed. Alternatively, reinstall easycr or PaddleOCR.")
            return None
        except aircv.BaseError as err:
            G.LOGGING.debug(repr(err))
            return None
        else:
            return ret

# 测试代码
# img_text = cv2.imread(r"G:\pyProject\odin-testautomation\TestAutomation\airtestProject\commons\img\odin\test (2).png")
# rett = OcrTemplate("RTT: 142ms", language=['ch']).match_in(img_text)
# print(rett)
