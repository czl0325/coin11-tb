import time
import random
import re
import cv2
import numpy as np
import ddddocr
import subprocess
from paddleocr import PaddleOCR

TB_APP = "com.taobao.taobao"
ALIPAY_APP = "com.eg.android.AlipayGphone"
FISH_APP = "com.taobao.idlefish"
TMALL_APP = "com.tmall.wireless"

# 应用启动配置，键为包名，值为activity
APP_START_CONFIG = {
    TB_APP: "com.taobao.tao.welcome.Welcome",
    FISH_APP: "com.taobao.fleamarket.home.activity.InitActivity",
    TMALL_APP: "com.tmall.wireless.maintab.module.TMMainTabActivity",
    ALIPAY_APP: None  # 默认配置，不指定activity
}

def check_chars_exist(text, chars=None):
    if chars is None:
        chars = ["拉好友", "抢红包", "搜索兴趣商品下单", "买精选商品", "全场3元3件", "固定入口", "农场小游戏", "砸蛋","大众点评", "蚂蚁新村", "消消乐", "3元抢3件包邮到家", "拍一拍", "1元抢爆款好货", "拉1人助力","玩消消乐", "下单即得", "添加签到神器", "下单得肥料", "88VIP", "邀请好友", "好货限时直降", "连连消","下单即得", "拍立淘", "玩任意游戏", "首页回访", "百亿外卖", "玩趣味游戏得大额体力", "天猫积分换体力", "头条刷热点", "一淘签到", "每拉", "闪购拿大额补贴", "开心消消乐过1关", "通关", "购买商品", "去闪购领红包点外卖", "冒险大作战", "欢喜斗地主", "买限时折扣好物", "趣头条"]
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


other_app = ["蚂蚁森林", "农场", "百度", "支付宝", "芝麻信用", "蚂蚁庄园", "闲鱼", "神奇海洋", "淘宝特价版", "点淘",
             "饿了么", "微博", "直播", "领肥料礼包", "福气提现金", "看小说", "菜鸟", "斗地主", "领肥料礼包"]


def fish_not_click(text, chars=None):
    if chars is None:
        chars = ["发布一件新宝贝", "买到或卖出", "中国移动", "视频", "下单", "点淘", "一淘", "收藏", "购买"]
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
    threshold = 0.7
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        return pt
    return None


def find_button2(image, btn_path):
    template = cv2.imread(btn_path)
    # 创建 ORB 检测器
    orb = cv2.ORB_create()
    # 检测关键点和描述符
    kp1, des1 = orb.detectAndCompute(image, None)
    kp2, des2 = orb.detectAndCompute(template, None)
    # 创建匹配器
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    # 按距离排序
    matches = sorted(matches, key=lambda x: x.distance)
    for match in matches:
        x, y = kp2[match.trainIdx].pt
        print(f"匹配距离: {match.distance},x = {x:.2f}, y = {y:.2f}")


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


def paddle_ocr(image):
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')
    result = ocr.ocr(image)
    texts = []
    for line in result[0]:  # result 是列表，result[0] 是当前图片的行信息
        text = line[1][0]  # line[1][0] 是识别的文字，line[1][1] 是置信度
        texts.append(text)
    # 拼接方式：可以直接连在一起，或者加空格/换行，根据你的图片实际情况调整
    full_sentence = ''.join(texts)  # 无空格直接拼接（适合连续文字）
    print(f"提取的完整文字：{full_sentence}")
    return full_sentence


# 判断一个字符是否为中文字符
def is_chinese(char):
    return '\u4e00' <= char <= '\u9fff'


def majority_chinese(text):
    if not text:
        return False
    chinese_count = sum(1 for char in text if is_chinese(char))
    return chinese_count > len(text) / 2


search_keys = ["华硕a豆air", "机械革命星耀14", "ipadmini7", "iphone16", "红米note13", "macbookairm4", "华硕灵耀14",
               "微星星影15"]


