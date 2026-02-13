import time
import re

import uiautomator2 as u2
from utils import select_device, start_app, TMALL_APP, get_current_app, task_loop

selected_device = select_device()
d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")
start_app(d, TMALL_APP, init=True)
ctx = d.watch_context()
ctx.when(xpath='//android.widget.FrameLayout[@resource-id="com.tmall.wireless:id/poplayer_native_state_center_layout_frame_id"]/android.widget.ImageView').click()
ctx.when("TB1XICqw4v1gK0jSZFFXXb0sXXa-105-105").click()
ctx.when("O1CN01hlloCi1c1pRpyL9bo_!!6000000003541-2-tps-132-132.png_q50.jpg_").click()


def check_in_task():
    package_name1, _ = get_current_app(d)
    if package_name1 != TMALL_APP:
        return False
    task_view = d(className="android.widget.TextView", textMatches=r"做任务.*?领现金值")
    if task_view.exists:
        return True
    return False


def back_to_task():
    while True:
        if check_in_task():
            break
        package_name1, _ = get_current_app(d)
        d.press("back")
        time.sleep(0.5)



shake_btn = d(className="android.widget.ImageView", description="必免卡")
if shake_btn.exists:
    shake_btn.click()
    print("点击摇钱树")
    time.sleep(3)
_, activity_name = get_current_app(d)
if activity_name == "com.tmall.wireless.themis.container.TMThemisActivity":
    withdrawal_btn1 = d(className="android.widget.TextView", text="立即提现")
    if withdrawal_btn1.exists:
        print("点击立即提现")
        withdrawal_btn1.click()
        time.sleep(3)
        withdrawal_btn2 = d.xpath('(//android.widget.TextView[@text="立即提现"])[2]')
        if withdrawal_btn2.exists:
            print("点击弹出框的提现")
            withdrawal_btn2.click()
            time.sleep(3)
    today_btn = d(className="android.widget.TextView", text="今日还可提")
    if today_btn.exists:
        today_btn.click()
        time.sleep(3)
    while True:
        time.sleep(5)
        has_task = False
        get_btn = d(className="android.widget.TextView", text="领取奖励")
        if get_btn.exists:
            print("点击领取奖励")
            get_btn.click()
            continue
        task_btn = d.xpath('//android.widget.TextView[@text="领取任务"]')
        if task_btn.exists:
            for index in range(len(task_btn.all())):
                title_view = d.xpath(f'(//android.widget.TextView[@text="领取任务"])[{index+1}]/../../android.widget.TextView[1]')
                subtitle_view = d.xpath(f'(//android.widget.TextView[@text="领取任务"])[{index+1}]/../../android.widget.TextView[2]')
                if title_view.exists:
                    title_text = title_view.get_text()
                    subtitle_text = subtitle_view.get_text()
                    if "添加桌面组件" in title_text:
                        continue
                    do_time = 30
                    if subtitle_text is str:
                        second = re.findall(r".*?(\d+)秒.*?", subtitle_text)
                        if len(second) > 0:
                            do_time = int(second[0])
                    (task_btn.all())[index].click()
                    print(f"点击任务：{title_text}")
                    time.sleep(5)
                    has_task = True
                    task_loop(d, back_to_task, duration=do_time)
                    break
        if not has_task:
            break
ctx.close()
d.shell("settings put system accelerometer_rotation 0")
print("关闭手机自动旋转")