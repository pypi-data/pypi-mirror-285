import re
import time
import datetime

import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

from ..base.ocr import TextDetector, TextClassifier, TextRecognizer


class LicensePlateProcessor:
    def __init__(self, text_det_path, text_class_path, text_rec_path, dict_path, font_path):
        self.detect_model = TextDetector(text_det_path)
        self.angle_model = TextClassifier(text_class_path)
        self.rec_model = TextRecognizer(text_rec_path, dict_path)
        self.font_path = font_path
        self.font_size = 30

    def detect_license_plates(self, srcimg):
        box_list = self.detect_model.detect(srcimg)
        results = []

        if len(box_list) > 0:
            for point in box_list:
                point = self.detect_model.order_points_clockwise(point)
                textimg = self.detect_model.get_rotate_crop_image(srcimg, point.astype(np.float32))
                angle = self.angle_model.predict(textimg)

                if angle == '180':
                    textimg = cv2.rotate(textimg, 1)

                text = re.sub(r'[ ·•\s-]', '', self.rec_model.predict_text(textimg).strip())

                pattern = re.compile(r"(([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼])([A-HJ-NP-Z]{1}[DABCEFGHJK]{1}[A-HJ-NP-Z0-9]{1}[0-9]{4})|([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼])([A-HJ-NP-Z]{1}[0-9]{5}[DABCEFGHJK]{1}))|(([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼])([A-HJ-NP-Z]{1}[A-HJ-NP-Z0-9]{4}[A-HJ-NP-Z0-9挂学警]{1}))|(([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼])([A-HJ-NP-Z]{1})([A-HJ-NP-Z0-9]{4}[警]))|(([0-9]{3})([0-9]{3})使)|([沪粤川云桂鄂闽鲁陕蒙藏黑辽渝鲁闽蒙蒙]{1}[ABDEH]{1}[0-9]{4}[领])|(WJ[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼]{1}[0-9]{4}[TDSHBXJ0-9]{1})|([VKHBSLJNGCE][A-DJ-PR-TVY0-9]{1}[0-9]{5})")
                match_result = re.search(pattern, text)
                if match_result:
                    text_result = match_result.group()
                    point = point.astype(int)
                    cv2.polylines(srcimg, [point], True, (0, 255, 0), thickness=2)
                    for i in range(4):
                        cv2.circle(srcimg, tuple(point[i, :]), 3, (0, 255, 0), thickness=-1)
                    results.append((point, text_result))
                # else:
                #     # results.append(("error", text))
                #     # print(point, text)
        return srcimg, results

    def draw_results(self, srcimg, results):
        y = -30
        time_ = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        pil_img = Image.fromarray(cv2.cvtColor(srcimg, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        text_width, text_height = 800, 30

        for point, text_result in results:
            y += 30
            text_position = (0, y)
            rectangle_position = (text_position[0], text_position[1])
            rectangle_size = (text_position[0] + text_width, text_position[1] + text_height)
            draw.rectangle((rectangle_position, rectangle_size), fill=(0, 0, 0))
            text_color = (255, 255, 255)
            text_img = f"时间：{time_}   车牌号码：{text_result}"
            font = ImageFont.truetype(self.font_path, self.font_size)
            draw.text(text_position, text_img, font=font, fill=text_color)

        srcimg = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return srcimg

    def process_image(self, srcimg):
        srcimg, results = self.detect_license_plates(srcimg)
        result_img = self.draw_results(srcimg, results)
        results = [item[1] for item in results]
        return result_img, results