def task_loop(d, back_func, origin_app=TB_APP, is_fish=False, duration=22):
    history_lst = d.xpath(
        '(//android.widget.TextView[@text="历史搜索"]/following-sibling::android.widget.ListView)/android.view.View[1]')
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
    # check_count = 3
    # while check_count >= 0:
    #     if not func():
    #         break
    #     print(f"检查次数：{check_count}当前在任务页面，没有执行任务。。。")
    #     check_count -= 1
    #     if check_count <= 0:
    #         return
    #     time.sleep(2)
    start_time = time.time()
    print("开始做任务。。。")
    while True:
        try:
            bt_open = d(resourceId="android:id/button1", text="浏览器打开")
            if bt_open.exists:
                bt_close = d(resourceId="android:id/button2", text="取消")
                if bt_close.exists:
                    bt_close.click()
                    time.sleep(2)
                    break
            if time.time() - start_time > duration:
                break
            if is_fish:
                print("开始查找闲鱼商品")
                time.sleep(4)
                commodity_view1 = d.xpath("//android.widget.ListView/android.view.View[1]")
                if commodity_view1.exists:
                    commodity_view1.click()
                    time.sleep(18)
                    break
                commodity_view2 = d(className="android.view.View", resourceId="feedsContainer")
                if commodity_view2.exists:
                    d.click(100, commodity_view2.center()[1])
                    time.sleep(18)
                    break
            if package_name == origin_app:
                if package_name == ALIPAY_APP:
                    screen_image = d.screenshot(format='opencv')
                    pt1 = find_button(screen_image, "./img/alipay_get.png")
                    if pt1:
                        print("检测到立即领取的弹框，点击立即领取")
                        d.click(int(pt1[0]) + 50, int(pt1[1]) + 20)
                        time.sleep(1)
                start_x = random.randint(screen_width // 6, screen_width // 2)
                start_y = random.randint(screen_height // 2, screen_height - screen_width // 4)
                end_x = random.randint(start_x - 100, start_x)
                end_y = random.randint(200, start_y - 300)
                swipe_time = random.uniform(0.4, 1) if end_y - start_y > 500 else random.uniform(0.2, 0.5)
                print("模拟滑动", start_x, start_y, end_x, end_y, swipe_time)
                d.swipe(start_x, start_y, end_x, end_y, swipe_time)
                time.sleep(random.uniform(0.8, 2))
            else:
                time.sleep(5)
        except Exception as e:
            time.sleep(5)
    back_func()


def close_xy_dialog(d):
    dialog_view1 = d.xpath(
        '//android.webkit.WebView[@text="闲鱼币首页"]/android.view.View/android.view.View[2]//android.widget.Image[1]')
    if dialog_view1.exists:
        dialog_view1.click()
        time.sleep(2)


def get_connected_devices():
    """通过ADB获取所有连接的安卓设备序列号"""
    try:
        # 执行adb命令获取设备列表
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            check=True
        )

        # 解析输出，提取设备序列号
        output = result.stdout
        devices = []
        for line in output.splitlines():
            # 跳过标题行和空行
            if line.strip() == "" or line.startswith("List of devices attached"):
                continue
            match = re.match(r"^([^\s]+)\s+device$", line)
            if match:
                devices.append(match.group(1))
        return devices
    except subprocess.CalledProcessError:
        print("执行ADB命令失败，请确保ADB已正确安装并添加到环境变量")
        return []
    except FileNotFoundError:
        print("未找到ADB命令，请确保ADB已正确安装并添加到环境变量")
        return []


# 从已连接的设备中，返回用户选中的设备序列号
def select_device():
    # 获取所有连接的设备
    devices = get_connected_devices()

    if not devices:
        raise Exception("未检测到任何连接的安卓设备")

        # 根据设备数量进行处理
    if len(devices) == 1:
        # 只有一个设备，直接返回
        return devices[0]
    else:
        # 多个设备，让用户选择
        print("当前连接多个设备，请输入要执行的设备序号：")
        for i, device in enumerate(devices, 1):
            print(f"  {i}: {device}")

        # 获取用户输入并验证
        while True:
            try:
                choice = input("请输入设备序号：")
                index = int(choice) - 1  # 转换为列表索引

                if 0 <= index < len(devices):
                    # 选中的设备
                    return devices[index]
                else:
                    print(f"输入错误，请重新输入序号（1-{len(devices)}）")
            except ValueError:
                print(f"输入错误，请重新输入序号（1-{len(devices)}）")


def start_app(d, package_name, init=False):
    """根据包名启动应用，支持特定应用的activity配置
    init参数控制启动模式：
    - True: 初始化启动，使用stop=True, use_monkey=True
    - False: 普通启动，使用stop=False, use_monkey=False
    默认不使用activity启动，如果失败再尝试使用activity
    activity启动时不使用use_monkey参数
    启动后验证是否成功"""
    # 根据init参数设置stop和use_monkey
    stop = init
    use_monkey = init
    
    # 获取配置的activity
    activity = APP_START_CONFIG.get(package_name)
    try_count = 3
    try:
        # 优先不使用activity启动
        while try_count > 0:
            print(f"启动应用: {package_name}, stop: {stop}, use_monkey: {use_monkey}, 不使用activity")
            d.app_start(package_name, stop=stop, use_monkey=use_monkey)
            time.sleep(5 if stop else 2)
            # 验证应用是否启动成功
            current_package, _ = get_current_app(d)
            if current_package == package_name:
                print(f"应用 {package_name} 启动成功")
                return
            else:
                print(f"应用 {package_name} 未成功启动，当前应用: {current_package}，尝试后退")
                d.press("back")
                time.sleep(1)
            try_count -= 1
    except Exception as e:
        print(f"不使用activity启动失败: {e}")
        
    # 如果失败且有配置activity，则尝试使用activity启动
    if activity:
        try:
            print(f"使用activity启动应用: {package_name}, activity: {activity}, stop: {stop}")
            d.app_start(package_name=package_name, activity=activity, stop=stop)
            time.sleep(2)
            # 验证应用是否启动成功
            current_package, _ = get_current_app(d)
            if current_package == package_name:
                print(f"应用 {package_name} 启动成功")
                return
            else:
                print(f"应用 {package_name} 未成功启动，当前应用: {current_package}")
        except Exception as e:
            print(f"使用activity启动也失败: {e}")


def check_verify(d):
    verify_view = d(className="android.webkit.WebView", text="验证码拦截")
    if verify_view.exists:
        while True:
            print("存在验证码的情况")
            d.shell("input swipe 150 1700 1180 1700 500")
            time.sleep(3)
            verify_view = d(className="android.webkit.WebView", text="验证码拦截")
            if verify_view.exists:
                d.click(500, 1700)
                time.sleep(3)
            else:
                print("验证码滑动成功")
                break


# find_button2(cv2.imread("screenshot.png"), "./img/alipay_get.png")
