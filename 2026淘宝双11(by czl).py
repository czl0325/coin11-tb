import re
import time
from pydoc import describe

import uiautomator2 as u2
from utils import check_chars_exist, other_app, get_current_app, select_device, task_loop, check_verify, start_app, TB_APP, check_popup

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
ctx.start()
time.sleep(3)
has_clicked = dict()


def in_coin_home():
    return d(className="android.webkit.WebView", text="淘金币首页").exists


def in_task_home():
    return d(className="android.widget.TextView", text="做任务赚能量").exists


def find_coin_btn(rounds=10):
    while True:
        if in_coin_home():
            break
        coin_btn = d(className="android.widget.FrameLayout", description="领淘金币")
        if coin_btn.exists:
            coin_btn.click()
        time.sleep(3)


def to_task():
    while True:
        if in_task_home():
            break
        task_btn = d(className="android.widget.Button", text="赚能量")
        if task_btn.exists:
            task_btn.click()
        else:
            canvas_image = d.xpath('//android.webkit.WebView[@text="淘金币首页"]/android.view.View/android.view.View[1]/android.widget.Image')
            if canvas_image.exists:
                d.click(canvas_image.bounds[2] - 100, canvas_image.bounds[3] - 150)
        time.sleep(3)


def back_to_task():
    while True:
        if in_coin_home():
            break
        temp_package, temp_activity = get_current_app(d)
        if not temp_package or not temp_activity:
            time.sleep(0.5)
            continue
        if "Ext2ContainerActivity" in temp_activity:
            time.sleep(0.5)
            continue
        if TB_APP not in temp_package:
            print(f"回到原始APP,{TB_APP}")
            start_app(d, TB_APP)
            jump_btn = d(resourceId="com.taobao.taobao:id/tv_close", text="跳过")
            if jump_btn.exists:
                jump_btn.click()
                time.sleep(2)
            continue
        else:
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
            d.press('back')
        time.sleep(0.4)



find_coin_btn()
to_task()
finish_count = 0

while True:
    time.sleep(4)
    get_btn = d(className="android.widget.Button", textMatches=r".*立即领取，奖励\d+")
    if get_btn.exists:
        get_btn.click()
        continue
    has_task = False
    task_btn = d.xpath('//android.widget.Button[@text="去完成"]')
    if task_btn.exists:
        task_name = None
        click_index = 0
        do_time = 18
        for index in range(len(task_btn.all())):
            title_view = d.xpath(f'(//android.widget.Button[@text="去完成"])[{index+1}]/preceding-sibling::android.widget.TextView[1]')
            if title_view.exists:
                temp_name = title_view.text
                if has_clicked.get(temp_name, 0) > 2:
                    continue
                if check_chars_exist(temp_name):
                    continue
                click_index = index
                find_arr = re.findall(r"浏览(\d+)秒", temp_name)
                if len(find_arr) > 0:
                    do_time = int(find_arr[0]) + 3
                task_name = temp_name
                break
        if task_name:
            print(f"进行任务：{task_name}，需要浏览{do_time}秒。")
            has_clicked[task_name] = has_clicked[task_name] + 1 if has_clicked.get(task_name) else 1
            (task_btn.all())[click_index].click()
            time.sleep(5)
            has_task = True
            task_loop(d, back_to_task, duration=do_time)
            finish_count += 1
            continue
        if not has_task:
            break
print(f"共完成{finish_count}个任务")
d.click(screen_width // 2, 150)
time.sleep(3)
print("开始升级赛车")
while True:
    time.sleep(4)
    close_btn = d(className="android.widget.Button", text="关闭")
    if close_btn.exists:
        close_btn.click()
        time.sleep(2)
    choice_btn = d(className="android.widget.TextView", text="确认选择")
    if choice_btn.exists:
        choice_btn.click()
        continue
    racing_btn = d(className="android.widget.Button", textContains="升级赛车拿钱")
    if racing_btn.exists:
        if energy_list := re.findall(r"剩余\s*(\d+)\s*能量", racing_btn.get_text()):
            energy_text = int(energy_list[0])
            print(f"剩余{energy_text}能量")
            if energy_text < 100:
                break
            elif energy_text < 500:
                racing_btn.click()
            else:
                racing_btn.long_click(duration=5)

