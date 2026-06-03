import time

import uiautomator2 as u2

from utils import select_device, task_loop, start_app, TB_APP

unclick_btn = []
have_clicked = dict()
is_end = False
error_count = 0
in_other_app = False
time1 = time.time()
selected_device = select_device()
d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")
start_app(d, TB_APP, init=True)
screen_width, screen_height = d.window_size()
ctx = d.watch_context()
ctx.when("O1CN012qVB9n1tvZ8ATEQGu_!!6000000005964-2-tps-144-144").click()
ctx.when("O1CN01sORayC1hBVsDQRZoO_!!6000000004239-2-tps-426-128.png_").click()
ctx.when("O1CN010MeQt21rz75RjBubN_!!6000000005701-2-gg_dtc.png_q75.jpg_").click()
ctx.when("领取今日奖励").click()
ctx.when("确认").click()
ctx.when("确定").click()
ctx.when("刷新").click()
ctx.when("点击刷新").click()
ctx.when(xpath="//android.app.Dialog//android.widget.Button[contains(text(), '-tps-')]").click()
ctx.when(xpath="//android.app.Dialog//android.widget.Button[@text='关闭']").click()
ctx.when(xpath="//android.widget.FrameLayout[@resource-id='com.taobao.taobao:id/poplayer_native_state_center_layout_frame_id']//android.widget.ImageView[@content-desc='关闭按钮']").click()
ctx.start()
time.sleep(3)

def find_achievement_btn():
    while True:
        achievement_view = d(className="android.widget.TextView", text="淘宝成就")
        if achievement_view.exists:
            print("进入淘宝成就页面")
            break
        achievement_btn = d(classNameMatches=r"android.widget.FrameLayout|android.view.View", description="成就中心")
        if achievement_btn.exists:
            achievement_btn.click()
        time.sleep(5)


def back_to_achievement():
    while True:
        achievement_view = d(className="android.widget.TextView", text="淘宝成就")
        if achievement_view.exists:
            print("当前在淘宝成就页面，退出循环")
            break
        d.press("back")
        time.sleep(0.5)


find_achievement_btn()
while True:
    has_task = False
    sign_btn = d(className="android.widget.TextView", text="签到")
    if sign_btn.exists:
        print("点击签到")
        sign_btn.click()
        time.sleep(3)
        continue
    todo_btn = d.xpath('//android.widget.TextView[@text="去完成"]')
    if todo_btn.exists:
        for index in range(len(todo_btn.all())):
            title_view = d.xpath(f'(//android.widget.TextView[@text="去完成"])[{index+1}]/../preceding-sibling::android.widget.TextView[1]')
            if title_view.exists:
                title_text = title_view.get_text()
                if "抽赏一次" in title_text or "邀请好友" in title_text:
                    continue
                print(f"点击任务：{title_text}")
                d.click((todo_btn.all())[index].bounds[0] + 50, (todo_btn.all())[index].center()[1])
                # (todo_btn.all())[index].click()
                time.sleep(3)
                has_task = True
                task_loop(d, back_func=back_to_achievement, duration=18)
                break
    if not has_task:
        print("任务都做完了，退出循环")
        break
ctx.close()
d.shell("settings put system accelerometer_rotation 0")
print("关闭手机自动旋转")
