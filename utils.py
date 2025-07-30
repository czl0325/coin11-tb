import time
import random
import re
import cv2
import numpy as np
import ddddocr


def check_chars_exist(text, chars=None):
    if chars is None:
        chars = ["拉好友", "快手", "抢红包", "搜索兴趣商品下单", "买精选商品", "全场3元3件", "固定入口", "农场小游戏", "砸蛋", "大众点评", "蚂蚁新村", "消消乐", "玩一玩", "3元抢3件包邮到家", "拍一拍", "1元抢爆款好货", "拉1人助力", "玩消消乐", "下单即得", "添加签到神器", "下单得肥料", "88VIP", "邀请好友", "好货限时直降", "连连消", "下单即得", "拍立淘", "玩任意游戏", "首页回访", "百亿外卖"]
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
        chars = ["发布一件新宝贝", "买到或卖出", "快手", "中国移动", "视频", "下单", "点淘", "一淘", "收藏", "购买"]
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


search_keys = ["华硕a豆air", "机械革命星耀14", "ipadmini7", "iphone16", "红米note13", "macbookairm4", "华硕灵耀14", "微星星影15"]


def task_loop(d, func):
    history_lst = d.xpath('(//android.widget.TextView[@text="历史搜索"]/following-sibling::android.widget.ListView)/android.view.View[1]')
    if history_lst.exists:
        print("查找到搜索关键字", history_lst)
        history_lst.click()
        time.sleep(2)
    else:
        search_view = d(className="android.view.View", text="搜索有福利")
        if search_view.exists:
            search_edit = d.xpath("//android.widget.EditText")
            if search_edit.exists:
                search_edit.set_text(random.choice(search_keys))
                search_btn = d(className="android.widget.Button", text="搜索")
                if search_btn.exists:
                    search_btn.click()
                    time.sleep(2)
    screen_width, screen_height = d.window_size()
    package_name, _ = get_current_app(d)
    check_count = 3
    while check_count >= 0:
        if not func():
            break
        print(f"检查次数：{check_count}当前在任务页面，没有执行任务。。。")
        check_count -= 1
        if check_count <= 0:
            return
        time.sleep(2)
    start_time = time.time()
    while True:
        if time.time() - start_time > 20:
            break
        if package_name == "com.taobao.taobao":
            start_x = random.randint(screen_width // 6, screen_width // 2)
            start_y = random.randint(screen_height // 2, screen_height - screen_width // 4)
            end_x = random.randint(start_x - 100, start_x)
            end_y = random.randint(start_y - 1200, start_y - 300)
            swipe_time = random.uniform(0.4, 1) if end_y - start_y > 500 else random.uniform(0.2, 0.5)
            print("模拟滑动", start_x, start_y, end_x, end_y, swipe_time)
            d.swipe(start_x, start_y, end_x, end_y, swipe_time)
            time.sleep(random.uniform(1, 3))
        else:
            time.sleep(5)
    try_count = 0
    while True:
        if func():
            print("当前是任务列表画面，不能继续返回")
            break
        else:
            d.press("back")
            time.sleep(0.2)
            try_count += 1
            if try_count > 10:
                break
# img = cv2.imread("./img/screenshot.png")
# pt = find_button(img, "./img/fish_back.png", (0, 0, 300, 500))
# print(pt)


def close_xy_dialog(d):
    dialog_view1 = d.xpath('//android.webkit.WebView[@text="闲鱼币首页"]/android.view.View/android.view.View[2]//android.widget.Image[1]')
    if dialog_view1.exists:
        dialog_view1.click()
        time.sleep(2)