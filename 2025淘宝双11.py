import time
import random
import re

import uiautomator2 as u2
from uiautomator2 import Direction
from utils import check_chars_exist, other_app, get_current_app

d = u2.connect()
d.app_start("com.taobao.taobao", stop=True, use_monkey=True)
screen_width = d.info['displayWidth']
screen_height = d.info['displayHeight']
time.sleep(5)
in_search = False
in_other_app = False
have_clicked = []

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


def check_in_task():
    temp_package, temp_activity = get_current_app(d)
    if temp_package == "com.taobao.taobao" and temp_activity == "com.taobao.themis.container.app.TMSActivity":
        phy_view = d(className="android.widget.TextView", text="做任务赚体力")
        if phy_view.exists:
            return True
    return False


def operate_task():
    start_time = time.time()
    cancel_btn = d(resourceId="android:id/button2", text="取消")
    if cancel_btn.exists:
        cancel_btn.click()
        time.sleep(2)
        return
    while True:
        if time.time() - start_time > 18:
            break
        start_x = random.randint(screen_width // 6, screen_width // 2)
        start_y = random.randint(screen_height // 2, screen_height - screen_width // 4)
        end_x = random.randint(start_x - 100, start_x)
        end_y = random.randint(start_y - 1200, start_y - 300)
        swipe_time = random.uniform(0.4, 1) if end_y - start_y > 500 else random.uniform(0.2, 0.5)
        print("模拟滑动", start_x, start_y, end_x, end_y, swipe_time)
        d.swipe(start_x, start_y, end_x, end_y, swipe_time)
        time.sleep(random.uniform(1, 5))
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
            else:
                print("点击后退")
                d.press("back")
                time.sleep(0.5)


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
print("进入领淘金币按钮")
physical_btn = d(className="android.widget.Button", text="赚体力")
if physical_btn.exists:
    physical_btn.click()
    time.sleep(5)
finish_count = 0
time1 = time.time()
while True:
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
                if task_name in have_clicked:
                    continue
                need_click_index = index
                need_click_view = view
                break
        if need_click_view:
            print("点击按钮", task_name)
            if task_name not in have_clicked:
                have_clicked.append(task_name)
            # need_click_view.click()
            d.click(random.randint(need_click_view.bounds()[0] + 10, need_click_view.bounds()[2] - 10), random.randint(need_click_view.bounds()[1] + 10, need_click_view.bounds()[3] - 10))
            time.sleep(4)
            search_view = d(className="android.view.View", text="搜索有福利")
            if search_view.exists:
                d(className="android.widget.EditText", instance=0).send_keys("笔记本电脑")
                d(className="android.widget.Button", text="搜索").click()
                in_search = True
                time.sleep(4)
            operate_task()
        else:
            break
    time.sleep(4)
print(f"共自动化完成{finish_count}个任务")
temp_btn = d(className="android.widget.TextView", text="做任务赚体力")
if temp_btn.exists:
    print("点击缩回弹框")
    temp_btn.right(className="android.widget.Button").click()
time.sleep(4)
while True:
    print("开始跳一跳。。。")
    share_view = d(className="android.view.View", text="分享给好友立得体力")
    if share_view.exists:
        print("存在分享给好友立得体力弹框，关闭它")
        close_btn = d.xpath('//android.view.View[@text="分享给好友立得体力"]/preceding-sibling::android.view.View[3]')
        if close_btn.exists:
            print("关闭按钮存在，关闭它")
            close_btn.click()
            time.sleep(3)
    dump_btn = d(className="android.widget.Button", textContains="跳一跳拿钱")
    if dump_btn.exists:
        dump_text = dump_btn.get_text()
        match = re.search(r'剩余 (\d+) 体力', dump_text)
        if match:
            phy_num = int(match.group(1))
            if phy_num <= 9:
                break
            print(f"当前剩余体力：{phy_num}")
            # d.shell(f"input touchscreen swipe {dump_btn.center()[0]} {dump_btn.center()[1]} {dump_btn.center()[0]} {dump_btn.center()[1]} 5000")
            dump_btn.long_click(duration=6)
            time.sleep(8)
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
