import time
import re

import uiautomator2 as u2
from utils import check_chars_exist, other_app, get_current_app, select_device, task_loop, check_verify, start_app, TB_APP, APP_START_CONFIG, check_popup

unclick_btn = []
have_clicked = dict()
is_end = False
error_count = 0
time1 = time.time()
selected_device = select_device()
d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")
start_app(d, TB_APP, init=True)
screen_width, screen_height = d.window_size()
ctx = d.watch_context()
ctx.when("O1CN012qVB9n1tvZ8ATEQGu_!!6000000005964-2-tps-144-144").click()
ctx.when("O1CN01sORayC1hBVsDQRZoO_!!6000000004239-2-tps-426-128.png_").click()
ctx.when("领取今日奖励").click()
ctx.when("确认").click()
ctx.when("确定").click()
ctx.when("刷新").click()
ctx.when("点击刷新").click()
ctx.when(xpath="//android.app.Dialog//android.widget.Button[contains(text(), '-tps-')]").click()
ctx.when(xpath="//android.app.Dialog//android.widget.Button[@text='关闭']").click()
ctx.when(xpath="//android.widget.Image[@text='关闭']").click()
ctx.when(xpath="//android.widget.FrameLayout[@resource-id='com.taobao.taobao:id/poplayer_native_state_center_layout_frame_id']//android.widget.ImageView[@content-desc='关闭按钮']").click()
# ctx.when(xpath="//android.widget.TextView[@package='com.eg.android.AlipayGphone']").click()
ctx.start()
time.sleep(3)


def find_coin_btn():
    while True:
        jump_btn = d(className="android.widget.Button", textContains="跳一跳拿钱")
        if jump_btn.exists:
            print("进入跳一跳页面")
            break
        coin_btn = d(classNameMatches=r"android.widget.FrameLayout|android.view.View", description="领淘金币")
        if coin_btn.exists:
            coin_btn.click()
        time.sleep(5)


def to_task():
    while True:
        title_view = d(className="android.widget.TextView", text="做任务赚体力")
        if title_view.exists:
            print("进入任务页面。。。")
            break
        earn_btn = d(className="android.widget.Button", text="赚体力")
        if earn_btn.exists:
            earn_btn.click()
        next_btn = d(className="android.widget.TextView", text="下个任务")
        if next_btn.exists:
            time.sleep(16)
            d.press("back")
        time.sleep(4)


def check_in_task():
    webview_home = d(className="android.webkit.WebView", text="淘金币首页")
    title_view = d(className="android.widget.TextView", text="做任务赚体力")
    if title_view.exists and webview_home.exists:
        print("进入任务页面。。。")
        return True
    return False


def back_to_task():
    print("开始返回任务页面")
    while True:
        temp_package, temp_activity = get_current_app(d)
        if temp_package is None or temp_activity is None or "Ext2ContainerActivity" in temp_activity:
            continue
        print(f"{temp_package}--{temp_activity}")
        check_popup(d)
        if TB_APP not in temp_package:
            print(f"回到原始APP,{TB_APP}")
            start_app(d, TB_APP)
            jump_btn = d(resourceId="com.taobao.taobao:id/tv_close", text="跳过")
            if jump_btn.exists:
                jump_btn.click()
                time.sleep(2)
        elif TB_APP in temp_package and APP_START_CONFIG[TB_APP] in temp_activity:
            find_coin_btn()
            to_task()
        else:
            if check_in_task():
                print("当前是任务列表画面，不能继续返回")
                break
            else:
                webview_home = d(className="android.webkit.WebView", text="淘金币首页")
                title_view = d(className="android.widget.TextView", text="做任务赚体力")
                if not title_view.exists and webview_home.exists:
                    print("在淘金币页面但是没有任务列表")
                    to_task()
                    continue
                close_btn1 = d.xpath("//android.widget.FrameLayout[@resource-id='com.alipay.multiplatform.phone.xriver_integration:id/frameLayout_rightButton1']/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.FrameLayout[2]")
                if close_btn1.exists:
                    print("点击关闭小程序按钮")
                    close_btn1.click()
                    time.sleep(1)
                    continue
                task_view = d.xpath('//android.widget.TextView[contains(@text, "限时下单任务")]')
                if task_view.exists:
                    close_btn2 = d.xpath('//android.widget.TextView[contains(@text, "限时下单任务")]/preceding-sibling::android.view.View[1]')
                    if close_btn2.exists:
                        print("点击关闭限时下单任务按钮")
                        close_btn2.click()
                        time.sleep(1)
                        continue
                print("点击后退")
                d.press("back")
                time.sleep(0.3)


