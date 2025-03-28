import re
import cv2
import numpy as np
import ddddocr


def check_chars_exist(text, chars=None):
    if chars is None:
        chars = ["拉好友", "快手", "抢红包", "搜索兴趣商品下单", "买精选商品", "全场3元3件", "固定入口", "农场小游戏", "砸蛋", "大众点评", "蚂蚁新村", "消消乐", "玩一玩", "3元抢3件包邮到家", "拍一拍", "1元抢爆款好货", "拉1人助力", "玩消消乐", "下单即得", "添加签到神器", "下单得肥料", "88VIP", "邀请好友", "好货限时直降", "连连消", "下单即得", "拍立淘", "玩任意游戏"]
    for char in chars:
        if char in text:
            return True
    return False


def get_current_app(d):
    info = d.shell("dumpsys window | grep mCurrentFocus").output
    match = re.search(r'mCurrentFocus=Window\{.*? u0 (.*?)/(.*?)\}', info)
    if match:
        package_name = match.group(1)
        activity_name = match.group(2)
        return package_name, activity_name
    return None, None


other_app = ["蚂蚁森林", "农场", "百度", "支付宝", "芝麻信用", "蚂蚁庄园", "闲鱼", "神奇海洋", "淘宝特价版", "点淘", "饿了么", "微博", "直播", "领肥料礼包", "福气提现金", "看小说", "菜鸟", "斗地主", "领肥料礼包"]


def fish_not_click(text, chars=None):
    if chars is None:
        chars = ["发布一件新宝贝", "买到或卖出", "快手", "中国移动", "视频", "下单", "点淘", "一淘", "收藏"]
    for char in chars:
        if char in text:
            return True
    return False


def find_button(image, btn_path, region=None):
    template = cv2.imread(btn_path)
    # 如果指定了区域，裁剪图像
    if region is not None:
        x, y, w_region, h_region = region
        image = image[y:y + h_region, x:x + w_region]
    # 转换为灰度图像
    screenshot_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    # 获取模板图像的宽度和高度
    w, h = template_gray.shape[::-1]
    # 使用模板匹配
    res = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        return pt
    return None


def find_text_position(image, text):
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocr_result = ocr.classification(image)
    # 将 OCR 结果按行解析
    lines = ocr_result.split('\n')
    # 遍历每一行，查找目标文本的位置
    for line in lines:
        if text in line:
            # 获取文本的位置
            start_index = line.find(text)
            end_index = start_index + len(text)
            return start_index, end_index
    return None


# 判断一个字符是否为中文字符
def is_chinese(char):
    return '\u4e00' <= char <= '\u9fff'


def majority_chinese(text):
    if not text:
        return False
    chinese_count = sum(1 for char in text if is_chinese(char))
    return chinese_count > len(text) / 2


# img = cv2.imread("./img/screenshot.png")
# pt = find_button(img, "./img/fish_back.png", (0, 0, 300, 500))
# print(pt)
