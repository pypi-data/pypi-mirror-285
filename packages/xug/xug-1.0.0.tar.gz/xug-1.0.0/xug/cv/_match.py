from xug import get_scaling
true_scale=get_scaling
import cv2
import os
import numpy as np
import pyautogui
from dataclasses import dataclass


def find_image_on_screen(template, min_threshold, gray=False, a=0, b=0, c=0, d=0,image_sacle=true_scale,max_deviation = 13):
    '''
参数:
template：模板图片，字符串，即待匹配图片，支持两种形式，可以传入图片地址，也可以直接传入图片名称，此时会从代码中设定的图片文件夹寻找图片；

min_threshold：最小匹配度，浮点数，只返回匹配度大于等于该值的结果，取值范围0-100

gray：灰度匹配，布尔值，为真时则忽略颜色，可以大幅提升匹配速度，适用于不考虑颜色的情况

a,b,c,d:区域匹配坐标，整数，都为0时不生效，否则只在该区域匹配，但是返回的结果坐标任然是相对于整个屏幕

image_sacle：图片缩放，浮点数，即传入的图片的缩放，也就是截图时电脑对应的缩放，默认和1.25，即125%，需要自己根据情况修改，取值是（1,1.25,1.5,1.75,2）

max_deviation：最大偏差值，整数，多个匹配结果之间距离的最小值，如果存在同一个目标被识别成两个结果的情况，可以适当增加这个参数的值

返回值：
列表类型，包含所有符合条件的匹配结果(MatchInfo对象)，如果没有匹配到则是空列表
    '''
    image_path='D:\\test\\image'
    min_threshold = min_threshold / 100
    if not os.path.isabs(template):
        template = os.path.join(image_path, template)
    templ = cv2.imread(template)
    screenshot = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    xx, yy = templ.shape[:-1]
    if true_scale != image_sacle:
        screenshot = cv2.resize(screenshot, None, fx=image_sacle / true_scale, fy=image_sacle / true_scale)
    if gray:
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        templ = cv2.cvtColor(templ, cv2.COLOR_BGR2GRAY)
    if a==0 and b==0 and c==0 and d==0:
        screenshot_region = screenshot
    else:
        c = max(a + yy, c)
        d = max(b + xx, d)
        screenshot_region = screenshot[b:d, a:c]
    result = cv2.matchTemplate(screenshot_region, templ, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= min_threshold)
    locations = list(zip(*locations[::-1]))
    match_info = {}
    for loc in locations:
        x, y = loc
        x = x + a 
        y = y + b 
        match_value = result[y - b, x - a]
        skip_current = False
        for (prev_x, prev_y), prev_match_value in match_info.items():
            if abs(x - prev_x) <= max_deviation and abs(y - prev_y) <= max_deviation:
                if match_value > prev_match_value:
                    match_info[(x, y)] = match_value
                    del match_info[(prev_x, prev_y)]
                else:
                    skip_current = True
                break
        if not skip_current:
            match_info[(x, y)] = match_value
    match_info_objects = []
    for (x, y), match_value in sorted(
        match_info.items(), key=lambda x: x[1], reverse=True
    ):
        h, w = xx, yy
        top_left = (x, y)
        bottom_right = (x + w, y + h)
        center = (x + w // 2, y + h // 2)
        matche = MatchInfo(
            match_value * 100,
            center[0],
            center[1],
            top_left[0],
            top_left[1],
            bottom_right[0],
            bottom_right[1],
        )
        match_info_objects.append(matche)
    return match_info_objects


@dataclass
class MatchInfo:
    match: float = 0
    x: int = 0
    y: int = 0
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0

    @staticmethod
    def not_found():
        return MatchInfo()

    def __str__(self):
        return (
            f"匹配度={self.match:.2f}, "
            f"中心坐标: ({self.x}, {self.y}) "
        )