import time
import random
import re

import uiautomator2 as u2
from uiautomator2 import Direction
from utils import check_chars_exist, other_app, get_current_app

def get_connected_devices():
    """通过ADB获取所有连接的安卓设备序列号"""
    import subprocess
    import re
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
        # 正则表达式匹配设备序列号（忽略第一行和离线设备）
        pattern = re.compile(r'^([a-zA-Z0-9.:]+)\s+device$', re.MULTILINE)
        devices = pattern.findall(output)
        
        return devices
    except subprocess.CalledProcessError:
        print("执行ADB命令失败，请确保ADB已正确安装并添加到环境变量")
        return []
    except FileNotFoundError:
        print("未找到ADB命令，请确保ADB已正确安装并添加到环境变量")
        return []

# 获取所有连接的设备
devices = get_connected_devices()

if not devices:
    raise Exception("未检测到任何连接的安卓设备")

    # 根据设备数量进行处理
if len(devices) == 1:
    # 只有一个设备，直接连接
    # d = u2.connect()
    selected_device = devices[0]
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
                # 连接选中的设备
                # d = u2.connect(devices[index])
                selected_device = devices[index]
                break
            else:
                print(f"输入错误，请重新输入序号（1-{len(devices)}）")
        except ValueError:
            print(f"输入错误，请重新输入序号（1-{len(devices)}）")


d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")

d.app_start("com.taobao.taobao", stop=True, use_monkey=True)
screen_width = d.info['displayWidth']
screen_height = d.info['displayHeight']
time.sleep(5)
in_search = False
in_other_app = False
have_clicked = {}

ctx = d.watch_context()
# ctx.when("O1CN012qVB9n1tvZ8ATEQGu_!!6000000005964-2-tps-144-144").click()
# ctx.when("O1CN01TkBa3v1zgLfbNmfp7_!!6000000006743-2-tps-72-72").click()
ctx.when("点击刷新").click()
# ctx.when(xpath="//android.app.Dialog//android.widget.Button[@text='关闭']").click()
# ctx.when(xpath="//android.widget.TextView[@package='com.eg.android.AlipayGphone']").click()
ctx.when(xpath="//android.widget.FrameLayout[@resource-id='com.taobao.taobao:id/poplayer_native_state_center_layout_frame_id']/android.widget.ImageView").click()
ctx.start()


def close_all_dialog():
    btn1 = d(className="android.widget.TextView", text="去使用")
    if btn1.exists:
        btn1.right(className="android.widget.ImageView").click()
        time.sleep(2)
    share_view = d(className="android.view.View", textMatches=r"分享给好友立得体力|去抢频道额外优惠")
    if share_view.exists:
        print("存在分享给好友立得体力弹框，关闭它")
        close_btn1 = d.xpath('//android.view.View[@text="分享给好友立得体力" or @text="去抢频道额外优惠"]/preceding-sibling::android.view.View[3]')
        if close_btn1.exists:
            print("关闭按钮存在，关闭它")
            close_btn1.click()
            time.sleep(3)
    dialog_view2 = d(className="android.view.View", text="去赚体力")
    if dialog_view2.exists:
        print("存在去赚体力弹框，关闭它")
        close_btn1 = d.xpath('//android.view.View[@text="去赚体力"]/preceding-sibling::android.view.View[5]')
        if close_btn1.exists:
            print("关闭按钮存在，关闭它")
            close_btn1.click()
            time.sleep(3)
    dialog_view3 = d(className="android.widget.TextView", text="去下单")
    if dialog_view3.exists:
        close_btn1 = d(className="android.widget.Image", text="关闭")
        if close_btn1.exists:
            close_btn1.click()
            time.sleep(3)


def check_in_task():
    temp_package, temp_activity = get_current_app(d)
    if temp_package == "com.taobao.taobao" and temp_activity == "com.taobao.themis.container.app.TMSActivity":
        phy_view = d(className="android.widget.TextView", text="做任务赚体力")
        if phy_view.exists(timeout=5):
            return True
    elif temp_package == "com.taobao.taobao" and temp_activity == "com.taobao.tao.welcome.Welcome":
        to_11()
        return True
    return False


def to_11():
    while True:
        package_name, activity_name = get_current_app(d)
        if package_name == "com.taobao.taobao" and activity_name != "com.taobao.tao.welcome.Welcome":
            break
        coin_btn = d(className="android.view.View", description="领淘金币")
        if coin_btn.exists:
            coin_btn.click()
        else:
            raise Exception("没有找到领淘金币按钮")
        time.sleep(4)
    time.sleep(10)
    print("进入领淘金币页面")
    close_all_dialog()
    while True:
        physical_btn = d(className="android.widget.Button", text="赚体力")
        if physical_btn.exists:
            physical_btn.click()
            time.sleep(5)
        if check_in_task():
            break