find_coin_btn()
to_task()
finish_count = 0
while True:
    try:
        time.sleep(4)
        check_verify(d)
        draw_down_btn = d(className="android.widget.Button", text="立即领取")
        if draw_down_btn.exists:
            draw_down_btn.click()
            time.sleep(2)
        print("开始查找按钮。。。")
        get_btn = d(className="android.widget.Button", text="领取奖励")
        if get_btn.exists:
            get_btn.click()
            print("点击领取奖励")
            time.sleep(2)
            continue
        de_btn = d(className="android.widget.Button", text="点击得")
        if de_btn.exists:
            de_btn.click()
            print("点击点击得")
            time.sleep(4)
            continue
        to_btn = d(className="android.widget.Button", textMatches="去完成|去逛逛|去浏览|逛一逛|立即领|去领取|去看看|搜一下|玩一把|捐一笔|逛一下")
        if to_btn.exists:
            need_click_view = None
            need_click_index = 0
            task_name = None
            for index, view in enumerate(to_btn):
                text_div = view.sibling(className="android.view.View", instance=0).child(className="android.widget.TextView", instance=0)
                if text_div.exists:
                    task_name = text_div.get_text()
                    if check_chars_exist(task_name):
                        if view not in unclick_btn:
                            unclick_btn.append(view)
                        continue
                    if task_name in have_clicked:
                        if have_clicked[task_name] >= 2:
                            continue
                    need_click_index = index
                    need_click_view = view
                    break
            if need_click_view:
                print("点击按钮", task_name)
                if have_clicked.get(task_name) is None:
                    have_clicked[task_name] = 1
                else:
                    have_clicked[task_name] += 1
                if check_chars_exist(task_name, other_app):
                    in_other_app = True
                need_click_view.click()
                time.sleep(3.5)
                task_loop(d, back_to_task, duration=18)
                finish_count = finish_count + 1
            else:
                error_count += 1
                print("未找到可点击按钮", error_count)
                if error_count >= 2:
                    break
        else:
            error_count += 1
            print("未找到可点击按钮", error_count)
            if error_count >= 2:
                break
    except Exception as e:
        print(e)
        continue
print(f"共自动化完成{finish_count}个任务")
d.click(screen_width // 2, 200)
time.sleep(2)
print("开始跳一跳")
while True:
    close_btn = d(className="android.widget.Button", text="关闭")
    if close_btn.exists:
        close_btn.click()
        time.sleep(2)
    jump_btn1 = d(className="android.widget.Button", textContains="跳一跳拿钱")
    if jump_btn1.exists:
        jump_text = jump_btn1.get_text()
        match = re.search(r".*剩余\s*(\d+)\s*体力", jump_text)
        if match:
            phy_num = int(match.group(1))
            if phy_num < 10:
                break
            print(f"当前剩余体力：{phy_num}")
            if phy_num < 50:
                jump_btn1.click()
            else:
                jump_btn1.long_click(duration=3)
            time.sleep(7)
    else:
        break
ctx.close()
d.shell("settings put system accelerometer_rotation 0")
print("关闭手机自动旋转")
time2 = time.time()
minutes, seconds = divmod(int(time2 - time1), 60)
print(f"共耗时: {minutes} 分钟 {seconds} 秒")