def operate_task(repeat=False):
    start_time = time.time()
    cancel_btn = d(resourceId="android:id/button2", text="取消")
    if cancel_btn.exists:
        cancel_btn.click()
        time.sleep(2)
        return
    while True:
        if time.time() - start_time > 25 if repeat else 20:
            break
        start_x = random.randint(screen_width // 6, screen_width // 2)
        start_y = random.randint(screen_height // 2, screen_height - screen_height // 4)
        end_x = random.randint(start_x - 100, start_x)
        end_y = random.randint(start_y - 800, start_y - 300)
        swipe_time = random.uniform(0.4, 1) if end_y - start_y > 500 else random.uniform(0.2, 0.5)
        print("模拟滑动", start_x, start_y, end_x, end_y, swipe_time)
        d.swipe(start_x, start_y, end_x, end_y, swipe_time)
        time.sleep(random.uniform(1, 3))
    print("开始返回界面")
    while True:
        if check_in_task():
            print("当前是任务列表画面，不能继续返回")
            break
        else:
            temp_package, temp_activity = get_current_app(d)
            if temp_package is None or temp_activity is None:
                continue
            print(f"{temp_package}--{temp_activity}")
            if "com.taobao.taobao" not in temp_package:
                print("回到淘宝APP")
                d.app_start("com.taobao.taobao", stop=False)
                time.sleep(2)
            else:
                print("点击后退")
                d.press("back")
                time.sleep(0.5)


to_11()
finish_count = 0
time1 = time.time()
while True:
    try:
        print("开始查找任务。。。")
        get_btn = d(className="android.widget.Button", text="立即领取")
        if get_btn.exists:
            get_btn.click()
            time.sleep(3)
        to_btn = d(className="android.widget.Button", text="去完成")
        if to_btn.exists:
            need_click_view = None
            need_click_index = 0
            task_name = None
            for index, view in enumerate(to_btn):
                text_div = view.sibling(className="android.view.View", instance=0).child(className="android.widget.TextView", instance=0)
                if text_div.exists:
                    if check_chars_exist(text_div.get_text()):
                        continue
                    task_name = text_div.get_text()
                    if task_name in have_clicked and have_clicked[task_name] > 1:
                        continue
                    need_click_index = index
                    need_click_view = view
                    break
            if need_click_view:
                print("点击按钮", task_name)
                if task_name not in have_clicked:
                    have_clicked[task_name] = 1
                else:
                    have_clicked[task_name] += 1
                # need_click_view.click()
                d.click(random.randint(need_click_view.bounds()[0] + 10, need_click_view.bounds()[2] - 10), random.randint(need_click_view.bounds()[1] + 10, need_click_view.bounds()[3] - 10))
                time.sleep(4)
                open_btn = d(className="android.widget.Button", resourceIdMatches=r"android:id/.*", textMatches="打开|允许")
                if open_btn.exists:
                    open_btn.click()
                    time.sleep(4)
                search_view = d(className="android.view.View", text="搜索有福利")
                if search_view.exists:
                    d(className="android.widget.EditText", instance=0).send_keys("笔记本电脑")
                    d(className="android.widget.Button", text="搜索").click()
                    in_search = True
                    time.sleep(4)
                operate_task(have_clicked[task_name]>1)
                finish_count += 1
            else:
                break
        time.sleep(5)
    except Exception as e:
        print("出现异常，继续下一轮", str(e))
print(f"共自动化完成{finish_count}个任务")
temp_btn = d(className="android.widget.TextView", text="做任务赚体力")
if temp_btn.exists:
    print("点击缩回弹框")
    try:
        close_btn = temp_btn.right(className="android.widget.Button")
        if close_btn.exists:
            close_btn.click()
    except Exception:
        d.shell("input tap 500 300")
time.sleep(4)
while True:
    print("开始跳一跳。。。")
    close_all_dialog()
    dump_btn = d(className="android.widget.Button", textContains="跳一跳拿钱")
    if dump_btn.exists:
        dump_text = dump_btn.get_text()
        match = re.search(r'剩余 (\d+) 体力', dump_text)
        if match:
            phy_num = int(match.group(1))
            if phy_num < 10:
                break
            print(f"当前剩余体力：{phy_num}")
            if phy_num < 50:
                dump_btn.click()
            else:
                # d.shell(f"input touchscreen swipe {dump_btn.center()[0]} {dump_btn.center()[1]} {dump_btn.center()[0]} {dump_btn.center()[1]} 5000")
                dump_btn.long_click(duration=5)
            time.sleep(7)
        else:
            break
    else:
        break

d.watcher.remove()
d.shell("settings put system accelerometer_rotation 0")
print("关闭手机自动旋转")
time2 = time.time()
minutes, seconds = divmod(int(time2 - time1), 60)  # 同时计算分钟和秒
print(f"共耗时: {minutes} 分钟 {seconds} 秒")
